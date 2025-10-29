"""Generated Ziptie graph models."""

# Import registry for convenience (safe imports for generation-time use)
try:
    from .registry import (
        registry,
        # Required by ziptie-ingest spec
        get_node_class,
        get_relationship_class,
        list_node_classes,
        list_relationship_classes,
        # Neo4j deserialization
        get_node_by_label,
        get_relationship_by_type,
        list_primary_labels,
        list_relationship_types,
        deserialize_node,
        deserialize_relationship,
        deserialize_node_from_labels,
        deserialize_neo4j_node,
    )
except ImportError:
    # Registry not yet generated - will be available after generation completes
    pass

# Import SQL metadata for ziptie-parsing consumption
try:
    from .sql_metadata import sql_metadata
except ImportError:
    # SQL metadata not yet generated
    pass

# Import constants for convenience
try:
    from .constants import Labels, Properties, RelationshipTypes
except ImportError:
    # Constants not yet generated
    pass

__all__ = [
    "registry",
    # Required by ziptie-ingest spec
    "get_node_class",
    "get_relationship_class",
    "list_node_classes",
    "list_relationship_classes",
    # Neo4j deserialization
    "get_node_by_label",
    "get_relationship_by_type",
    "list_primary_labels",
    "list_relationship_types",
    "deserialize_node",
    "deserialize_relationship",
    "deserialize_node_from_labels",
    "deserialize_neo4j_node",
    # SQL metadata (for ziptie-parsing)
    "sql_metadata",
    # Constants
    "Labels",
    "Properties",
    "RelationshipTypes",
]
