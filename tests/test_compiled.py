import json
from dilemma.compiled import create_optimized_evaluator, extract_variable_paths
from dilemma.lang import parser


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