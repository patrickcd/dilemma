import pytest
import json
from hypothesis import given, strategies as st, settings, example
from dilemma.lang import evaluate
from dilemma.lookup import nested_getattr, check_numeric, compile_getter

# Strategy for generating nested variable names with smaller size limits
nested_variable_names_st = st.lists(
    st.from_regex(r"[a-zA-Z_][a-zA-Z0-9_]{1,5}", fullmatch=True), min_size=2, max_size=3
).map(".".join)

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
@example(var_path="a.b.c", value=42, context={"a": {"b": {}}})
def test_evaluate_nested_variable(var_path, value, context):
    """Test evaluating nested variable names."""
    # Inject the value into the context at the specified path
    segments = var_path.split(".")

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
    assert evaluate("a.b", context) == 42

    # Test case 2: Deeper nesting
    context = {"x": {"y": {"z": 99}}}
    assert evaluate("x.y.z", context) == 99

    # Test case 3: Path with boolean value
    context = {"flag": {"state": True}}
    assert evaluate("flag.state", context) is True


@settings(max_examples=20)
@given(var_path=nested_variable_names_st, context=nested_dicts_st)
@example(var_path="a.b.c", context={"a": {"x": 5}})
@example(var_path="a.b", context={"a": 5})
def test_evaluate_undefined_nested_variable(var_path, context):
    """Test that evaluating an undefined nested variable raises a NameError."""
    # Ensure the variable path does not exist in the context
    segments = var_path.split(".")
    current = context
    for segment in segments[:-1]:
        if not isinstance(current, dict) or segment not in current:
            break
        current = current[segment]
    else:
        if isinstance(current, dict):
            current.pop(segments[-1], None)

    with pytest.raises(
        NameError,
        match=f"Variable '{var_path}' is not defined or path cannot be resolved",
    ):
        evaluate(var_path, context)


@settings(max_examples=20)
@given(
    var_path=nested_variable_names_st,
    value=st.integers(min_value=-10, max_value=10),
    context=nested_dicts_st,
)
@example(var_path="a.b", value=42, context={})
def test_nested_getattr(var_path, value, context):
    """Test resolving nested variable names using nested_getattr."""
    # Inject the value into the context at the specified path
    segments = var_path.split(".")

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
    result = nested_getattr(modified_context, var_path)
    assert result == value


def test_nested_getattr_manually():
    """Manual tests for nested_getattr with specific test cases."""
    # Test case 1: Simple nested dictionary
    context = {"a": {"b": 123}}
    assert nested_getattr(context, "a.b") == 123

    # Test case 2: Mixed attribute and item access
    class TestObj:
        def __init__(self):
            self.value = {"x": 42}

    obj = TestObj()
    context = {"obj": obj}
    assert nested_getattr(context, "obj.value.x") == 42


@settings(max_examples=10)
@given(var_path=nested_variable_names_st, context=nested_dicts_st)
def test_nested_getattr_undefined_variable(var_path, context):
    """Test that nested_getattr raises an AttributeError for undefined paths."""
    # We don't need to modify the context - just try to access a path that
    # doesn't exist and expect an AttributeError
    with pytest.raises(AttributeError):
        nested_getattr(context, var_path)


def test_nested_attribute_access():
    """Test accessing nested attributes of objects."""

    # Create test classes with nested attributes
    class Inner:
        def __init__(self):
            self.value = 42  # Integer value
            self.flag = True  # Boolean value
            self.rate = 3.14  # Float value

    class Outer:
        def __init__(self):
            self.inner = Inner()
            # Using numeric value for name since only int/float/bool are supported
            self.value = 100

    # Test direct attribute access
    obj = Outer()
    assert nested_getattr(obj, "inner.value") == 42
    assert nested_getattr(obj, "inner.flag") is True
    assert nested_getattr(obj, "inner.rate") == pytest.approx(3.14)
    assert nested_getattr(obj, "value") == 100

    # Test with expression evaluation
    context = {"obj": obj}
    assert evaluate("obj.inner.value", context) == 42
    assert evaluate("obj.inner.flag", context) is True
    assert evaluate("obj.inner.rate", context) == pytest.approx(3.14)
    assert evaluate("obj.value", context) == 100

    # Test with expressions using the attributes
    assert evaluate("obj.inner.value * 2", context) == 84
    assert evaluate("obj.inner.flag and True", context) is True
    assert evaluate("obj.inner.rate + 2.0", context) == pytest.approx(5.14)


def test_mixed_attribute_and_dict_access():
    """Test mixed attribute and dictionary access in nested paths."""

    # Create a class with both attributes and dictionary properties
    class Container:
        def __init__(self):
            self.data = {"x": 10, "y": {"z": 20}}
            # Only numeric values are supported for leaf nodes
            self.flag = True
            self.count = 5

    obj = Container()

    # Test nested lookups combining attribute and dictionary access
    assert nested_getattr(obj, "data.x") == 10
    assert nested_getattr(obj, "data.y.z") == 20
    assert nested_getattr(obj, "flag") is True
    assert nested_getattr(obj, "count") == 5

    # Test with expression evaluation
    context = {"container": obj}
    assert evaluate("container.data.x", context) == 10
    assert evaluate("container.data.y.z", context) == 20
    assert evaluate("container.flag", context) is True

    # Test with expressions using the attributes
    assert evaluate("container.data.x + container.data.y.z", context) == 30
    assert evaluate("container.flag and container.data.x > 5", context) is True


def test_attribute_access_errors():
    """Test error cases for attribute access."""

    class TestObj:
        def __init__(self):
            self.value = 42
            # String values are not supported
            self.nested = {"data": 100}

    obj = TestObj()
    context = {"obj": obj}

    # Test accessing non-existent attribute
    with pytest.raises(AttributeError):
        nested_getattr(obj, "nonexistent")

    # Test accessing attribute through a non-container
    with pytest.raises(AttributeError):
        nested_getattr(obj, "value.something")

    # Test with expression evaluation
    with pytest.raises(NameError):
        evaluate("obj.nonexistent", context)

    with pytest.raises(NameError):
        evaluate("obj.value.something", context)

    # Test with TypeError for non-numeric values
    obj.string_value = "not supported"
    with pytest.raises(TypeError, match="Expected numeric or boolean value"):
        nested_getattr(obj, "string_value")

    obj.list_value = [1, 2, 3]
    with pytest.raises(TypeError, match="Expected numeric or boolean value"):
        nested_getattr(obj, "list_value")


# Add an example with a class to the nested_getattr test
class SimpleClass:
    def __init__(self, value):
        self.value = value  # Integer value
        self.nested = {"data": value * 2}  # Dictionary with integer value
        self.flag = value > 0  # Boolean value
        self.rate = value / 10.0  # Float value


@settings(max_examples=10)
@given(value=st.integers(min_value=-10, max_value=10))
@example(value=42)
def test_nested_getattr_with_class(value):
    """Test nested_getattr with class attributes."""
    obj = SimpleClass(value)

    # Test direct attribute access
    assert nested_getattr(obj, "value") == value
    assert nested_getattr(obj, "flag") is (value > 0)
    assert nested_getattr(obj, "rate") == value / 10.0

    # Test mixed attribute and dictionary access
    assert nested_getattr(obj, "nested.data") == value * 2

    # Test with a context dictionary
    context = {"obj": obj}
    assert nested_getattr(context, "obj.value") == value
    assert nested_getattr(context, "obj.nested.data") == value * 2


def test_nested_getattr_non_container():
    """Test that nested_getattr raises AttributeError for non-containers in the path."""
    # Create a simple object with a primitive value
    obj = {"a": 5}

    # Attempting to access a.b should fail because 'a' is an integer, not a container
    with pytest.raises(AttributeError) as excinfo:
        nested_getattr(obj, "a.b")

    assert "not subscriptable" in str(excinfo.value)


def test_nested_getattr_non_subscriptable():
    """Test nested_getattr with an object that's not subscriptable."""
    class NoSubscript:
        pass

    obj = {"a": NoSubscript()}

    with pytest.raises(AttributeError) as excinfo:
        nested_getattr(obj, "a.b")

    assert "not subscriptable" in str(excinfo.value)


def test_check_numeric_invalid():
    """Test check_numeric with non-numeric values."""
    with pytest.raises(TypeError):
        check_numeric("not a number")

    with pytest.raises(TypeError):
        check_numeric([1, 2, 3])


def test_nested_getattr_invalid_container_check():
    """Test the container check for intermediate segments in nested_getattr."""
    # Create a test object with primitive values that shouldn't be used as containers
    test_obj = {
        "num": 123,
        "bool": True,
        "float_val": 3.14
    }

    # Test with integer as intermediate segment
    with pytest.raises(AttributeError) as excinfo:
        nested_getattr(test_obj, "num.something")
    assert "not subscriptable" in str(excinfo.value)

    # Test with boolean as intermediate segment
    with pytest.raises(AttributeError) as excinfo:
        nested_getattr(test_obj, "bool.something")
    assert "not subscriptable" in str(excinfo.value)

    # Test with float as intermediate segment
    with pytest.raises(AttributeError) as excinfo:
        nested_getattr(test_obj, "float_val.something")
    assert "not subscriptable" in str(excinfo.value)


def test_compile_getter_attr_path():
    """Test compile_getter with attribute access paths."""
    # Test with JSON containing non-dict values that would be accessed via attributes
    sample_json = json.dumps({
        "config": {
            "settings": 5  # This numeric value would be accessed via attributes in real code
        }
    })

    # Get a compiled getter that includes attribute access
    getter = compile_getter("config.settings.enabled", sample_json)

    # Create a test object with the expected structure
    class Settings:
        def __init__(self):
            self.enabled = True

    test_obj = {
        "config": {
            "settings": Settings()
        }
    }

    # The getter should be able to access the attribute
    assert getter(test_obj) is True


def test_compile_getter_eval_error():
    """Test compile_getter handling of eval errors."""
    import unittest.mock

    with unittest.mock.patch('dilemma.lookup.eval') as mock_eval:
        # Set up mock to raise exception
        mock_eval.side_effect = SyntaxError("Invalid syntax")

        # This should handle the exception and raise a ValueError
        with pytest.raises(ValueError) as excinfo:
            compile_getter("a.b", json.dumps({"a": {"b": 1}}))

        assert "Failed to compile" in str(excinfo.value)


def test_compile_getter_complex_path():
    """Test compile_getter with a mix of attribute and item access."""
    # Test with a JSON structure
    sample_json = json.dumps({
        "users": {
            "admin": {
                "permissions": {
                    "canEdit": True
                }
            }
        }
    })

    # Create a getter for a path that will use mixed access
    getter = compile_getter("users.admin.permissions.canEdit", sample_json)

    # Create a test object with the SAME structure as the JSON
    # Since the JSON has dictionaries all the way, we need to use dictionaries
    test_obj = {
        "users": {
            "admin": {
                "permissions": {
                    "canEdit": False  # Different value to verify the getter works
                }
            }
        }
    }

    # The getter should correctly navigate the structure
    assert getter(test_obj) is False


def test_nested_getattr_primitive_container_check():
    """Test the non-container check at the beginning of nested_getattr."""
    # Create a test object with primitive values that should fail the container check
    # The key difference here is that we're setting up the test to hit the specific
    # container validation logic at the start of the function
    test_obj = {
        "num": 123,
        "bool": True,
        "float_val": 3.14
    }

    # Test with integer as intermediate segment - this should trigger the
    # initial container check, not the subscriptable check
    with pytest.raises(AttributeError) as excinfo:
        nested_getattr(test_obj, "num.something.deeper")  # Note: adding a deeper level

    # This should hit the container check, which returns a different error
    assert "non-container" in str(excinfo.value)

    # Also test with boolean and float
    with pytest.raises(AttributeError) as excinfo:
        nested_getattr(test_obj, "bool.something.more")
    assert "non-container" in str(excinfo.value)

    with pytest.raises(AttributeError) as excinfo:
        nested_getattr(test_obj, "float_val.something.more")
    assert "non-container" in str(excinfo.value)
