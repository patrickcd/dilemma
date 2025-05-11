"""
Path handling utilities for Dilemma.

This module provides functions for working with path expressions
and converting between different path formats.
"""

def convert_rest_path_to_jq(path: str) -> str:
    """
    Convert a REST-style path to JQ format.
    Supports REST-style numeric path segments for array indexing.
    The leading forward slash is optional.
    """
    # If path contains a dot, it's invalid (we don't support dot notation)
    if '.' in path:
        raise ValueError(f"Path cannot contain dots, use forward slashes instead: {path}")

    # If path contains bracket notation, it's invalid (we only support REST-style)
    if '[' in path:
        raise ValueError(f"Path cannot contain bracket notation '[index]', use REST-style with forward slashes instead: {path}")

    # Handle simple variable names with no slashes and no array indexing
    if '/' not in path:
        return f".{path}"

    # Handle REST-style path
    # Strip leading slash if present
    if path.startswith('/'):
        path = path[1:]

    # Split the path and filter out empty segments
    parts = [p for p in path.split('/') if p]

    if not parts:
        return "."  # Root path

    # Build JQ path, converting numeric segments to array indices
    jq_path = ""
    for part in parts:
        if part.isdigit():
            # Numeric segment - treat as array index
            jq_path += f"[{part}]"
        else:
            # Named segment - treat as object property
            jq_path += f".{part}"

    return jq_path
