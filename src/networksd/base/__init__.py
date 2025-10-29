"""Base classes for generated models.

This module re-exports the base classes from ziptie_schema.base for convenience.
"""
from ziptie_schema.base.models import BaseNode, BaseRelationship
from ziptie_schema.base.mixins import IDGenerationMixin

__all__ = [
    "BaseNode",
    "BaseRelationship", 
    "IDGenerationMixin",
]