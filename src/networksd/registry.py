"""Registry of all generated node and relationship classes.

Provides dual lookup mechanisms:
1. By class name - for Python code and ziptie-ingest (includes all classes)
2. By primary_label/rel_type - for Neo4j deserialization (excludes classifiable base classes)
"""
from typing import Type, Dict, List, Any, Optional

# Import all node classes
from .nodes.ip_address import IPAddress
from .nodes.private_ip_address import PrivateIPAddress
from .nodes.public_ip_address import PublicIPAddress
from .nodes.domain import Domain
from .nodes.email_address import EmailAddress
from .nodes.email import Email

# Import all relationship classes
from .relationships.has_ip import HasIP
from .relationships.from_relationship import FromRelationship
from .relationships.to import To
from .relationships.knows import Knows


class Registry:
    """Registry for node and relationship class lookups."""
    
    def __init__(self):
        """Initialize registry with dual lookup mechanisms."""
        
        # Python/code use: class_name -> class (includes ALL classes)
        self.node_classes: Dict[str, Type] = {
            "IPAddress": IPAddress,
            "PrivateIPAddress": PrivateIPAddress,
            "PublicIPAddress": PublicIPAddress,
            "Domain": Domain,
            "EmailAddress": EmailAddress,
            "Email": Email,
        }
        
        self.relationship_classes: Dict[str, Type] = {
            "HasIP": HasIP,
            "FromRelationship": FromRelationship,
            "To": To,
            "Knows": Knows,
        }
        
        # Neo4j use: primary_label/rel_type -> class (excludes classifiable base classes)
        # Classifiable nodes are excluded since they're never instantiated directly in Neo4j
        # Nodes with roles or auto_labels are INCLUDED since they're the same type, just with dynamic labels
        self.nodes: Dict[str, Type] = {
            "PrivateIPAddress": PrivateIPAddress,
            "PublicIPAddress": PublicIPAddress,
            "Domain": Domain,
            "EmailAddress": EmailAddress,
            "Email": Email,
        }
        
        self.relationships: Dict[str, Type] = {
            "HAS_IP": HasIP,
            "FROM": FromRelationship,
            "TO": To,
            "Knows": Knows,
        }
        
        # NEW: Class to labels mapping for best-match deserialization
        self.class_to_labels: Dict[Type, set] = {
            IPAddress: {
                "IPAddress"            },
            PrivateIPAddress: {
                "PrivateIPAddress",
                "IPAddress"            },
            PublicIPAddress: {
                "PublicIPAddress",
                "IPAddress"            },
            Domain: {
                "Domain"            },
            EmailAddress: {
                "EmailAddress"            },
            Email: {
                "Email"            },
        }
        
    
    # ========== Python/ziptie-ingest Interface (REQUIRED BY SPEC) ==========
    
    def get_node_class(self, class_name: str) -> Type:
        """Get node class by Python class name.
        
        This is for Python code and configuration files that reference classes by name.
        Includes ALL node classes, even classifiable base classes.
        
        Args:
            class_name: The Python class name (e.g., "IPAddress", "PrivateIPAddress")
            
        Returns:
            The node class
            
        Raises:
            KeyError: If class_name not found
        """
        if class_name not in self.node_classes:
            available = list(self.node_classes.keys())
            raise KeyError(
                f"Node class '{class_name}' not found. Available: {available}"
            )
        return self.node_classes[class_name]
    
    def get_relationship_class(self, class_name: str) -> Type:
        """Get relationship class by Python class name.
        
        This is for Python code and configuration files that reference classes by name.
        
        Args:
            class_name: The Python class name (e.g., "Connected")
            
        Returns:
            The relationship class
            
        Raises:
            KeyError: If class_name not found
        """
        if class_name not in self.relationship_classes:
            available = list(self.relationship_classes.keys())
            raise KeyError(
                f"Relationship class '{class_name}' not found. Available: {available}"
            )
        return self.relationship_classes[class_name]
    
    def list_node_classes(self) -> List[str]:
        """List all available node class names.
        
        Returns all Python class names, including classifiable base classes.
        """
        return list(self.node_classes.keys())
    
    def list_relationship_classes(self) -> List[str]:
        """List all available relationship class names."""
        return list(self.relationship_classes.keys())
    
    # ========== Neo4j Deserialization Interface ==========
    
    def get_node_by_label(self, primary_label: str) -> Type:
        """Get node class by Neo4j primary label.
        
        This is for deserializing nodes from Neo4j queries.
        Excludes classifiable base classes since they don't exist in Neo4j.
        
        Args:
            primary_label: The primary label from Neo4j
            
        Returns:
            The node class
            
        Raises:
            KeyError: If primary_label not found
        """
        if primary_label not in self.nodes:
            raise KeyError(
                f"Node with label '{primary_label}' not found. "
                f"Available: {list(self.nodes.keys())}"
            )
        return self.nodes[primary_label]
    
    def get_relationship_by_type(self, rel_type: str) -> Type:
        """Get relationship class by Neo4j relationship type.
        
        This is for deserializing relationships from Neo4j queries.
        
        Args:
            rel_type: The relationship type from Neo4j (e.g., "CONNECTED")
            
        Returns:
            The relationship class
            
        Raises:
            KeyError: If rel_type not found
        """
        if rel_type not in self.relationships:
            raise KeyError(
                f"Relationship type '{rel_type}' not found. "
                f"Available: {list(self.relationships.keys())}"
            )
        return self.relationships[rel_type]
    
    def list_primary_labels(self) -> List[str]:
        """List unique Neo4j primary labels (excludes classifiable base classes)."""
        return list(self.nodes.keys())
    
    def list_all_primary_labels(self) -> List[str]:
        """List ALL primary labels including duplicates across classes.
        
        This shows which classes share the same ID space (primary_label).
        Useful for understanding label distribution in your schema.
        
        Returns:
            List of all primary labels (may contain duplicates)
        """
        result = []
        for cls in self.node_classes.values():
            label_attr = getattr(cls, '_primary_label', None)
            if hasattr(label_attr, 'get_default'):
                # It's a ModelPrivateAttr
                result.append(label_attr.get_default())
            elif label_attr:
                result.append(label_attr)
            else:
                result.append(cls.__name__)
        return result
    
    def list_relationship_types(self) -> List[str]:
        """List all Neo4j relationship types."""
        return list(self.relationships.keys())
    
    def deserialize_node(self, data: Dict[str, Any]) -> Any:
        """Deserialize a node from dictionary with 'primary_label'.
        
        Simple deserialization when you already know the primary label.
        
        Args:
            data: Dictionary with node properties including 'primary_label'
            
        Returns:
            Instance of the appropriate node class
            
        Raises:
            KeyError: If primary_label missing or unknown
        """
        if "primary_label" not in data:
            raise KeyError("Missing 'primary_label' in node data")
        
        node_class = self.get_node_by_label(data["primary_label"])
        return node_class(**data)
    
    def deserialize_relationship(self, data: Dict[str, Any]) -> Any:
        """Deserialize a relationship from dictionary with 'rel_type'.
        
        Args:
            data: Dictionary with relationship properties including 'rel_type'
            
        Returns:
            Instance of the appropriate relationship class
            
        Raises:
            KeyError: If rel_type missing or unknown
        """
        if "rel_type" not in data:
            raise KeyError("Missing 'rel_type' in relationship data")
        
        rel_class = self.get_relationship_by_type(data["rel_type"])
        return rel_class(**data)
    
    def deserialize_node_from_labels(self, data: Dict[str, Any], labels: List[str]) -> Any:
        """Deserialize a node from Neo4j by finding the class with most matching labels.
        
        This method uses a best-match algorithm:
        1. Compares Neo4j labels with each class's label set
        2. Picks the class with the most matching labels
        3. Adds any extra Neo4j labels to the instance's additional_labels
        
        Example:
            Neo4j labels: ["Transaction", "Suspicious", "HighRisk", "Audit2024"]
            
            Classes in registry:
            - Transaction: labels = {"Transaction"} → 1 match
            - SuspiciousTransaction: labels = {"Transaction", "Suspicious"} → 2 matches (WINNER)
            
            Result: SuspiciousTransaction instance with additional_labels 
                   including ["HighRisk", "Audit2024"]
        
        Args:
            data: Dictionary with node properties
            labels: List of ALL labels from Neo4j
            
        Returns:
            Instance of the best matching node class with extra labels preserved
            
        Raises:
            KeyError: If no class matches any of the provided labels
        """
        neo4j_label_set = set(labels)
        
        # Find the class with the most matching labels
        best_match_class = None
        best_match_score = 0
        best_match_labels = set()
        
        for cls, cls_labels in self.class_to_labels.items():
            # Count how many labels match
            matching_labels = cls_labels & neo4j_label_set
            score = len(matching_labels)
            
            if score > best_match_score:
                best_match_class = cls
                best_match_score = score
                best_match_labels = cls_labels
        
        if not best_match_class:
            raise KeyError(
                f"No class found matching any of labels: {labels}. "
                f"Available classes: {list(self.node_classes.keys())}"
            )
        
        # Create the instance
        instance = best_match_class(**data)
        
        # Add any extra labels that aren't part of the class definition
        extra_labels = list(neo4j_label_set - best_match_labels)
        if extra_labels and hasattr(instance, 'additional_labels'):
            # Merge extra labels with existing additional_labels
            current_labels = getattr(instance, 'additional_labels', [])
            merged_labels = list(set(current_labels) | set(extra_labels))
            instance.additional_labels = merged_labels
        
        return instance
    
    def deserialize_neo4j_node(self, neo4j_node) -> Any:
        """Convenience method to deserialize directly from a Neo4j node object.
        
        Args:
            neo4j_node: A Neo4j node with .labels and properties
            
        Returns:
            Instance of the appropriate node class
            
        Example:
            for record in session.run("MATCH (n) RETURN n"):
                node = registry.deserialize_neo4j_node(record["n"])
        """
        # Extract properties and labels from Neo4j node
        data = dict(neo4j_node)
        labels = list(neo4j_node.labels) if hasattr(neo4j_node, 'labels') else []
        
        if not labels:
            # Fallback if no labels provided
            if 'primary_label' in data:
                return self.deserialize_node(data)
            raise KeyError("No labels found on Neo4j node and no primary_label in data")
        
        return self.deserialize_node_from_labels(data, labels)
    
    @staticmethod
    def combine(*registries: 'Registry', strict: bool = False) -> 'Registry':
        """Combine multiple registries into one.
        
        Args:
            *registries: Registry instances to combine
            strict: If True, raise error on duplicate labels/types
            
        Returns:
            New Registry with combined classes
            
        Raises:
            ValueError: If strict=True and duplicates found
        """
        combined = Registry.__new__(Registry)
        
        # Define registry attributes to combine
        registry_attrs = [
            ('node_classes', 'node class'),
            ('relationship_classes', 'relationship class'),
            ('nodes', 'node primary_label'),
            ('relationships', 'relationship type'),
            ('class_to_labels', None),  # Special handling, no error messages
        ]
        
        for attr_name, error_desc in registry_attrs:
            combined_dict = {}
            
            for reg in registries:
                source_dict = getattr(reg, attr_name, {})
                for key, value in source_dict.items():
                    if strict and key in combined_dict and error_desc:
                        raise ValueError(
                            f"Duplicate {error_desc} '{key}' found. "
                            f"Set strict=False to allow overwriting."
                        )
                    combined_dict[key] = value
            
            setattr(combined, attr_name, combined_dict)
        
        return combined


# Create default instance
registry = Registry()

# ========== REQUIRED MODULE-LEVEL EXPORTS (ziptie-ingest spec) ==========
get_node_class = registry.get_node_class
get_relationship_class = registry.get_relationship_class
list_node_classes = registry.list_node_classes
list_relationship_classes = registry.list_relationship_classes

# ========== Neo4j DESERIALIZATION EXPORTS ==========
get_node_by_label = registry.get_node_by_label
get_relationship_by_type = registry.get_relationship_by_type
list_primary_labels = registry.list_primary_labels
list_all_primary_labels = registry.list_all_primary_labels
list_relationship_types = registry.list_relationship_types
deserialize_node = registry.deserialize_node
deserialize_relationship = registry.deserialize_relationship
deserialize_node_from_labels = registry.deserialize_node_from_labels
deserialize_neo4j_node = registry.deserialize_neo4j_node

# Registry exports for Neo4j label/type to class mapping
NODE_REGISTRY = registry.nodes
RELATIONSHIP_REGISTRY = registry.relationships