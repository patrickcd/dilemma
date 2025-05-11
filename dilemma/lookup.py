"""
This module provides functions to perform attribute and item lookups on objects
and mappings, using jq for powerful path resolution.
It also includes a function to compile getters for optimized access paths.
"""

import jq
import json
import re
from datetime import datetime

from dilemma.path import convert_rest_path_to_jq

# These types are acceptable as variable values
# Updated to include dict and list, which are valid JSON types.
SUPPORTED_TYPES = (int, float, bool, str, datetime, dict, list)

# Regular expression to detect array indexing in paths
ARRAY_INDEX_PATTERN = re.compile(r'(\[\d+\])')

# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        return {"__datetime__": obj.isoformat()}


def lookup_variable(path: str, json_obj: dict) -> int | float | bool | str | datetime | dict | list:
    """
    Look up a variable using REST-style path notation.
    The leading forward slash is optional.
    Numeric path segments are treated as array indices.

    Args:
        path: Path expression (e.g., "/users/1/name" or "config/settings" or "username")
        json_obj: Preprocessed JSON object

    Returns:
        Value at the specified path
    """
    # Handle empty or root path
    if path == "/" or not path:
        return json_obj

    # If path contains a dot, it's invalid (we don't support dot notation)
    if '.' in path:
        raise ValueError(f"Path cannot contain dots, use forward slashes instead: {path}")

    # If path contains bracket notation, it's invalid (we only support REST-style)
    if '[' in path:
        raise ValueError(f"Path cannot contain bracket notation '[index]', use REST-style with forward slashes instead: {path}")

    # Handle simple variable name with no slashes
    if '/' not in path:
        if path not in json_obj:
            raise NameError(f"Variable '{path}' is not defined")
        return json_obj[path]

    # Handle simple nested paths like "user/nonexistent" directly
    segments = path.strip('/').split('/')
    current = json_obj
    try:
        for i, segment in enumerate(segments):
            if segment.isdigit() and isinstance(current, list):
                # Handle numeric segment as array index
                index = int(segment)
                if index < 0 or index >= len(current):
                    raise NameError(f"Index {index} out of bounds for array (length {len(current)})")
                current = current[index]
            elif segment not in current:
                raise NameError(f"Property '{segment}' not found in path '{path}'")
            else:
                current = current[segment]
        return current
    except (TypeError, KeyError) as e:
        raise NameError(f"Path '{path}' cannot be resolved: {str(e)}")

