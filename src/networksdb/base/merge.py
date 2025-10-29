"""Merge strategies for models schema package.

This module contains merge strategy implementations used by nodes and relationships
to combine duplicate records according to their configured merge strategies.
"""

from typing import Any, Callable, Dict


def error_if_different(existing: Any, new: Any, property_name: str) -> Any:
    """Fail if values are different.
    
    Args:
        existing: The existing value
        new: The new value to merge
        property_name: Name of the property being merged
        
    Returns:
        The existing value if they match
        
    Raises:
        ValueError: If values differ
    """
    if existing != new:
        raise ValueError(
            f"Cannot merge {property_name}: conflicting values "
            f"(existing={existing!r}, new={new!r})"
        )
    return existing


def take_first(existing: Any, new: Any, property_name: str) -> Any:
    """Keep the existing value, ignoring the new one.
    
    Args:
        existing: The existing value
        new: The new value to merge
        property_name: Name of the property being merged
        
    Returns:
        The existing value if not None, otherwise the new value
    """
    return existing if existing is not None else new


def take_last(existing: Any, new: Any, property_name: str) -> Any:
    """Replace with the new value.
    
    Args:
        existing: The existing value
        new: The new value to merge
        property_name: Name of the property being merged
        
    Returns:
        The new value if not None, otherwise the existing value
    """
    return new if new is not None else existing


def min_value(existing: Any, new: Any, property_name: str) -> Any:
    """Take the minimum value (for timestamps and numerics).
    
    Args:
        existing: The existing value
        new: The new value to merge
        property_name: Name of the property being merged
        
    Returns:
        The minimum of the two values
    """
    if existing is None:
        return new
    if new is None:
        return existing
    try:
        return min(existing, new)
    except TypeError as e:
        raise TypeError(
            f"Cannot apply 'min' strategy to {property_name}: "
            f"values are not comparable ({existing!r}, {new!r})"
        ) from e


def max_value(existing: Any, new: Any, property_name: str) -> Any:
    """Take the maximum value (for timestamps and numerics).
    
    Args:
        existing: The existing value
        new: The new value to merge
        property_name: Name of the property being merged
        
    Returns:
        The maximum of the two values
    """
    if existing is None:
        return new
    if new is None:
        return existing
    try:
        return max(existing, new)
    except TypeError as e:
        raise TypeError(
            f"Cannot apply 'max' strategy to {property_name}: "
            f"values are not comparable ({existing!r}, {new!r})"
        ) from e


def sum_values(existing: Any, new: Any, property_name: str) -> Any:
    """Sum the values (for counters and metrics).
    
    Args:
        existing: The existing value
        new: The new value to merge
        property_name: Name of the property being merged
        
    Returns:
        The sum of the two values
    """
    # Treat None as 0 for summing
    existing = existing if existing is not None else 0
    new = new if new is not None else 0
    
    try:
        return existing + new
    except TypeError as e:
        raise TypeError(
            f"Cannot apply 'sum' strategy to {property_name}: "
            f"values are not numeric ({existing!r}, {new!r})"
        ) from e


def union_values(existing: Any, new: Any, property_name: str) -> Any:
    """Collect unique values (for lists).
    
    Args:
        existing: The existing value (should be a list)
        new: The new value to merge (should be a list)
        property_name: Name of the property being merged
        
    Returns:
        A list containing the union of unique values
    """
    if existing is None:
        return new
    if new is None:
        return existing
    
    if not isinstance(existing, list) or not isinstance(new, list):
        raise TypeError(
            f"Cannot apply 'union' strategy to {property_name}: "
            f"values must be lists (existing={type(existing).__name__}, "
            f"new={type(new).__name__})"
        )
    
    # Maintain order while removing duplicates
    seen = set()
    result = []
    for item in existing + new:
        # Handle unhashable types by using repr as fallback
        try:
            if item not in seen:
                seen.add(item)
                result.append(item)
        except TypeError:
            # For unhashable types, just append (can't dedupe efficiently)
            if item not in result:
                result.append(item)
    
    return result


def take_any_non_null(existing: Any, new: Any, property_name: str) -> Any:
    """Take any non-null value, preferring the new value if both are non-null.

    This strategy is ideal for dynamic properties where you want to preserve
    any available data, giving precedence to the newer value.

    Args:
        existing: The existing value
        new: The new value to merge
        property_name: Name of the property being merged

    Returns:
        The new value if not None, otherwise the existing value
    """
    if new is not None:
        return new
    return existing


def take_any_non_empty(existing: Any, new: Any, property_name: str) -> Any:
    """Take any non-empty value, preferring the new value if both are non-empty.

    This strategy is ideal for dynamic properties where you want to preserve
    meaningful data, giving precedence to the newer value. Treats None, empty
    strings, empty lists, and empty dicts as "empty". Explicit values like 0,
    0.0, and False are considered non-empty (they have explicit meaning).

    Args:
        existing: The existing value
        new: The new value to merge
        property_name: Name of the property being merged

    Returns:
        The new value if non-empty, otherwise the existing value if non-empty,
        otherwise None
    """

    def is_empty(val: Any) -> bool:
        """Check if a value is considered empty."""
        return val is None or val == "" or val == [] or val == {}

    if not is_empty(new):
        return new
    if not is_empty(existing):
        return existing
    return None


# Registry of all available merge strategies
MERGE_STRATEGIES: Dict[str, Callable[[Any, Any, str], Any]] = {
    "error_if_different": error_if_different,
    "take_first": take_first,
    "take_last": take_last,
    "take_any_non_null": take_any_non_null,
    "take_any_non_empty": take_any_non_empty,
    "min": min_value,
    "max": max_value,
    "sum": sum_values,
    "union": union_values,
}