import pytest
from hypothesis import given, strategies as st, settings, example
from dilemma.lang import evaluate
from dilemma.lookup import lookup_variable

# Strategy for generating nested variable names with smaller size limits - updated to use slash notation
nested_variable_names_st = st.lists(
    st.from_regex(r"[a-zA-Z_][a-zA-Z0-9_]{1,5}", fullmatch=True), min_size=2, max_size=3
).map(lambda segments: "/" + "/".join(segments))

# Strategy for generating smaller nested dictionaries with fewer potential values
nested_dicts_st = st.recursive(
    st.dictionaries(
        st.from_regex(r"[a-zA-Z_][a-zA-Z0-9_]{1,5}", fullmatch=True),
        st.one_of(st.integers(min_value=-10, max_value=10), st.booleans()),
        max_size=3,
    ),
    lambda children: st.dictionaries(
        st.from_regex(r"[a-zA-Z_][a-zA-Z0-9_]{1,5}", fullmatch=True), children, max_size=2
    ),
    max_leaves=5,
)


# Use settings to limit the number of test examples
@settings(max_examples=20)
@given(
    var_path=nested_variable_names_st,
    value=st.integers(min_value=-10, max_value=10),
    context=nested_dicts_st,
)
@example(var_path="/a/b/c", value=42, context={"a": {"b": {}}})
def test_evaluate_nested_variable(var_path, value, context):
    """Test evaluating nested variable names."""
    # Inject the value into the context at the specified path
    segments = var_path.strip('/').split("/")

    # Create a new context to avoid modifying the original
    modified_context = context.copy()
    current = modified_context

    # Inject value at the path, ensuring all intermediate segments are dictionaries
    for segment in segments[:-1]:
        if segment not in current or not isinstance(current[segment], dict):
            current[segment] = {}
        current = current[segment]
    current[segments[-1]] = value

    # Evaluate the expression using the modified context
    result = evaluate(var_path, modified_context)
    assert result == value


# Add specific test cases for edge cases
def test_evaluate_nested_variable_specific_cases():
    """Test evaluating nested variable names with specific test cases."""
    # Test case 1: Simple nested path
    context = {"a": {"b": 42}}
    assert evaluate("/a/b", context) == 42

    # Test case 2: Deeper nesting
    context = {"x": {"y": {"z": 99}}}
    assert evaluate("/x/y/z", context) == 99

    # Test case 3: Path with boolean value
    context = {"flag": {"state": True}}
    assert evaluate("/flag/state", context) is True

    # Add test for array indexing using REST-style path (numeric segment)
    context = {"items": [10, 20, 30]}
    assert evaluate("/items/1", context) == 20

    # Add test for nested array access
    context = {"users": [{"name": "Alice"}, {"name": "Bob"}]}
    assert evaluate("/users/1/name", context) == "Bob"


@settings(max_examples=20)
@given(var_path=nested_variable_names_st, context=nested_dicts_st)
@example(var_path="/a/b/c", context={"a": {"x": 5}})
@example(var_path="/A0/A0", context={"A0": 0})
def test_evaluate_undefined_nested_variable(var_path, context):
    """Test evaluating undefined nested variable paths."""
    # Strip the leading slash and split to get the path segments
    segments = var_path.strip('/').split("/")

    # Create a new context that definitely doesn't contain the path
    modified_context = {}

    # Start with a clean context that doesn't have the path
    # Then selectively add parts of the original context that don't conflict
    for key, value in context.items():
        if key != segments[0]:
            modified_context[key] = value

    # If we need to ensure the first segment exists but the path is still invalid,
    # add a non-dict value at the first segment to make deeper segments invalid
    if len(segments) > 1 and segments[0] not in modified_context:
        modified_context[segments[0]] = 0  # Use a non-dict value to make nested lookups fail

    # Try to evaluate the expression, should raise some kind of lookup error
    with pytest.raises((NameError, AttributeError)):  # Accept either error type
        evaluate(var_path, modified_context)


@settings(max_examples=20)
@given(
    var_path=nested_variable_names_st,
    value=st.integers(min_value=-10, max_value=10),
    context=nested_dicts_st,
)
@example(var_path="/a/b", value=42, context={})
def test_nested_lookup_variable(var_path, value, context):
    """Test resolving nested variable names using lookup_variable."""
    # Inject the value into the context at the specified path
    segments = var_path.strip('/').split("/")

    # Create a new context to avoid modifying the original
    modified_context = context.copy()
    current = modified_context

    # Inject value at the path, ensuring all intermediate segments are dictionaries
    for segment in segments[:-1]:
        if segment not in current or not isinstance(current[segment], dict):
            current[segment] = {}
        current = current[segment]
    current[segments[-1]] = value

    # Resolve the variable path
    result = lookup_variable(var_path, modified_context)
    assert result == value


# Add test for array access with REST-style paths
def test_array_access_with_rest_paths():
    """Test array access using REST-style paths with numeric segments."""
    # Simple array access
    context = {"numbers": [1, 2, 3, 4, 5]}
    assert lookup_variable("/numbers/2", context) == 3

    # Nested array access
    context = {
        "data": {
            "items": [
                {"id": 1, "value": "first"},
                {"id": 2, "value": "second"}
            ]
        }
    }
    assert lookup_variable("/data/items/0/id", context) == 1
    assert lookup_variable("data/items/1/value", context) == "second"

    # Verify invalid array access raises proper error
    with pytest.raises(NameError):
        lookup_variable("/data/items/99", context)
