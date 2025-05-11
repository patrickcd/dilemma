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
        if isinstance(obj, datetime):
            return {"__datetime__": obj.isoformat()}
        try:
            # Try to use the default encoder for other types
            return super().default(obj)
        except TypeError:
            # For non-serializable objects, return a string representation
            return f"<non-serializable: {type(obj).__name__}>"

def lookup_variable(obj, path, precomputed_json=None) -> int | float | bool | str | datetime | dict | list:
    """
    Look up a variable in a context using a dot-separated path via jq.

    Given:
      - obj: the context object (a dictionary, list, or JSON string)
      - path: a path expression, e.g. "user.profile.age" or "users[0].name"
      - precomputed_json: optional pre-processed JSON data to avoid repeated processing
    Returns:
      - the value at that path, or raises a NameError if it doesn't exist or is invalid.
    """

    # Handle top-level variables directly for optimization (when no complex path is present)
    if "." not in path and "[" not in path and not isinstance(obj, str):
        if isinstance(obj, dict) and path in obj:
            value = obj[path]
            # None values should be returned as None, not converted to strings
            if value is None:
                return None
            # Handle non-serializable objects like lambda functions
            if callable(value) or not isinstance(value, SUPPORTED_TYPES):
                return f"<non-serializable: {type(value).__name__}>"
            return value
        raise NameError(f"Variable '{path}' is not defined or path cannot be resolved.")

    # Use precomputed JSON if available
    if precomputed_json is not None:
        json_obj = precomputed_json
    else:
        # If obj is a JSON string, use it directly
        if isinstance(obj, str):
            try:
                json_obj = json.loads(obj)  # Parse the JSON string
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string provided: {e}")
        else:
            # Convert object to JSON-compatible structure and ensure
            # it's safe
            json_obj = json.loads(json.dumps(obj, cls=DateTimeEncoder))

    # Convert expression path to jq path
    # For paths that start with array indexing like users[0], add leading dot
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

        result = results[0]

        # Handle datetime reconstruction
        if isinstance(result, dict) and "__datetime__" in result:
            return datetime.fromisoformat(result["__datetime__"])

        return result
    except Exception as e:
        # Treat all errors as NameError for consistency
        raise NameError(f"Variable '{path}' is not defined or path cannot be resolved. Error: {str(e)}")
