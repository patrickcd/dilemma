import pytest
from hypothesis import given, strategies as st
from dilemma.lang import evaluate

# Strategy for generating integers including negative numbers
integers_st = st.integers(min_value=-100, max_value=1000)

# Strategy for generating simple expressions with integers
@st.composite
def integer_expressions(draw):
    """Generate a simple integer expression and its expected result"""
    number = draw(integers_st)
    return str(number), number

# Strategy for generating addition expressions
@st.composite
def addition_expressions(draw):
    """Generate an addition expression and its expected result"""
    left = draw(integers_st)
    right = draw(integers_st)
    expr = f"{left} + {right}"
    expected = left + right
    return expr, expected

# Strategy for generating subtraction expressions
@st.composite
def subtraction_expressions(draw):
    """Generate a subtraction expression and its expected result"""
    left = draw(integers_st)
    right = draw(integers_st)
    expr = f"{left} - {right}"
    expected = left - right
    return expr, expected

# Strategy for generating multiplication expressions
@st.composite
def multiplication_expressions(draw):
    """Generate a multiplication expression and its expected result"""
    left = draw(integers_st)
    right = draw(integers_st)
    expr = f"{left} * {right}"
    expected = left * right
    return expr, expected

# Strategy for generating division expressions
@st.composite
def division_expressions(draw):
    """Generate a division expression and its expected result"""
    left = draw(integers_st)
    # Ensure we don't divide by zero
    right = draw(st.integers(min_value=1, max_value=100))
    expr = f"{left} / {right}"
    # Use integer division to match our implementation
    expected = left // right
    return expr, expected

# Strategy for generating complex expressions with multiple operations
@st.composite
def complex_expressions(draw):
    """Generate a complex expression with multiple operations and its expected result"""
    # Start with a single number
    expr = str(draw(integers_st))

    # Add 1-4 operations
    num_operations = draw(st.integers(min_value=1, max_value=4))

    for _ in range(num_operations):
        # Choose operation (avoid division if it might cause errors)
        if expr.endswith('0'):
            # Avoid potential division by zero
            operation = draw(st.sampled_from(["+", "-", "*"]))
        else:
            operation = draw(st.sampled_from(["+", "-", "*", "/"]))

        # For division, ensure non-zero divisor
        if operation == "/":
            operand = draw(st.integers(min_value=1, max_value=20))
        else:
            operand = draw(integers_st)

        # Update expression
        expr = f"{expr} {operation} {operand}"

    # Replace Python's normal division with integer division
    # to match our implementation
    expr_for_eval = expr.replace('/', '//')
    expected = eval(expr_for_eval)

    return expr, expected

# Strategy for generating various whitespace variations
@st.composite
def whitespace_variations(draw):
    """Generate expressions with varied whitespace"""
    base_expr, expected = draw(st.one_of(
        integer_expressions(),
        addition_expressions(),
        subtraction_expressions(),
        multiplication_expressions(),  # Added multiplication
        division_expressions()         # Added division
    ))

    # Create variations with different whitespace
    whitespace = draw(st.text(alphabet=" \t", min_size=0, max_size=3))

    # For simple integers, just add whitespace around
    if all(op not in base_expr for op in ["+", "-", "*", "/"]):
        return f"{whitespace}{base_expr}{whitespace}", expected

    # For operations, modify the whitespace around operators
    for op in ["+", "-", "*", "/"]:
        if op in base_expr:
            left, right = base_expr.split(op, 1)  # Split on first occurrence
            return f"{left.strip()}{whitespace}{op}{whitespace}{right.strip()}", expected

    return base_expr, expected  # Fallback

@given(integer_expressions())
def test_integer_expressions(expr_tuple):
    """Test that integer expressions are evaluated correctly"""
    expr, expected = expr_tuple
    assert evaluate(expr) == expected

@given(addition_expressions())
def test_addition(expr_tuple):
    """Test that addition expressions are evaluated correctly"""
    expr, expected = expr_tuple
    assert evaluate(expr) == expected

@given(subtraction_expressions())
def test_subtraction(expr_tuple):
    """Test that subtraction expressions are evaluated correctly"""
    expr, expected = expr_tuple
    assert evaluate(expr) == expected

@given(multiplication_expressions())
def test_multiplication(expr_tuple):
    """Test that multiplication expressions are evaluated correctly"""
    expr, expected = expr_tuple
    assert evaluate(expr) == expected

@given(division_expressions())
def test_division(expr_tuple):
    """Test that division expressions are evaluated correctly"""
    expr, expected = expr_tuple
    assert evaluate(expr) == expected

@given(complex_expressions())
def test_complex_expressions(expr_tuple):
    """Test that complex expressions with multiple operations are evaluated correctly"""
    expr, expected = expr_tuple
    assert evaluate(expr) == expected

@given(whitespace_variations())
def test_whitespace_handling(expr_tuple):
    """Test that expressions with varied whitespace are handled correctly"""
    expr, expected = expr_tuple
    assert evaluate(expr) == expected

# Test for operation precedence
@given(st.integers(0, 100), st.integers(0, 100), st.integers(0, 100))
def test_operation_precedence(a, b, c):
    """Test that operations are evaluated from left to right"""
    # (a + b) - c
    expr = f"{a} + {b} - {c}"
    expected = (a + b) - c
    assert evaluate(expr) == expected

    # (a - b) + c
    expr = f"{a} - {b} + {c}"
    expected = (a - b) + c
    assert evaluate(expr) == expected

# Test for operation precedence with multiplication
@given(st.integers(0, 20), st.integers(0, 20), st.integers(0, 20))
def test_multiplication_precedence(a, b, c):
    """Test that multiplication has higher precedence than addition/subtraction"""
    # a + b * c should be a + (b * c)
    expr = f"{a} + {b} * {c}"
    expected = a + (b * c)
    assert evaluate(expr) == expected

    # a - b * c should be a - (b * c)
    expr = f"{a} - {b} * {c}"
    expected = a - (b * c)
    assert evaluate(expr) == expected

    # a * b + c should be (a * b) + c
    expr = f"{a} * {b} + {c}"
    expected = (a * b) + c
    assert evaluate(expr) == expected

    # a * b - c should be (a * b) - c
    expr = f"{a} * {b} - {c}"
    expected = (a * b) - c
    assert evaluate(expr) == expected

# Test for operation precedence with division
@given(st.integers(0, 20), st.integers(1, 20), st.integers(1, 20))
def test_division_precedence(a, b, c):
    """Test that division has higher precedence than addition/subtraction"""
    # a + b / c should be a + (b / c)
    expr = f"{a} + {b} / {c}"
    expected = a + (b // c)
    assert evaluate(expr) == expected

    # a - b / c should be a - (b / c)
    expr = f"{a} - {b} / {c}"
    expected = a - (b // c)
    assert evaluate(expr) == expected

    # a / b + c should be (a / b) + c
    expr = f"{a} / {b} + {c}"
    expected = (a // b) + c
    assert evaluate(expr) == expected

    # a / b - c should be (a / b) - c
    expr = f"{a} / {b} - {c}"
    expected = (a // b) - c
    assert evaluate(expr) == expected

    # a * b / c should be (a * b) / c
    expr = f"{a} * {b} / {c}"
    expected = (a * b) // c
    assert evaluate(expr) == expected

    # a / b * c should be (a / b) * c
    expr = f"{a} / {b} * {c}"
    expected = (a // b) * c
    assert evaluate(expr) == expected

# Add a hypothesis test for division by zero
@given(st.integers(min_value=1, max_value=1000))
def test_hypothesis_division_by_zero(numerator):
    """Test that division by zero always raises a ZeroDivisionError"""
    expr = f"{numerator} / 0"
    with pytest.raises(ZeroDivisionError):
        evaluate(expr)

# Test boundary conditions with large integers
@given(st.integers(min_value=10000, max_value=1000000),
       st.integers(min_value=10000, max_value=1000000))
def test_large_integers(a, b):
    """Test expressions with very large integers"""
    # Addition with large integers
    expr = f"{a} + {b}"
    assert evaluate(expr) == a + b

    # Subtraction with large integers
    expr = f"{a} - {b}"
    assert evaluate(expr) == a - b

    # Multiplication with large integers (if not too large to cause overflow)
    if a < 10000 and b < 10000:
        expr = f"{a} * {b}"
        assert evaluate(expr) == a * b

# Test expressions with many operations
@given(st.lists(st.integers(min_value=1, max_value=20), min_size=5, max_size=10))
def test_many_operations(numbers):
    """Test expressions with many operations in sequence"""
    # Build an expression with alternating operations
    expr = str(numbers[0])

    for i, num in enumerate(numbers[1:]):
        if i % 3 == 0:
            expr += f" + {num}"
        elif i % 3 == 1:
            expr += f" - {num}"
        else:
            expr += f" * {num}"

    # Calculate expected result using Python's eval to handle precedence correctly
    expr_for_eval = expr.replace('/', '//')
    expected = eval(expr_for_eval)

    assert evaluate(expr) == expected

# Test with negative numbers
@given(st.integers(min_value=-100, max_value=-1),
       st.integers(min_value=-100, max_value=-1))
def test_negative_numbers(a, b):
    """Test expressions with negative numbers"""
    # Addition with negative numbers
    expr = f"{a} + {b}"
    assert evaluate(expr) == a + b

    # Subtraction with negative numbers
    expr = f"{a} - {b}"
    assert evaluate(expr) == a - b

    # Multiplication with negative numbers
    expr = f"{a} * {b}"
    assert evaluate(expr) == a * b

    # Division with negative numbers (avoiding division by zero)
    if b != 0:
        expr = f"{a} / {b}"
        assert evaluate(expr) == a // b

# Add a comment explaining the use of eval() for test expectations
"""
NOTE: This test suite uses Python's eval() function to calculate expected results for tests.
This is safe in this context because:
1. eval() is only used in the test code, not in the actual implementation
2. The expressions being evaluated are generated by the test code, not from external input
3. The expressions are limited to simple arithmetic operations and integers

The main implementation in dilemma.lang uses a proper grammar-based parser for security.
"""
