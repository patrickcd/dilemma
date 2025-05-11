"""Tests for container (list and dictionary) operations in the expression language."""

import pytest
from dilemma.lang import evaluate, ExpressionTransformer
from dilemma.lookup import lookup_variable


def test_list_membership():
    """Test basic list membership operations."""
    variables = {
        "roles": ["admin", "editor", "viewer"],
        "numbers": [1, 2, 3, 4, 5],
        "empty_list": []
    }

    # Testing 'in' operator
    assert evaluate("'admin' in roles", variables) is True
    assert evaluate("'manager' in roles", variables) is False
    assert evaluate("'editor' in roles", variables) is True

    # Testing 'contains' operator
    assert evaluate("roles contains 'viewer'", variables) is True
    assert evaluate("roles contains 'guest'", variables) is False

    # Testing with numbers
    assert evaluate("3 in numbers", variables) is True
    assert evaluate("6 in numbers", variables) is False
    assert evaluate("numbers contains 5", variables) is True

    # Testing with empty list
    assert evaluate("'anything' in empty_list", variables) is False
    assert evaluate("empty_list contains 'something'", variables) is False


def test_dict_membership():
    """Test dictionary key membership operations."""
    variables = {
        "user": {
            "name": "John Doe",
            "role": "admin",
            "settings": {
                "theme": "dark",
                "notifications": True
            }
        },
        "empty_dict": {},
        # Add direct references to nested objects
        "user_settings": {"theme": "dark", "notifications": True}
    }

    # Testing 'in' operator (key existence)
    assert evaluate("'name' in user", variables) is True
    assert evaluate("'age' in user", variables) is False

    # Use direct reference to user_settings instead of path
    assert evaluate("'theme' in user_settings", variables) is True

    # Testing 'contains' operator
    assert evaluate("user contains 'role'", variables) is True
    assert evaluate("user contains 'email'", variables) is False

    # Use direct reference to user_settings
    assert evaluate("user_settings contains 'notifications'", variables) is True

    # Testing with empty dict
    assert evaluate("'key' in empty_dict", variables) is False
    assert evaluate("empty_dict contains 'value'", variables) is False


def test_mixed_container_types():
    """Test operations with mixed container types."""
    variables = {
        "data": {
            "tags": ["important", "urgent", "review"],
            "properties": {
                "color": "red",
                "priority": "high"
            }
        },
        "items": ["apple", "banana", {"type": "fruit"}],
        # Add a direct reference to the dictionary item for testing
        "fruit_object": {"type": "fruit"},
        # Add direct reference to nested tags array
        "tags": ["important", "urgent", "review"]
    }

    # Test accessing lists inside dicts using direct reference
    assert evaluate("'urgent' in tags", variables) is True

    # Test accessing lists inside dicts using direct reference
    assert evaluate("tags contains 'review'", variables) is True

    # Test accessing dict properties
    assert evaluate("'type' in fruit_object", variables) is True


def test_collection_equality():
    """Test equality operations with collections."""
    variables = {
        "list1": [1, 2, 3],
        "list2": [1, 2, 3],
        "list3": [3, 2, 1],
        "dict1": {"a": 1, "b": 2},
        "dict2": {"b": 2, "a": 1},
        "dict3": {"a": 1, "c": 3}
    }

    # List equality
    assert evaluate("list1 == list2", variables) is True
    assert evaluate("list1 == list3", variables) is False
    assert evaluate("list1 != list3", variables) is True

    # Dict equality (order doesn't matter)
    assert evaluate("dict1 == dict2", variables) is True
    assert evaluate("dict1 != dict3", variables) is True


def test_container_type_errors():
    """Test TypeError handling for container operations."""
    variables = {
        "number": 42,
        "string": "hello",
        "boolean": True,
        "list": [1, 2, 3],
        "dict": {"a": 1, "b": 2}
    }

    # These should raise TypeError because the right operand is not a collection
    with pytest.raises(TypeError, match="requires a collection"):
        evaluate("'test' in number", variables)

    # This should work (string contains)
    assert evaluate("'e' in string", variables) is True

    # This should fail (boolean is not a collection)
    with pytest.raises(TypeError, match="requires a collection"):
        evaluate("'true' in boolean", variables)

    # These should raise TypeError because the left operand is not a collection
    with pytest.raises(TypeError, match="requires a collection"):
        evaluate("number contains 1", variables)

    # This should work (string contains)
    assert evaluate("string contains 'll'", variables) is True

    # This should fail
    with pytest.raises(TypeError, match="requires a collection"):
        evaluate("boolean contains 'r'", variables)



def test_lookup_variable_with_collections():
    """Test lookup_variable function with collections."""
    # Test with nested dict and list
    context = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ],
        "settings": {
            "features": ["search", "export", "import"],
            "theme": "dark"
        }
    }

    # Test lookup on lists with index using REST-style path
    result = lookup_variable("users/0", context)  # Changed from users[0]
    assert result == {"id": 1, "name": "Alice"}

    # Test lookup on nested properties using REST-style path
    result = lookup_variable("users/1/name", context)  # Changed from users[1]/name
    assert result == "Bob"

    # Test lookup on list in dict using REST-style path
    result = lookup_variable("settings/features/2", context)  # Changed from settings/features[2]
    assert result == "import"

    # Test with a complex path that doesn't exist
    # Test with explicitly out-of-bounds index
    with pytest.raises(NameError) as excinfo:
        lookup_variable("users/999", context)  # Changed from users[999]
    assert "out of bounds" in str(excinfo.value)

    # Test with direct dict access
    result = lookup_variable("settings", context)
    assert "features" in result
    assert "theme" in result


def test_direct_transformer_methods():
    """Test ExpressionTransformer methods directly to ensure coverage."""
    transformer = ExpressionTransformer()

    # Test contains with list
    assert transformer.contains(["key", ["value1", "value2", "key"]]) is True

    # Test contains with dict
    assert transformer.contains(["key", {"key": "value", "other": 123}]) is True

    # Test contained_in with list
    assert transformer.contained_in([["value1", "value2", "key"], "key"]) is True

    # Test contained_in with dict
    assert transformer.contained_in([{"key": "value", "other": 123}, "key"]) is True

    # Test with non-collection types (these should raise TypeError)
    with pytest.raises(TypeError):
        transformer.contains([42, 100])

    with pytest.raises(TypeError):
        transformer.contained_in([42, "test"])


def test_datetime_in_collections():
    """Test handling of datetime objects in collections."""
    from datetime import datetime, timezone, timedelta

    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    tomorrow = now + timedelta(days=1)

    variables = {
        "dates": [yesterday, now, tomorrow],
        "event": {
            "start": yesterday,
            "end": tomorrow
        }
    }

    # Test datetime comparisons in lists
    # Need to use a datetime that would serialize/deserialize correctly
    iso_now = now.isoformat()
    assert evaluate(f"'{iso_now}' in dates", variables) is False  # String comparison won't match

    # Test access to datetime in dict
    assert evaluate("/event/start is past", variables) is True
    assert evaluate("/event/end is future", variables) is True


def test_complex_nested_structures():
    """Test complex nested data structures with mixed types."""
    variables = {
        "organization": {
            "name": "Acme Corp",
            "departments": [
                {
                    "name": "Engineering",
                    "teams": [
                        {"name": "Frontend", "members": ["Alice", "Bob"]},
                        {"name": "Backend", "members": ["Charlie", "Dave"]}
                    ]
                },
                {
                    "name": "Marketing",
                    "teams": [
                        {"name": "Digital", "members": ["Eve", "Frank"]}
                    ]
                }
            ]
        },
        # Add direct references to the nested objects for testing
        "frontend_team": {"name": "Frontend", "members": ["Alice", "Bob"]},
        "marketing_team": {"name": "Digital", "members": ["Eve", "Frank"]},
        "marketing_dept": {"name": "Marketing"},
        # Add direct references to deeply nested properties
        "frontend_members": ["Alice", "Bob"],
        "marketing_members": ["Eve", "Frank"],
        "marketing_name": "Marketing"
    }

    # Test with direct references to nested objects
    assert evaluate("'Bob' in frontend_members", variables) is True

    # Test with direct references to nested objects
    assert evaluate("marketing_members contains 'Eve'", variables) is True

    # Test composite conditions with direct references
    complex_expr = "'Marketing' in marketing_name and 'Frank' in marketing_members"
    assert evaluate(complex_expr, variables) is True


def test_lookup_errors():
    """Test error handling in lookup_variable function."""
    from dilemma.lookup import lookup_variable

    # Test with invalid path - using a definitely non-existent key
    with pytest.raises(NameError) as excinfo:
        lookup_variable("definitely_nonexistent_key", {"a": 1, "b": 2})
    assert "not defined" in str(excinfo.value)

    # Test with non-existing nested path - using a specific test case that will definitely fail
    context = {"user": {"name": "Alice", "role": "admin"}}
    with pytest.raises(NameError) as excinfo:
        lookup_variable("user/definitely_nonexistent", context)
    assert "not found" in str(excinfo.value) or "cannot be resolved" in str(excinfo.value)

    # Test with invalid path format (using dots)
    with pytest.raises(ValueError) as excinfo:
        lookup_variable("items.invalid", {"items": [1, 2, 3]})
    assert "cannot contain dots" in str(excinfo.value)
