import pytest
from dilemma.lang import evaluate, ExpressionTransformer


def test_specific_cases():
    """Test specific edge cases"""
    test_cases = [
        # Basic integers
        ("0", 0),
        ("1", 1),
        ("42", 42),
        # Addition
        ("1 + 2", 3.0),
        ("5 + 10", 15.0),
        ("0 + 0", 0.0),
        # Subtraction
        ("5 - 2", 3.0),
        ("10 - 5", 5.0),
        ("10 - 5 + 3", 8.0),
        ("1 + 2 + 3", 6.0),
        ("10 - 5 - 3", 2.0),
        # Multiplication tests
        ("3 * 4", 12.0),
        ("0 * 5", 0.0),
        ("5 * 0", 0.0),
        ("1 * 42", 42.0),
        # Division tests
        ("10 / 2", 5.0),
        ("9 / 3", 3.0),
        ("8 / 4", 2.0),
        ("7 / 2", 3.5),  # Float division
        ("100 / 1", 100.0),
        # Combined operations with precedence
        ("2 + 3 * 4", 14.0),
        ("2 * 3 + 4", 10.0),
        ("10 - 2 * 3", 4.0),
        ("10 / 2 + 3", 8.0),
        ("10 + 20 / 5", 14.0),
        ("10 * 2 / 4", 5.0),
        ("20 / 4 * 2", 10.0),
        # Complex expressions
        ("1 + 2 * 3 + 4", 11.0),
        ("10 / 2 + 3 * 4", 17.0),
        ("1 + 2 + 3 * 4", 15.0),
    ]

    for expr, expected in test_cases:
        assert evaluate(expr) == expected


def test_division_by_zero():
    """Test that division by zero raises an error"""
    with pytest.raises(ZeroDivisionError):
        evaluate("5 / 0")


# Add a test for triggering other VisitErrors
class CustomTransformer(ExpressionTransformer):
    def mul(self, items):
        # Intentionally raise a custom error for testing
        raise ValueError("Custom error for testing")


def test_other_visit_errors(monkeypatch):
    """Test that other VisitErrors are properly handled"""
    import dilemma.lang

    # Create an instance of our custom transformer
    custom_transformer = CustomTransformer()

    # Keep the original function to restore later
    original_transform = dilemma.lang.ExpressionTransformer.transform

    # Replace the transform method on the ExpressionTransformer class
    def mock_transform(self, tree):
        if self.__class__ == dilemma.lang.ExpressionTransformer:
            return custom_transformer.transform(tree)
        return original_transform(self, tree)

    # Apply the monkeypatch to the class method
    monkeypatch.setattr(dilemma.lang.ExpressionTransformer, "transform", mock_transform)

    with pytest.raises(ValueError) as excinfo:
        evaluate("3 * 4")

    # Check that the error message contains the expression
    assert "3 * 4" in str(excinfo.value)


def test_invalid_syntax():
    """Test that invalid syntax raises an appropriate error"""
    with pytest.raises(ValueError) as excinfo:
        evaluate("2 + * 3")
    assert "Invalid expression syntax" in str(excinfo.value)


# Add test for syntax errors
def test_invalid_characters():
    """Test that invalid characters raise an appropriate error"""
    with pytest.raises(ValueError) as excinfo:
        evaluate("2 + 3 $ 4")
    assert "Invalid expression syntax" in str(excinfo.value)


def test_comparison_operators():
    """Test comparison operators"""
    test_cases = [
        # Equality
        ("5 == 5", True),
        ("5 == 6", False),
        ("10 == 10", True),
        # Inequality
        ("5 != 5", False),
        ("5 != 6", True),
        ("10 != 20", True),
        # Less than
        ("5 < 10", True),
        ("10 < 5", False),
        ("5 < 5", False),
        # Greater than
        ("10 > 5", True),
        ("5 > 10", False),
        ("5 > 5", False),
        # Less than or equal
        ("5 <= 10", True),
        ("10 <= 5", False),
        ("5 <= 5", True),
        # Greater than or equal
        ("10 >= 5", True),
        ("5 >= 10", False),
        ("5 >= 5", True),
    ]

    for expr, expected in test_cases:
        assert evaluate(expr) == expected


def test_comparison_with_arithmetic():
    """Test comparison operators combined with arithmetic operations"""
    test_cases = [
        # Arithmetic on both sides
        ("2 + 3 == 5", True),
        ("2 + 3 == 6", False),
        ("10 - 5 != 3", True),
        # With operator precedence
        ("2 + 3 * 2 == 8", True),
        ("2 + 3 * 2 != 11", True),
        ("10 - 2 * 3 < 5", True),  # 10 - 6 = 4.0, and 4.0 < 5 is True
        ("10 - 2 * 3 <= 4", True),  # 10 - 6 = 4.0, and 4.0 <= 4 is True
        # With division
        ("10 / 2 == 5", True),
        ("7 / 2 == 3.5", True),  # Float division
        ("20 / 4 > 3", True),
        ("20 / 4 < 6", True),
    ]

    for expr, expected in test_cases:
        assert evaluate(expr) == expected
