"""Generated node model for Email."""
from typing import Any, List, Optional
from datetime import datetime, datetime
from ..nodes.email_address import EmailAddress

from typing import ClassVar
from pydantic import ConfigDict, Field, field_validator, model_validator, computed_field
from ziptie_schema.base.models import BaseNode
from ziptie_schema.base.mixins import IDGenerationMixin



class Email(BaseNode, IDGenerationMixin):
    """Email node type.
"""

    # Configuration
    model_config = ConfigDict(
extra="forbid",  # Strict validation - no dynamic properties
validate_assignment=True
    )

    # Class attributes
    _primary_label = "Email"
    schema_version: ClassVar[str] = "0.1"

    # Override base fields with defaults from schema
    primary_label: str = Field(
        default="Email",
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

    from_rel: EmailAddress = Field(
        ...,
        description="from_rel",
json_schema_extra={"identifying": True, "from_base_schema": False, "property_type": "node", "merge_strategy": "error_if_different", "embedded_config": {"node_class": "EmailAddress", "relationship": "FromRelationship", "direction": "IN"}}
    )

    to: List[EmailAddress] = Field(
        default_factory=list,
        description="to",
json_schema_extra={"identifying": True, "from_base_schema": False, "property_type": "node_list", "merge_strategy": "error_if_different", "embedded_config": {"node_class": "EmailAddress", "relationship": "To", "direction": "OUT"}}
    )


    # Validators for embedded node properties
    @field_validator('from_rel', 'to')
    @classmethod
    def _validate_embedded_nodes(cls, v, info):
        """Ensure embedded nodes have node_id computed."""
        if v is None:
            return v

        field_name = info.field_name
        field_info = cls.model_fields[field_name]
        prop_type = field_info.json_schema_extra.get('property_type')

        if prop_type == 'node':
            # Single node - ensure it has node_id
            if hasattr(v, 'compute_node_id') and not hasattr(v, 'node_id'):
                v.node_id = v.compute_node_id()
        elif prop_type == 'node_list':
            # List of nodes - ensure all have node_id
            for node in v:
                if hasattr(node, 'compute_node_id') and not hasattr(node, 'node_id'):
                    node.node_id = node.compute_node_id()
        return v
    @model_validator(mode='before')
    @classmethod
    def provide_helpful_errors(cls, values: Any) -> Any:
        """Provide helpful error messages for missing required fields."""
        if not isinstance(values, dict):
            return values

        # Check for missing required fields
        missing = []
        if 'from_rel' not in values or values['from_rel'] is None:
            missing.append("  • from_rel: from_rel")
        if 'to' not in values or values['to'] is None:
            missing.append("  • to: to")

        if missing:
            example_fields = []
            example_fields.append("      from_rel='<value>'")
            example_fields.append("      to='<value>'")

            raise ValueError(
                f"\nEmail is missing required fields:\n" +
                "\n".join(missing) +
                "\n\nExample usage:\n  Email(\n" +
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
        separate_dynamic_properties: bool = False,
        serialize_containers: bool = False
    ) -> dict[str, Any]:
        """Convert node to structured dictionary representation.

        Note: Embedded node properties are excluded from serialization.

        Args:
            separate_dynamic_properties: If True, dynamic properties are returned in a
                                       separate 'dynamic_properties' field. If False
                                       (default), they are merged into the 'properties' field.
            serialize_containers: If True, serialize property containers (identifying_properties,
                                properties, dynamic_properties) to JSON strings. If False (default),
                                return them as dicts.

        Returns:
            Dictionary with:
            - Base schema properties as direct keys
            - 'node_id': Computed unique identifier
- 'schema_version': Schema version string (e.g., "1.0")
- 'identifying_properties': Dict of identifying properties (or JSON string if serialize_containers=True)
            - 'properties': Dict of regular properties (non-identifying, non-base) (or JSON string if serialize_containers=True)
            - 'primary_label': Primary label string
            - 'labels': List of ALL labels (primary_label + additional_labels)
            - 'dynamic_properties': Dict of dynamic properties (only if separate_dynamic_properties=True and node allows dynamic properties) (or JSON string if serialize_containers=True)
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

        # Node does not allow dynamic properties, but canonical format requires empty dict
        if separate_dynamic_properties:
            result['dynamic_properties'] = {}

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
            if 'dynamic_properties' in result:
                result['dynamic_properties'] = json.dumps(result['dynamic_properties'])

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

        if self.from_rel:
            # Get relationship class from registry
            RelClass = registry.get_relationship_class("FromRelationship")

            # Single embedded node
            rel = RelClass(start_node=self.from_rel, end_node=self)
            relationships.append(rel)

        if self.to:
            # Get relationship class from registry
            RelClass = registry.get_relationship_class("To")

            # List of embedded nodes
            for node in self.to:
                rel = RelClass(start_node=self, end_node=node)
                relationships.append(rel)

        return relationships

    def merge(self, other: 'Email') -> 'Email':
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



        # Create new merged instance
        return self.__class__(**merged_data)



# Set json_schema_extra for embedded node properties after class definition# Configure metadata for embedded node fields (used for ID generation and relationships)
Email.model_fields['from_rel'].json_schema_extra = {
    'identifying': True,
    'property_type': 'node',}
Email.model_fields['to'].json_schema_extra = {
    'identifying': True,
    'property_type': 'node_list',}
