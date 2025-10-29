# API Specification: Schema Metadata Helper for Ziptie-Parsing


## Requirements

We need a metadata helper API that provides the **same schema information** that entity classes have, but accessible without instantiating entities.

### Essential Operations

1. **Load metadata registry** for a schema package by name
2. **Get metadata** for a specific entity type (e.g., `"PublicIPAddress"`)
3. **Iterate schema-defined properties** to build aggregation expressions with merge strategies
4. **Classify field names** into struct buckets to reconstruct canonical format

### Use Cases

#### Use Case 1: Property Expansion

When expanding properties from structs for deduplication:

```python
# Need to iterate all schema properties
for prop_name, prop_info in entity_meta.properties.items():
    if prop_info.is_identifying():
        # Expand from identifying_properties struct
        expr = pl.col("identifying_properties").struct.field(prop_name)
```

#### Use Case 2: Merge Strategy Application

When building aggregation expressions:

```python
# Need merge strategy for each property
for prop_name, prop_info in entity_meta.properties.items():
    strategy = prop_info.merge_strategy
    if strategy == "sum":
        expr = pl.col(prop_name).sum()
    elif strategy == "error_if_different":
        expr = pl.col(prop_name).first()  # + validation
```

#### Use Case 3: Struct Reconstruction (THE CRITICAL FIX)

After deduplication, classify DataFrame columns into struct buckets:

```python
# DataFrame has columns: ["node_id", "address", "context", "count", "custom_field"]
# For PublicIPAddress:
classification = entity_meta.classify_fields([
    "address", "context", "count", "custom_field"
])

# Expected result:
# {
#   "identifying_properties": ["address"],  # Only schema-defined identifying
#   "properties": ["count"],                # Only schema-defined regular
#   "dynamic_properties": ["context", "custom_field"]  # NOT in PublicIPAddress schema
# }

# For PrivateIPAddress, same fields would classify as:
# {
#   "identifying_properties": ["address", "context"],  # Both in schema
#   "properties": ["count"],
#   "dynamic_properties": ["custom_field"]
# }
```

This allows polars_dedup to reconstruct structs that match what `entity.to_dict()` produces, filtering out diagonal concat pollution.

## Requested API

### Top-Level Function

```python
def load_metadata_from_package(package_name: str) -> MetadataRegistry:
    """Load metadata registry for a schema package.

    Args:
        package_name: Name of schema package (e.g., "networksdb")

    Returns:
        MetadataRegistry instance for accessing entity metadata

    Raises:
        ImportError: If package not found or has no metadata
    """
```

### MetadataRegistry Class

```python
class MetadataRegistry:
    """Registry of entity metadata for a schema package."""

    def get_entity(self, entity_type_name: str) -> EntityMetadata:
        """Get metadata for a specific entity type.

        Args:
            entity_type_name: Concrete entity type name (e.g., "PublicIPAddress")

        Returns:
            EntityMetadata for that type

        Raises:
            KeyError: If entity type not found

        Example:
            >>> registry = load_metadata_from_package("networksdb")
            >>> pub_ip_meta = registry.get_entity("PublicIPAddress")
            >>> priv_ip_meta = registry.get_entity("PrivateIPAddress")
        """
```

### EntityMetadata Class

```python
class EntityMetadata:
    """Metadata for a single entity type."""

    @property
    def properties(self) -> dict[str, PropertyMetadata]:
        """Get all schema-defined properties (identifying + regular).

        Returns:
            Dict mapping property name to PropertyMetadata

        Example:
            >>> for prop_name, prop_info in entity_meta.properties.items():
            ...     print(f"{prop_name}: identifying={prop_info.is_identifying()}")
        """

    def classify_fields(self, field_names: list[str]) -> dict[str, list[str]]:
        """Classify field names into their struct buckets.

        This is the CRITICAL method for fixing the bug. It determines which
        fields belong in which struct based on the schema definition.

        Args:
            field_names: List of field names from DataFrame or entity dict

        Returns:
            Dictionary with three keys:
            - "identifying_properties": Schema-defined identifying fields
            - "properties": Schema-defined regular fields
            - "dynamic_properties": Fields NOT in schema (dynamic)

        Example:
            >>> # For PublicIPAddress
            >>> entity_meta.classify_fields(["address", "context", "count"])
            {
                "identifying_properties": ["address"],
                "properties": ["count"],
                "dynamic_properties": ["context"]
            }

            >>> # For PrivateIPAddress (same fields classify differently!)
            >>> entity_meta.classify_fields(["address", "context", "count"])
            {
                "identifying_properties": ["address", "context"],
                "properties": ["count"],
                "dynamic_properties": []
            }
        """
```

### PropertyMetadata Class

```python
class PropertyMetadata:
    """Metadata for a single property."""

    def is_identifying(self) -> bool:
        """Check if this property goes in identifying_properties struct.

        Returns:
            True if identifying, False if regular property
        """

    @property
    def merge_strategy(self) -> str:
        """Get merge strategy for deduplication.

        Returns:
            Strategy name: "error_if_different", "take_first", "take_last",
            "take_any_non_null", "min", "max", "sum", "union"

        Note:
            Should default to "take_first" if not specified in schema
        """
```

## Expected Behavior

### Scenario: PublicIPAddress vs PrivateIPAddress

**Schema definitions:**
- `PublicIPAddress`: identifying properties = `["address"]`
- `PrivateIPAddress`: identifying properties = `["address", "context"]`

**Input DataFrame** (after diagonal concat of both types):
```
┌──────────────────┬─────────┬─────────┬───────┐
│ primary_label    │ address │ context │ count │
├──────────────────┼─────────┼─────────┼───────┤
│ PublicIPAddress  │ 1.2.3.4 │ null    │ 1     │
│ PrivateIPAddress │ 10.0.0.1│ prod    │ 5     │
└──────────────────┴─────────┴─────────┴───────┘
```

**Expected classification:**

For `PublicIPAddress` partition:
```python
classify_fields(["address", "context", "count"])
→ {
    "identifying_properties": ["address"],  # Only address in schema
    "properties": ["count"],
    "dynamic_properties": ["context"]  # NOT in PublicIPAddress schema
}
```

For `PrivateIPAddress` partition:
```python
classify_fields(["address", "context", "count"])
→ {
    "identifying_properties": ["address", "context"],  # Both in schema
    "properties": ["count"],
    "dynamic_properties": []
}
```

**Expected output:**
```json
// PublicIPAddress entity
{
  "identifying_properties": {"address": "1.2.3.4"},
  "properties": {"count": 1},
  "dynamic_properties": {"context": null}
}

// PrivateIPAddress entity
{
  "identifying_properties": {"address": "10.0.0.1", "context": "prod"},
  "properties": {"count": 5},
  "dynamic_properties": {}
}
```

## Integration Point

The API will be used by `ziptie-parsing/src/ziptie_parsing/sql/metadata.py`:

```python
from ziptie_schema_helper import load_metadata_from_package

# In ziptie-parsing code
metadata_registry = load_metadata_from_package("networksdb")
entity_meta = metadata_registry.get_entity("PublicIPAddress")

# Struct reconstruction in polars_dedup
classification = entity_meta.classify_fields(dataframe_columns)
df = df.with_columns([
    pl.struct(classification["identifying_properties"]).alias("identifying_properties"),
    pl.struct(classification["properties"]).alias("properties"),
    pl.struct(classification["dynamic_properties"]).alias("dynamic_properties")
])
```

## Success Criteria

1. ✅ `polars_dedup` produces **identical output** to `memory_dedup` (same entity.to_dict() format)
2. ✅ No `context` pollution in `PublicIPAddress` identifying_properties
3. ✅ Different entity types correctly classify the same field names differently
4. ✅ API works without entity instantiation (performance requirement)
5. ✅ Clear separation: schema-defined properties vs dynamic properties

## Notes

- The implementation can live in `ziptie-schema` as a helper module
- No specific implementation details required - focus on correct behavior
- Must work across all schema packages (networksdb, ziptie_schema_example, etc.)
- Should be importable by ziptie-parsing stages
