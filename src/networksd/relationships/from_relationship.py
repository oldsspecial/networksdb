"""Generated relationship model for FROM."""
from typing import Any, ClassVar, List, Optional
from datetime import datetime, datetime
from pydantic import ConfigDict, Field, field_validator, model_validator
from ziptie_schema.base.models import BaseRelationship
from ziptie_schema.base.mixins import IDGenerationMixin

# Import node types for type checking
from ..nodes.email_address import EmailAddress
from ..nodes.email import Email


class FromRelationship(BaseRelationship, IDGenerationMixin):
    """FROM relationship type.
    
    Valid node pairs:    - EmailAddress -> Email    """
    
    # Class attributes
    _rel_type: ClassVar[str] = "FROM"
    schema_version: ClassVar[str] = "0.1"
    _valid_pairs: ClassVar[list[tuple[str, str]]] = [        ("EmailAddress", "Email"),    ]
    _bidirectional: ClassVar[bool] = False
    
    # Override base field with default from schema
    rel_type: str = Field(
        default="FROM",
        description="Type of this relationship"
    )
    
    # Properties
    created_at: Optional[datetime] = Field(        default_factory=lambda: datetime.now(),        description="When this entity was created",        json_schema_extra={
            "identifying": False,
            "from_base_schema": True,
            "merge_strategy": "min"        }
    )
    modified_at: Optional[datetime] = Field(        default_factory=lambda: datetime.now(),        description="When this entity was last modified",        json_schema_extra={
            "identifying": False,
            "from_base_schema": True,
            "merge_strategy": "max"        }
    )
    count: Optional[int] = Field(        default=1,        description="count",        json_schema_extra={
            "identifying": False,
            "from_base_schema": True,
            "merge_strategy": "sum"        }
    )
    sources: Optional[List[Any]] = Field(        default_factory=lambda: [],        description="sources",        json_schema_extra={
            "identifying": False,
            "from_base_schema": True,
            "merge_strategy": "union"        }
    )

    @model_validator(mode='before')
    @classmethod
    def provide_helpful_errors(cls, values: Any) -> Any:
        """Provide helpful error messages for missing required fields."""
        if not isinstance(values, dict):
            return values
        
        # Check for missing required fields
        missing = []
        
        # Check for required relationship fields (start_node and end_node)
        if 'start_node' not in values or values['start_node'] is None:
            missing.append("  • start_node: The source node of this relationship")
        if 'end_node' not in values or values['end_node'] is None:
            missing.append("  • end_node: The target node of this relationship")
        
        
        if missing:
            example_fields = []
            example_fields.append("      start_node=<source_node_instance>")
            example_fields.append("      end_node=<target_node_instance>")
            
            valid_pairs_str = ", ".join([f"{start}->{end}" for start, end in cls._valid_pairs])
            
            raise ValueError(
                f"\nFromRelationship is missing required fields:\n" + 
                "\n".join(missing) +
                f"\n\nValid node pairs: {valid_pairs_str}" +
                "\n\nExample usage:\n  FromRelationship(\n" +
                ",\n".join(example_fields) +
                "\n  )"
            )
        return values
    
    @model_validator(mode='after')
    def validate_node_types(self):
        """Validate that start and end nodes match schema definition.
        
        This validator is inheritance-aware: if a relationship is defined
        between parent types, it will accept any subclass of those types.
        For example, if the relationship is IPAddress -> IPAddress, it will
        accept PrivateIPAddress -> PublicIPAddress since both are subclasses
        of IPAddress.
        """
        # Get all labels from the nodes (primary + inherited)
        start_labels = self.start_node.labels if hasattr(self.start_node, 'labels') else [self.start_node.primary_label]
        end_labels = self.end_node.labels if hasattr(self.end_node, 'labels') else [self.end_node.primary_label]
        
        # Check if this pair is valid (checking against all labels for inheritance)
        valid = False
        for valid_start, valid_end in self._valid_pairs:
            # Check if any of the start node's labels match the required start type
            # AND any of the end node's labels match the required end type
            if valid_start in start_labels and valid_end in end_labels:
                valid = True
                break
            # For bidirectional relationships, also check the reverse
            if self._bidirectional and valid_end in start_labels and valid_start in end_labels:
                valid = True
                break
        
        if not valid:
            # Provide helpful error showing what was given vs what's expected
            start_primary = self.start_node.primary_label
            end_primary = self.end_node.primary_label
            raise ValueError(
                f"Invalid node pair: {start_primary} -> {end_primary}. "
                f"Valid pairs (including inherited types): {self._valid_pairs}. "
                f"Start node labels: {start_labels}, End node labels: {end_labels}"
            )
        
        return self
    
    @property
    def rel_id(self) -> str:
        """Compute the unique relationship ID."""
        return self.compute_rel_id()
    
    def _serialize_value(self, value):
        """Convert datetime objects to ISO format strings for JSON serialization."""
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    def to_dict(self, separate_dynamic_properties: bool = False) -> dict[str, Any]:
        """Convert relationship to structured dictionary representation.

        Args:
            separate_dynamic_properties: If True, dynamic properties are returned in a
                                       separate 'dynamic_properties' field. If False
                                       (default), they are merged into the 'properties' field.

        Returns:
            Dictionary with:
            - Base schema properties as direct keys
            - 'rel_id': Computed unique identifier (relationship ID)
- 'schema_version': Schema version string (e.g., "1.0")
- 'identifying_properties': Dict of identifying properties
            - 'properties': Dict of regular properties
            - 'rel_type': Relationship type string
            - 'start_node': Dict with minimal node info (primary_label, node_id)
            - 'end_node': Dict with minimal node info (primary_label, node_id)
            - 'dynamic_properties': Dict of dynamic properties (only if separate_dynamic_properties=True and relationship allows dynamic properties)
        """
        result = {}

        identifying_props = {}
        regular_props = {}

        for field_name, field_info in self.__class__.model_fields.items():
            # Skip computed and base fields
            if field_name in ('rel_id', 'rel_type', 'start_node', 'end_node'):
                continue

            # Skip excluded fields (those with exclude=True in Field definition)
            if field_info.exclude:
                continue

            value = self._serialize_value(getattr(self, field_name))
            metadata = field_info.json_schema_extra or {}

            if metadata.get('identifying', False):
                identifying_props[field_name] = value
            else:
                regular_props[field_name] = value
        
        # Relationship does not allow dynamic properties, but canonical format requires empty dict
        if separate_dynamic_properties:
            result['dynamic_properties'] = {}

        result['rel_id'] = self.rel_id
        result['schema_version'] = self.__class__.schema_version
        result['identifying_properties'] = identifying_props
        result['properties'] = regular_props
        result['rel_type'] = self.rel_type
        # Store minimal node information for SQL efficiency
        result['start_node'] = {
            'primary_label': self.start_node.primary_label,
            'node_id': self.start_node.node_id
        }
        result['end_node'] = {
            'primary_label': self.end_node.primary_label,
            'node_id': self.end_node.node_id
        }

        return result
    
    def merge(self, other: 'FromRelationship') -> 'FromRelationship':
        """Merge another relationship into this one using configured merge strategies.
        
        Args:
            other: Another relationship of the same type to merge with this one
            
        Returns:
            A new merged relationship instance with combined data
            
        Raises:
            ValueError: If relationships have different types, endpoints, or merge conflicts
        """
        from ..base.merge import MERGE_STRATEGIES
        
        # Verify same relationship type
        if self.rel_type != other.rel_type:
            raise ValueError(
                f"Cannot merge relationships of different types: "
                f"{self.rel_type} != {other.rel_type}"
            )
        
        # Verify same start and end nodes
        if self.start_node.node_id != other.start_node.node_id:
            raise ValueError(
                f"Cannot merge relationships with different start nodes: "
                f"{self.start_node.node_id} != {other.start_node.node_id}"
            )
        
        if self.end_node.node_id != other.end_node.node_id:
            raise ValueError(
                f"Cannot merge relationships with different end nodes: "
                f"{self.end_node.node_id} != {other.end_node.node_id}"
            )
        
        # Merge properties
        merged_data = {
            'rel_type': self.rel_type,
            'start_node': self.start_node,
            'end_node': self.end_node
        }
        
        # Merge created_at (strategy: min)
        self_created_at = getattr(self, 'created_at')
        other_created_at = getattr(other, 'created_at')
        
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
        self_modified_at = getattr(self, 'modified_at')
        other_modified_at = getattr(other, 'modified_at')
        
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
        self_count = getattr(self, 'count')
        other_count = getattr(other, 'count')
        
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
        self_sources = getattr(self, 'sources')
        other_sources = getattr(other, 'sources')
        
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
    
    # Model configuration for better error handling
    model_config = ConfigDict(
        extra="forbid",  # Catch typos in field names
        validate_assignment=True,
        str_strip_whitespace=True,
        validate_default=True
    )