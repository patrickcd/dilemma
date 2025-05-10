import json
import pytest
from dilemma.compiled import create_optimized_evaluator, extract_variable_paths
from dilemma.lang import build_parser
from dilemma.lookup import compile_getter


def test_basic_optimization():
    """Test that the optimized evaluator produces the same results as the regular evaluator."""
    # Sample expression
    expression = "a.b + c.d * 2"

    # Sample data structure in JSON format
    sample_json = json.dumps({
        "a": {"b": 10},
        "c": {"d": 5}
    })

    # Create optimized evaluator
    optimized_eval = create_optimized_evaluator(expression, sample_json)

    # Test data
    test_data = {
        "a": {"b": 10},
        "c": {"d": 5}
    }

    # Expected result: a.b + c.d * 2 = 10 + 5 * 2 = 20
    expected = 20

    # Evaluate with optimized evaluator
    result = optimized_eval(test_data)

    assert result == expected


def test_nested_path_optimization():
    """Test optimization with deeply nested paths."""
    expression = "user.profile.settings.notifications.enabled"

    sample_json = json.dumps({
        "user": {
            "profile": {
                "settings": {
                    "notifications": {
                        "enabled": True
                    }
                }
            }
        }
    })

    optimized_eval = create_optimized_evaluator(expression, sample_json)

    test_data = {
        "user": {
            "profile": {
                "settings": {
                    "notifications": {
                        "enabled": False
                    }
                }
            }
        }
    }

    result = optimized_eval(test_data)
    assert result is False


def test_extract_variable_paths():
    """Test that variable paths are correctly extracted from expressions."""
    expression = "a.b + c.d * (e.f - 10)"
    parser = build_parser()
    tree = parser.parse(expression)

    paths = extract_variable_paths(tree)

    assert set(paths) == {"a.b", "c.d", "e.f"}


def test_fallback_to_standard():
    """Test that optimized evaluator falls back to standard evaluation when paths change."""
    expression = "data.value * 2"

    sample_json = json.dumps({
        "data": {"value": 5}
    })

    optimized_eval = create_optimized_evaluator(expression, sample_json)

    # Test with different structure but same result
    test_data = {
        "data": {"value": 10}
    }

    result = optimized_eval(test_data)
    assert result == 20

    # Test with attribute access instead of dictionary
    class Data:
        def __init__(self, value):
            self.value = value

    test_data2 = {"data": Data(15)}
    result2 = optimized_eval(test_data2)
    assert result2 == 30


def test_optimization_performance():
    """Simple test to verify optimization provides performance benefit."""
    import time

    # Create a more complex expression with many variable references
    expression = "a.x + a.y + a.z + b.x + b.y + b.z"

    sample_json = json.dumps({
        "a": {"x": 1, "y": 2, "z": 3},
        "b": {"x": 4, "y": 5, "z": 6}
    })

    # Create both standard and optimized evaluators
    optimized_eval = create_optimized_evaluator(expression, sample_json)
    standard_eval = create_optimized_evaluator(expression, None)  # No optimization

    test_data = {
        "a": {"x": 1, "y": 2, "z": 3},
        "b": {"x": 4, "y": 5, "z": 6}
    }

    # Run standard evaluation many times
    start = time.time()
    for _ in range(1000):
        standard_eval(test_data)
    standard_time = time.time() - start

    # Run optimized evaluation many times
    start = time.time()
    for _ in range(1000):
        optimized_eval(test_data)
    optimized_time = time.time() - start

    # Optimized should be faster, but we don't assert exact times
    # as it depends on the machine
    assert optimized_time < standard_time

    # Just print the performance improvement for information
    print(f"Standard: {standard_time:.6f}s, Optimized: {optimized_time:.6f}s")
    print(f"Speedup: {standard_time/optimized_time:.2f}x")


def test_comprehensive_performance_comparison():
    """Compare performance of standard, optimized, and direct evaluation approaches."""
    import time
    from dilemma.lang import evaluate

    # Create a more complex expression with many variable references
    expression = "a.x + a.y + a.z + b.x + b.y + b.z"

    sample_json = json.dumps({
        "a": {"x": 1, "y": 2, "z": 3},
        "b": {"x": 4, "y": 5, "z": 6}
    })

    test_data = {
        "a": {"x": 1, "y": 2, "z": 3},
        "b": {"x": 4, "y": 5, "z": 6}
    }

    # Create both standard (pre-parsed) and optimized evaluators
    optimized_eval = create_optimized_evaluator(expression, sample_json)
    standard_eval = create_optimized_evaluator(expression, None)  # No optimization

    # Direct evaluation using lang.evaluate (which parses each time)
    def direct_eval(data):
        return evaluate(expression, data)

    # Run direct evaluation many times
    start = time.time()
    for _ in range(1000):
        direct_eval(test_data)
    direct_time = time.time() - start

    # Run standard evaluation many times
    start = time.time()
    for _ in range(1000):
        standard_eval(test_data)
    standard_time = time.time() - start

    # Run optimized evaluation many times
    start = time.time()
    for _ in range(1000):
        optimized_eval(test_data)
    optimized_time = time.time() - start

    # Verify all approaches yield the same result (21)
    assert direct_eval(test_data) == 21
    assert standard_eval(test_data) == 21
    assert optimized_eval(test_data) == 21

    # Print performance comparison
    print("\nComprehensive Performance Comparison:")
    print(f"Direct evaluation (lang.evaluate): {direct_time:.6f}s")
    print(f"Standard pre-parsed:              {standard_time:.6f}s")
    print(f"Optimized pre-parsed:             {optimized_time:.6f}s")

    print(f"\nSpeedup ratios:")
    print(f"Standard vs Direct:    {direct_time/standard_time:.2f}x")
    print(f"Optimized vs Direct:   {direct_time/optimized_time:.2f}x")
    print(f"Optimized vs Standard: {standard_time/optimized_time:.2f}x")

    # We expect direct evaluation to be slowest due to parsing overhead
    print("\nNote: Direct evaluation parses the expression on every call.")
    print("Pre-parsing provides significant performance benefits for repeated evaluations.")

def test_compile_getter_invalid_json():
    """Test compile_getter with invalid JSON."""
    with pytest.raises(ValueError) as excinfo:
        compile_getter("a.b", "{invalid_json")

    assert "Invalid JSON" in str(excinfo.value)


def test_compile_getter_missing_key():
    """Test compile_getter with a key that doesn't exist in the JSON data."""
    with pytest.raises(ValueError) as excinfo:
        compile_getter("a.missing", json.dumps({"a": {"b": 1}}))

    assert "not found" in str(excinfo.value)


def test_compile_getter_complex_structure():
    """Test compile_getter with a more complex nested structure."""
    sample_json = json.dumps({
        "users": [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ],
        "settings": {
            "theme": "dark",
            "notifications": {
                "email": True,
                "sms": False
            }
        }
    })

    # Test item access with a complex path
    getter = compile_getter("settings.notifications.email", sample_json)

    test_data = {
        "settings": {
            "notifications": {
                "email": True
            }
        }
    }

    assert getter(test_data) is True


def test_compile_getter_eval_failure():
    """Test compile_getter with an invalid expression that fails during eval."""
    # Create a situation where the expression can't be compiled
    # This requires mocking or monkeypatching to force eval to fail
    import unittest.mock

    with unittest.mock.patch('dilemma.lookup.eval') as mock_eval:
        mock_eval.side_effect = SyntaxError("Invalid syntax")

        with pytest.raises(ValueError) as excinfo:
            compile_getter("a.b", json.dumps({"a": {"b": 1}}))

        assert "Failed to compile" in str(excinfo.value)


def test_optimized_evaluator_exception_handling():
    """Test that create_optimized_evaluator handles exceptions during getter compilation."""
    # Create a patch that will make compile_getter raise an exception for one path but not others
    import unittest.mock

    # We'll use a side effect function that raises exception only for specific paths
    def side_effect(path, json_str):
        if path == "b.value":
            raise ValueError("Test exception")
        # For other paths, call the original function
        return original_compile_getter(path, json_str)

    # Create the expression and sample data
    expression = "a.value + b.value + c.value"
    sample_json = json.dumps({
        "a": {"value": 1},
        "b": {"value": 2},
        "c": {"value": 3}
    })

    # Apply the patch
    with unittest.mock.patch('dilemma.compiled.compile_getter') as mock_compile:
        # Save the original function
        original_compile_getter = compile_getter
        # Set the side effect
        mock_compile.side_effect = side_effect

        # Create optimized evaluator - should succeed despite the exception for b.value
        evaluator = create_optimized_evaluator(expression, sample_json)

        # Test that it works - b.value should use standard lookup since optimization failed
        test_data = {
            "a": {"value": 10},
            "b": {"value": 20},
            "c": {"value": 30}
        }

        result = evaluator(test_data)
        assert result == 60  # 10 + 20 + 30

    # Verify the mock was called for all three paths
    assert mock_compile.call_count >= 3


def test_extract_variable_paths_edge_cases():
    """Test extract_variable_paths function with various node types."""
    from lark import Tree, Token

    # Create a tree with a mix of regular nodes, tokens, and other structures
    # This tree contains a non-tree child (a token directly) which should exercise
    # the branch where a child doesn't have a 'data' attribute
    tree = Tree('expr', [
        Tree('variable', [Token('VARIABLE', 'a.b')]),
        Token('OPERATOR', '+'),  # This token is directly in children, not in a subtree
        Tree('variable', [Token('VARIABLE', 'c.d')])
    ])

    # Extract paths from this tree
    paths = extract_variable_paths(tree)

    # Check that we got the correct paths despite the unusual tree structure
    assert set(paths) == {"a.b", "c.d"}

    # Also test with a completely different type of object to ensure robustness
    class CustomNode:
        def __init__(self, data=None, children=None, value=None):
            self.data = data
            self.children = children or []
            self.value = value

    # Create a custom structure that mimics a Tree but isn't one
    custom_tree = CustomNode('expr', [
        CustomNode('variable', [CustomNode(children=[CustomNode(value='x.y')])]),
        CustomNode('variable', [CustomNode(value='z.w')])
    ])

    # Extract should handle this gracefully, even if it doesn't extract anything
    custom_paths = extract_variable_paths(custom_tree)
    assert isinstance(custom_paths, list)  # Should return a list, even if empty


def test_extract_variable_paths_no_token_value():
    """Test extract_variable_paths with a variable node where token has no value."""
    from lark import Tree, Token

    # Create a class that mimics a token but has no value attribute
    class NoValueToken:
        def __init__(self):
            # Intentionally no value attribute
            pass

    # Create a variable node with this token
    var_node = Tree('variable', [NoValueToken()])

    # Put it in a tree
    tree = Tree('expr', [
        var_node,
        Tree('variable', [Token('VARIABLE', 'x.y')])
    ])

    # This should execute the branch where hasattr(token, "value") is False
    paths = extract_variable_paths(tree)

    # Should only include the valid path
    assert set(paths) == {"x.y"}


def test_extract_variable_paths_with_non_iterable_children():
    """Test extract_variable_paths with a node whose children attribute is not iterable."""
    from lark import Tree, Token

    # Create a class with a children property that raises TypeError when converted to list
    class NonIterableChildrenNode:
        def __init__(self):
            self.data = "not_variable"

        @property
        def children(self):
            # This is a property that returns a non-iterable object
            return 123  # An integer is not iterable, will raise TypeError

    # Create a tree with this problematic node
    tree = Tree('expr', [
        Tree('variable', [Token('VARIABLE', 'a.b')]),
        NonIterableChildrenNode(),  # This will cause TypeError in _get_node_children
        Tree('variable', [Token('VARIABLE', 'c.d')])
    ])

    # The function should handle this gracefully
    paths = extract_variable_paths(tree)

    # It should still extract the valid paths
    assert set(paths) == {"a.b", "c.d"}


def test_dunder_vars():
    with pytest.raises(ValueError):
        compile_getter("__class__", None)