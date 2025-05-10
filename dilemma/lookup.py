"""
This module provides functions to perform attribute and item lookups on objects
and mappings, including nested lookups using dot-separated paths.
It also includes a function to compile getters for optimized access paths.
"""

import json

def nested_getattr(obj, attr) -> int | float | bool:
    """
    Given:
      - obj: an object or mapping
      - attr: a dot-separated path, e.g. "things.that.inspire"
    Returns:
      - the value at that path, or raises an AttributeError if it doesn't exist.
    """
    segments = attr.split(".")
    for i, name in enumerate(segments):
        # If this is not the last segment, check if obj is a container
        if i < len(segments) - 1:
            # For non-final segments, check if obj can contain other objects
            if not isinstance(obj, (dict, object)) or isinstance(obj, (int, float, bool)):
                msg = f"Segment '{name}' refers to a non-container: {obj!r}"
                raise AttributeError(msg)

        try:
            obj = getattr(obj, name)
        except AttributeError:
            try:
                # Check if the object is subscriptable before attempting item access
                if not hasattr(obj, "__getitem__"):
                    raise AttributeError(
                        f"Cannot resolve segment '{name}' on {obj!r} - not subscriptable"
                    )
                obj = obj[name] # type: ignore[assignment]
            except (KeyError, TypeError):
                raise AttributeError(
                    f"Cannot resolve segment '{name}' on {obj!r}"
                ) from None

    check_numeric(obj)
    return obj


def check_numeric(value):
    """
    Check if the value is numeric (int or float).
    """
    if not isinstance(value, (int, float, bool)):
        raise TypeError(f"Expected numeric or boolean value, got {type(value).__name__}")


def compile_getter(ref, sample_context_json):
    """
    Given:
      - ref: a dot-separated path, e.g. "things.that.inspire"
      - sample_context_json: a JSON string representing the structure of the data
        that will be passed to the getter function

    Returns:
      - a function getter(context) that performs the chain of attribute/item lookups

    Using JSON for sample data ensures we don't execute property getters
    with side effects.
    """
    # Parse the JSON string to get a safe sample context
    try:
        sample_context = json.loads(sample_context_json)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in sample_context_json: {e}")

    segments = ref.split(".")
    ops = []  # each entry will be ('attr', name) or ('item', name)
    cursor = sample_context

    # Figure out, at compile time, which lookup works for each segment
    for name in segments:
        # For JSON objects (dicts), use item lookup
        if isinstance(cursor, dict):
            if name in cursor:
                ops.append(("item", name))
                cursor = cursor[name]
            else:
                raise ValueError(f"Key '{name}' not found in dictionary at this path")
        # For JSON objects that might be accessed via attributes in Python
        else:
            # Default to attribute access for compatibility with Python objects
            ops.append(("attr", name))
            # Since we're working with JSON data, we can't actually resolve further
            # Just assume the rest will be available at runtime
            break

    # Build a literal expression like context.things['that'].inspire
    expr = "context"
    for kind, name in ops:
        if kind == "attr":
            expr += f".{name}"
        else:
            expr += f"[{name!r}]"

    # Wrap it in a lambda that takes a context parameter
    src = f"lambda context: {expr}"

    try:
        # Note - eval is being used with an expression generated internally
        #  that should be safe, as it only contains attribute/item lookups
        getter = eval(src, {})  # use empty globals
    except Exception as e:
        raise ValueError(f"Failed to compile {src!r}: {e}")

    return getter
