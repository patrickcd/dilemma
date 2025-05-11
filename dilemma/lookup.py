"""
This module provides functions to perform attribute and item lookups on objects
and mappings, using jq for powerful path resolution.
It also includes a function to compile getters for optimized access paths.
"""

import jq
import json
import re
from datetime import datetime

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
    Look up a variable in a preprocessed JSON object using a dot-separated path.

    Args:
        path: Path expression (e.g., "user.profile.age" or "users[0].name")
        json_obj: Preprocessed JSON object (must already be JSON compatible)

    Returns:
        Value at the specified path
    """
    # Handle top-level variables directly for optimization
    if "." not in path and "[" not in path:
        if isinstance(json_obj, dict) and path in json_obj:
            value = json_obj[path]
            if value is None:
                return None
            return value
        raise NameError(f"Variable '{path}' is not defined")

    # Convert expression path to jq path
    if path.startswith("["):
        jq_path = "." + path
    else:
        jq_path = "." + path

    try:
        # Execute jq query
        results = jq.compile(jq_path).input(json_obj).all()

        # Handle missing or null results
        if not results or results[0] is None:
            raise NameError(f"Variable '{path}' is not defined or path cannot be resolved.")

        return results[0]
    except Exception as e:
        raise NameError(f"Variable '{path}' cannot be resolved: {str(e)}")
