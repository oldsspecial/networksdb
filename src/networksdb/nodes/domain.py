"""Generated node model for Domain."""
from typing import Any, List, Optional
from datetime import datetime, datetime

from typing import ClassVar
from pydantic import ConfigDict, Field, field_validator, model_validator, computed_field
from ziptie_schema.base.models import BaseNode
from ziptie_schema.base.mixins import IDGenerationMixin
from enum import Enum


# Transform imports
from ..transforms import validate_domain

# Label enricher for dynamic labels
from ..transforms import enrich_domain_labels

class Domain(BaseNode, IDGenerationMixin):
    """Domain node type.
"""

    # Configuration
    model_config = ConfigDict(
extra="forbid",  # Strict validation - no dynamic properties
validate_assignment=True
    )

    # Class attributes
    _primary_label = "Domain"
    schema_version: ClassVar[str] = "0.1"

    # Override base fields with defaults from schema
    primary_label: str = Field(
        default="Domain",
        description="Primary label for this node type"
    )
    # Dynamic additional labels (persisted to Neo4j)
    additional_labels: List[str] = Field(
        default_factory=list,
        description="Labels for this node (includes role and enriched labels)"
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
        description="Fully qualified domain name",
json_schema_extra={"identifying": True, "from_base_schema": False, "property_type": "string", "merge_strategy": "error_if_different", "validators": ['networksdb.transforms.validate_domain']}
    )



    # Field validators
    @field_validator("address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Validate address field."""
        # Skip validation for None values on optional fields
        if v is None:
            return v

        if not validate_domain(v):
            raise ValueError(f"Validation failed for networksdb.transforms.validate_domain: {v}")

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
            missing.append("  • address: Fully qualified domain name")

        if missing:
            example_fields = []
            example_fields.append("      address='<value>'")

            raise ValueError(
                f"\nDomain is missing required fields:\n" +
                "\n".join(missing) +
                "\n\nExample usage:\n  Domain(\n" +
                ",\n".join(example_fields) +
                "\n  )"
            )
        return values

    @model_validator(mode='after')
    def enrich_labels(self):
        """Apply label enricher to add computed labels."""
        # Get enriched labels based on current data (exclude additional_labels to avoid recursion)
        data_for_enricher = self.model_dump(exclude={'additional_labels'})
        enriched = enrich_domain_labels(data_for_enricher)

        # Add any new enriched labels
        if enriched:
            for label in enriched:
                if label not in self.additional_labels:
                    self.additional_labels.append(label)

        return self

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


        return relationships

    def merge(self, other: 'Domain') -> 'Domain':
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

        # Create new merged instance
        return self.__class__(**merged_data)


    # Role enum for type-safe label management
    class Role(Enum):
        """Available roles for Domain."""
        MAIL_SERVER = "mail_server"
        WEB_SERVER = "web_server"
        DNS_SERVER = "dns_server"
        EMAIL_DOMAIN = "email_domain"

    # Role to label mapping
    _role_labels = {
        "mail_server": "MailServer",
        "web_server": "WebServer",
        "dns_server": "DNSServer",
        "email_domain": "EmailDomain",
    }

    # Role management methods
    def add_role(self, role: Role) -> None:
        """Add a role's label to this node."""
        label = self._role_labels.get(role.value)
        if label and label not in self.additional_labels:
            self.additional_labels.append(label)

    def remove_role(self, role: Role) -> None:
        """Remove a role's label from this node."""
        label = self._role_labels.get(role.value)
        if label and label in self.additional_labels:
            self.additional_labels.remove(label)

    def has_role(self, role: Role) -> bool:
        """Check if this node has a specific role."""
        label = self._role_labels.get(role.value)
        return label in self.additional_labels if label else False


# Set json_schema_extra for embedded node properties after class definition