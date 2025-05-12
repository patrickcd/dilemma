import pytest
from dilemma.lang import evaluate


def test_string_equality():
    test_cases = [
        ("'hello' == 'hello'", True),
        ("'hello' == 'world'", False),
        ("'test' == 'test'", True),
        ("'Test' == 'test'", False),
    ]

    for expr, expected in test_cases:
        assert evaluate(expr) == expected


def test_string_inequality():
    test_cases = [
        ("'hello' != 'world'", True),
        ("'hello' != 'hello'", False),
        ("'test' != 'Test'", True),
        ("'Test' != 'Test'", False),
    ]

    for expr, expected in test_cases:
        assert evaluate(expr) == expected


def test_string_contains():
    test_cases = [
        ("'hello' in 'hello world'", True),
        ("'world' in 'hello world'", True),
        ("'test' in 'testing'", True),
        ("'Test' in 'testing'", False),
    ]

    for expr, expected in test_cases:
        assert evaluate(expr) == expected


def test_string_comparison_with_arithmetic():
    with pytest.raises(TypeError):
        evaluate("'hello' + 5")
    with pytest.raises(TypeError):
        evaluate("5 + 'hello'")


def test_invalid_contains_operation():
    with pytest.raises(TypeError, match="'in' operator requires a collection"):
        evaluate("5 in 10")
    with pytest.raises(TypeError, match="'in' operator requires a collection"):
        evaluate("5 in 'hello'")
