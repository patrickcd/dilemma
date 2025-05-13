"""
This module provides functions to perform attribute and item lookups on objects
and mappings, using jq for powerful path resolution.
It also includes a function to compile getters for optimized access paths.
"""

import jq
import json
import re
from datetime import datetime

from .exc import VariableError

# These types are acceptable as variable values
# Updated to include dict and list, which are valid JSON types.
SUPPORTED_TYPES = (int, float, bool, str, datetime, dict, list)

# Regular expression to detect array indexing in paths
ARRAY_INDEX_PATTERN = re.compile(r"(\[\d+\])")


# Custom JSON encoder for datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        return {"__datetime__": obj.isoformat()}


def lookup_variable(
    path: str, json_obj: dict
) -> int | float | bool | str | datetime | dict | list:
    """
    Look up a variable in a preprocessed JSON object using a dot-separated path.

    Args:
        path: Path expression (e.g., "user.profile.age" or "users[0].name")
        json_obj: Preprocessed JSON object (must already be JSON compatible)

    Returns:
        Value at the specified path
    """
    original_path = path
    if "'s" in path:
        # Transform possessive path to dotted path with regex to handle any whitespace
        path = re.sub(r"'s\s+", ".", path)

    # Handle top-level variables directly for optimization
    if "." not in path and "[" not in path:
        if isinstance(json_obj, dict) and path in json_obj:
            return json_obj[path]

        raise VariableError(
            template_key="undefined_variable",
            name=path
        )

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
            raise VariableError(
                template_key="unresolved_path",
                path=original_path,
                details="Path exists but resolves to null or is missing"
            )

        return results[0]
    except Exception as e:
        raise VariableError(
            template_key="unresolved_path",
            path=original_path,
            details=str(e)
        )


def evaluate_jq_expression(
    jq_expr: str, json_obj: dict
) -> int | float | bool | str | datetime | dict | list:
    """
    Evaluate a raw JQ expression against a JSON object.

    Args:
        jq_expr: Raw JQ expression (e.g., ".user.profile.age")
        json_obj: JSON object to query

    Returns:
        The value resulting from the JQ query

    Raises:
        NameError: If the JQ expression cannot be resolved
    """
    try:
        # Validate the jq syntax before compiling
        if not jq_expr.strip():
            raise VariableError(
                template_key="invalid_jq",
                expr=jq_expr,
                details="Empty JQ expression"
            )

        # Compile and execute the JQ expression
        compiled_jq = jq.compile(jq_expr)
        results = list(compiled_jq.input(json_obj))

        # jq always returns a list of results
        if not results:
            raise VariableError(
                template_key="invalid_jq",
                expr=jq_expr,
                details="JQ expression returned no results"
            )

        # For consistency with lookup_variable, just return the first result
        return results[0]
    except Exception as e:
        # Instead of trying to catch specific jq exceptions, catch all exceptions
        # and convert them to VariableError with a descriptive message
        error_msg = str(e)
        raise VariableError(
            template_key="invalid_jq",
            expr=jq_expr,
            details=error_msg
        )
