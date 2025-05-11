"""
This module provides functions to perform attribute and item lookups on objects
and mappings, using jq for powerful path resolution.
It also includes a function to compile getters for optimized access paths.
"""

import jq
import json
from datetime import datetime

# These types are acceptable as variable values
# Updated to include dict and list, which are valid JSON types.
SUPPORTED_TYPES = (int, float, bool, str, datetime, dict, list)

# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        return {"__datetime__": obj.isoformat()}

def lookup_variable(obj, path) -> int | float | bool | str | datetime | dict | list:
    """
    Look up a variable in a context using a dot-separated path via jq.

    Given:
      - obj: the context object (a dictionary, list, or JSON string)
      - path: a dot-separated path, e.g. "user.profile.age"
    Returns:
      - the value at that path, or raises a NameError if it doesn't exist or is invalid.
    """

    # Handle top-level variables directly for optimization
    if "." not in path and not isinstance(obj, str):
        if isinstance(obj, dict) and path in obj:
            return obj[path]
        raise NameError(f"Variable '{path}' is not defined or path cannot be resolved.")

    # If obj is a JSON string, use it directly
    if isinstance(obj, str):
        try:
            json_obj = json.loads(obj)  # Parse the JSON string
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string provided: {e}")
    else:
        # Convert object to JSON-compatible structure and ensure
        # it;s safe
        json_obj = json.loads(json.dumps(obj, cls=DateTimeEncoder))

    # Conver expression patht to jq path
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
    except Exception:
        # Treat all errors as NameError for consistency
        raise NameError(f"Variable '{path}' is not defined or path cannot be resolved.")
