"""Generated node model for IPAddress."""
from typing import Any, List, Optional
from datetime import datetime, datetime

from typing import ClassVar
from pydantic import ConfigDict, Field, field_validator, model_validator, computed_field
from ziptie_schema.base.models import BaseNode
from ziptie_schema.base.mixins import IDGenerationMixin
from ziptie_schema.classification import ClassificationError


# Transform imports
from networksdb.transforms.transforms import classify_ip, normalize_ip

# Classifier function for runtime type determination
from networksdb.transforms.transforms import classify_ip

class IPAddress(BaseNode, IDGenerationMixin):
    """IPAddress node type.
"""
    # Flag for runtime classification
    __classifiable__ = True

    # Configuration
    model_config = ConfigDict(
extra="allow",  # Allow dynamic properties
validate_assignment=True
    )

    # Class attributes
    _primary_label = "IPAddress"
    schema_version: ClassVar[str] = "0.1"

    # Override base fields with defaults from schema
    primary_label: str = Field(
        default="IPAddress",
        description="Primary label for this node type"
    )
    # Static additional labels from schema
    additional_labels: List[str] = Field(
        default_factory=lambda: [],
        description="Additional labels from inheritance chain"
    )

    # Properties
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(),
        description="When this entity was created",
json_schema_extra={"identifying": False, "from_base_schema": True, "property_type": "datetime", "merge_strategy": "min"}
    )

    modified_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(),
        description="When this entity was last modified",
json_schema_extra={"identifying": False, "from_base_schema": True, "property_type": "datetime", "merge_strategy": "max"}
    )

    count: Optional[int] = Field(
        default=1,
        description="count",
json_schema_extra={"identifying": False, "from_base_schema": True, "property_type": "int", "merge_strategy": "sum"}
    )

    sources: Optional[List[Any]] = Field(
        default_factory=lambda: [],
        description="sources",
json_schema_extra={"identifying": False, "from_base_schema": True, "property_type": "list", "merge_strategy": "union"}
    )

    address: str = Field(
        ...,
        description="The IP address in standard notation",
json_schema_extra={"identifying": True, "from_base_schema": False, "property_type": "string", "merge_strategy": "error_if_different", "normalizers": ['networksdb.transforms.transforms.normalize_ip'], "index": {"type": "key", "tokenizer": "default"}}
    )

# Classification configuration
    _classifiable = True
    _classifier_function = "networksdb.transforms.transforms.classify_ip"

    def __new__(cls, **kwargs):
        """Handle runtime classification for base class instantiation.

        When instantiating the base class directly, this method uses the
        configured classifier function to determine the appropriate subclass
        based on the provided data.
        """
        # Only classify when instantiating the base class directly
        if cls.__name__ == "IPAddress" and hasattr(cls, '_classifiable') and cls._classifiable:
            # Pre-normalize data before classification
            # Normalizers are idempotent, so running them here and again during
            # Pydantic validation is safe. This ensures the classifier receives clean data.
            normalized_data = {}
            for key, value in kwargs.items():
                normalized_data[key] = value

            # Apply property normalizers
            if "address" in normalized_data and normalized_data["address"] is not None:
                try:
                    normalized_data["address"] = normalize_ip(normalized_data["address"])
                except Exception as e:
                    raise ValueError(
                        f"Failed to normalize 'address' for classification: {str(e)}"
                    ) from e

            # Get the subclass name from the classifier (with normalized data)
            subclass_name = classify_ip(normalized_data)

            if subclass_name is None:
                raise ClassificationError(
                    f"Could not classify IPAddress with provided data. "
                    f"Classifier function 'networksdb.transforms.transforms.classify_ip' returned None. "
                    f"Data keys: {list(kwargs.keys())}"
                )

            if subclass_name != cls.__name__:
                # Look up the subclass in the parent package (where all node classes are imported)
                import sys
                parent_package_name = cls.__module__.rsplit('.', 1)[0]  # e.g., 'models.nodes'
                parent_package = sys.modules[parent_package_name]
                subclass = getattr(parent_package, subclass_name, None)

                if subclass is None:
                    # List available classes for better error message
                    available = [name for name in dir(parent_package)
                                if not name.startswith('_') and name != cls.__name__]
                    raise ClassificationError(
                        f"Classifier function 'networksdb.transforms.transforms.classify_ip' returned "
                        f"unknown subclass name: '{subclass_name}'. "
                        f"Available classes in parent package: {available}"
                    )

                # Verify it's actually a subclass
                if not issubclass(subclass, cls):
                    raise ClassificationError(
                        f"Class '{subclass_name}' is not a subclass of IPAddress"
                    )

                # Create instance of the subclass
                return subclass(**kwargs)

        # Normal instantiation
        return super().__new__(cls)

    @classmethod
    def model_validate(
        cls,
        obj: Any,
        *,
        strict: bool | None = None,
        from_attributes: bool | None = None,
        context: dict | None = None,
    ) -> "IPAddress":
        """Override model_validate to handle classification before validation.

        This ensures that classifiable nodes work with both direct instantiation
        and model_validate by running classification before Pydantic validation.
        """
        # Only classify when called on the base class directly
        if cls.__name__ == "IPAddress" and hasattr(cls, '_classifiable') and cls._classifiable:
            # Convert obj to dict if needed
            data = obj if isinstance(obj, dict) else dict(obj)

            # Pre-normalize data before classification
            # Normalizers are idempotent, so running them here and again during
            # Pydantic validation is safe. This ensures the classifier receives clean data.
            normalized_data = {}
            for key, value in data.items():
                normalized_data[key] = value

            # Apply property normalizers
            if "address" in normalized_data and normalized_data["address"] is not None:
                try:
                    normalized_data["address"] = normalize_ip(normalized_data["address"])
                except Exception as e:
                    raise ValueError(
                        f"Failed to normalize 'address' for classification: {str(e)}"
                    ) from e

            # Get the subclass name from the classifier (with normalized data)
            subclass_name = classify_ip(normalized_data)

            if subclass_name is None:
                raise ClassificationError(
                    f"Could not classify IPAddress with provided data. "
                    f"Classifier function 'networksdb.transforms.transforms.classify_ip' returned None. "
                    f"Data keys: {list(obj.keys()) if hasattr(obj, 'keys') else 'N/A'}"
                )

            if subclass_name != cls.__name__:
                # Look up the subclass in the parent package
                import sys
                parent_package_name = cls.__module__.rsplit('.', 1)[0]
                parent_package = sys.modules[parent_package_name]
                subclass = getattr(parent_package, subclass_name, None)

                if subclass is None:
                    available = [name for name in dir(parent_package)
                                if not name.startswith('_') and name != cls.__name__]
                    raise ClassificationError(
                        f"Classifier function 'networksdb.transforms.transforms.classify_ip' returned "
                        f"unknown subclass name: '{subclass_name}'. "
                        f"Available classes in parent package: {available}"
                    )

                # Verify it's actually a subclass
                if not issubclass(subclass, cls):
                    raise ClassificationError(
                        f"Class '{subclass_name}' is not a subclass of IPAddress"
                    )

                # Validate with the subclass
                return subclass.model_validate(
                    obj,
                    strict=strict,
                    from_attributes=from_attributes,
                    context=context
                )

        # Normal validation for non-classifiable or when called on subclass
        return super().model_validate(
            obj,
            strict=strict,
            from_attributes=from_attributes,
            context=context
        )


    # Field normalizers
    @field_validator("address", mode='before')
    @classmethod
    def normalize_address(cls, v: Any) -> Any:
        """Apply normalizers to address field."""
        if v is None:
            return v
        
        try:            v = normalize_ip(v)
        except Exception as e:
            field_desc = "The IP address in standard notation"
            raise ValueError(
                f"Failed to process 'address' ({field_desc}): {str(e)}"
            ) from e
        return v
    @model_validator(mode='before')
    @classmethod
    def provide_helpful_errors(cls, values: Any) -> Any:
        """Provide helpful error messages for missing required fields."""
        if not isinstance(values, dict):
            return values

        # Check for missing required fields
        missing = []
        if 'address' not in values or values['address'] is None:
            missing.append("  • address: The IP address in standard notation")

        if missing:
            example_fields = []
            example_fields.append("      address='<value>'")

            raise ValueError(
                f"\nIPAddress is missing required fields:\n" +
                "\n".join(missing) +
                "\n\nExample usage:\n  IPAddress(\n" +
                ",\n".join(example_fields) +
                "\n  )"
            )
        return values

    @property
    def node_id(self) -> str:
        """Compute the unique node ID."""
        return self.compute_node_id()

    def _serialize_value(self, value):
        """Convert datetime objects to ISO format strings for JSON serialization."""
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    def to_dict(
        self,
        serialize_containers: bool = False
    ) -> dict[str, Any]:
        """Convert node to structured dictionary representation.

        Note: Embedded node properties are excluded from serialization.

        Args:
            serialize_containers: If True, serialize property containers (identifying_properties,
                                properties) to JSON strings. If False (default),
                                return them as dicts.

        Returns:
            Dictionary with:
            - Base schema properties as direct keys
            - 'node_id': Computed unique identifier
- 'schema_version': Schema version string (e.g., "1.0")
- 'identifying_properties': Dict of identifying properties (or JSON string if serialize_containers=True)
            - 'properties': Dict of all properties including dynamic properties (or JSON string if serialize_containers=True)
            - 'primary_label': Primary label string
            - 'labels': List of ALL labels (primary_label + additional_labels)
        """
        result = {}

        # Use Pydantic's model_fields to iterate through all fields
        identifying_props = {}
        regular_props = {}

        for field_name, field_info in self.__class__.model_fields.items():
            # Skip computed fields and base class fields
            if field_name in ('node_id', 'labels', 'primary_label', 'additional_labels'):
                continue

            metadata = field_info.json_schema_extra or {}

            # Skip embedded node properties - they're for relationships, not serialization
            if metadata.get('property_type') in ['node', 'node_list']:
                continue

            # Skip excluded fields (those with exclude=True in Field definition)
            if field_info.exclude:
                continue

            value = self._serialize_value(getattr(self, field_name))

            # Check if this is an identifying property
            if metadata.get('identifying', False):
                identifying_props[field_name] = value
            # Otherwise it's a regular property
            else:
                regular_props[field_name] = value

        # Merge dynamic properties into regular properties (always merged in canonical format)
        dynamic_props = getattr(self, '__pydantic_extra__', {})
        serialized_dynamic_props = {k: self._serialize_value(v) for k, v in dynamic_props.items() if v is not None}
        # Always merge into regular properties
        regular_props.update(serialized_dynamic_props)

        # Add structured data
        result['node_id'] = self.node_id
        result['schema_version'] = self.__class__.schema_version
        result['identifying_properties'] = identifying_props
        result['properties'] = regular_props
        result['primary_label'] = self.primary_label
        result['labels'] = self.labels  # Use the labels property which includes primary_label + additional_labels

        # Optionally serialize containers to JSON strings
        if serialize_containers:
            import json
            result['identifying_properties'] = json.dumps(result['identifying_properties'])
            result['properties'] = json.dumps(result['properties'])

        return result

    def create_relationships(self, registry=None) -> list:
        """Create relationship instances from embedded nodes.

        Args:
            registry: Optional registry. If None, uses package's default registry.

        Returns:
            List of relationship instances

        Raises:
            KeyError: If relationship type not found in registry
            ValidationError: If nodes don't match relationship requirements (from Pydantic)
        """
        if registry is None:
            from ..registry import registry as default_registry
            registry = default_registry

        relationships = []


        return relationships

    def merge(self, other: 'IPAddress') -> 'IPAddress':
        """Merge another node into this one using configured merge strategies.

        Args:
            other: Another node of the same type to merge with this one

        Returns:
            A new merged node instance with combined data

        Raises:
            ValueError: If nodes have different primary labels or merge conflicts
        """
        from ..base.merge import MERGE_STRATEGIES

        # Verify same primary label
        if self.primary_label != other.primary_label:
            raise ValueError(
                f"Cannot merge nodes with different primary labels: "
                f"{self.primary_label} != {other.primary_label}"
            )

        # Merge additional labels (union)
        merged_labels = list(set(self.additional_labels + other.additional_labels))

        # Merge properties
        merged_data = {
            'primary_label': self.primary_label,
            'additional_labels': merged_labels
        }

        # Merge created_at (strategy: min)
        self_created_at = getattr(self, 'created_at', None)
        other_created_at = getattr(other, 'created_at', None)

        if self_created_at is None and other_created_at is None:
            merged_data['created_at'] = None
        elif self_created_at is None:
            merged_data['created_at'] = other_created_at
        elif other_created_at is None:
            merged_data['created_at'] = self_created_at
        else:
            # Both have values, use merge strategy
            strategy = MERGE_STRATEGIES['min']
            merged_data['created_at'] = strategy(
                self_created_at,
                other_created_at,
                'created_at'
            )
        # Merge modified_at (strategy: max)
        self_modified_at = getattr(self, 'modified_at', None)
        other_modified_at = getattr(other, 'modified_at', None)

        if self_modified_at is None and other_modified_at is None:
            merged_data['modified_at'] = None
        elif self_modified_at is None:
            merged_data['modified_at'] = other_modified_at
        elif other_modified_at is None:
            merged_data['modified_at'] = self_modified_at
        else:
            # Both have values, use merge strategy
            strategy = MERGE_STRATEGIES['max']
            merged_data['modified_at'] = strategy(
                self_modified_at,
                other_modified_at,
                'modified_at'
            )
        # Merge count (strategy: sum)
        self_count = getattr(self, 'count', None)
        other_count = getattr(other, 'count', None)

        if self_count is None and other_count is None:
            merged_data['count'] = None
        elif self_count is None:
            merged_data['count'] = other_count
        elif other_count is None:
            merged_data['count'] = self_count
        else:
            # Both have values, use merge strategy
            strategy = MERGE_STRATEGIES['sum']
            merged_data['count'] = strategy(
                self_count,
                other_count,
                'count'
            )
        # Merge sources (strategy: union)
        self_sources = getattr(self, 'sources', None)
        other_sources = getattr(other, 'sources', None)

        if self_sources is None and other_sources is None:
            merged_data['sources'] = None
        elif self_sources is None:
            merged_data['sources'] = other_sources
        elif other_sources is None:
            merged_data['sources'] = self_sources
        else:
            # Both have values, use merge strategy
            strategy = MERGE_STRATEGIES['union']
            merged_data['sources'] = strategy(
                self_sources,
                other_sources,
                'sources'
            )
        # Merge address (strategy: error_if_different)
        self_address = getattr(self, 'address', None)
        other_address = getattr(other, 'address', None)

        if self_address is None and other_address is None:
            merged_data['address'] = None
        elif self_address is None:
            merged_data['address'] = other_address
        elif other_address is None:
            merged_data['address'] = self_address
        else:
            # Both have values, use merge strategy
            strategy = MERGE_STRATEGIES['error_if_different']
            merged_data['address'] = strategy(
                self_address,
                other_address,
                'address'
            )
        # Merge dynamic properties from __pydantic_extra__
        self_extra = getattr(self, '__pydantic_extra__', {})
        other_extra = getattr(other, '__pydantic_extra__', {})

        # Get all unique dynamic property keys
        all_extra_keys = set(self_extra.keys()) | set(other_extra.keys())

        # Merge each dynamic property using take_any_non_empty strategy
        for extra_key in all_extra_keys:
            self_value = self_extra.get(extra_key)
            other_value = other_extra.get(extra_key)

            # Apply take_any_non_empty strategy from base.merge
            merged_value = MERGE_STRATEGIES['take_any_non_empty'](
                self_value, other_value, extra_key
            )
            if merged_value is not None:
                merged_data[extra_key] = merged_value

        # Create new merged instance
        return self.__class__(**merged_data)



# Set json_schema_extra for embedded node properties after class definition