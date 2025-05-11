from datetime import datetime, timezone, timedelta

import pytest
from hypothesis import given, strategies as st

from dilemma.lang import evaluate
from dilemma.lookup import lookup_variable
import jq


# --- Tests to cover missing branches in dilemma/lang.py ---

def test_lang_paren_expression():
    """
    Test parenthesized expressions to exercise the grammar's paren rule.
    (Covers missing lines in lang.py, e.g. handling of "( expr )")
    """
    # Simple arithmetic expression in parentheses
    result = evaluate("(2 + 3) * 4", {})
    assert result == 20

def test_lang_nested_arithmetic():
    """
    Test a complex nested arithmetic expression that uses multiple grammar branches.
    """
    # This forces use of the addition, subtraction, multiplication, and paren rules.
    result = evaluate("((10 - 3) * 2) + 5", {})
    expected = ((10 - 3) * 2) + 5
    assert result == expected

# --- Tests to cover missing branches in dilemma/lookup.py ---

def test_lookup_returns_datetime():
    """
    Test that lookup_variable reconstructs datetime objects correctly.
    This ensures the __datetime__ branch is covered.
    """
    dt = datetime(2025, 5, 11, 14, 30, tzinfo=timezone.utc)
    context = {"event": dt}
    result = lookup_variable(context, "event")
    assert isinstance(result, datetime)
    # Compare ISO strings to account for potential microsecond differences.
    assert result.isoformat() == dt.isoformat()

def test_lookup_error_nonexistent_path():
    """
    Test that lookup_variable raises a NameError when the requested path does not exist.
    Covers branch where jq returns an empty result.
    """
    context = {"a": {"b": 123}}
    with pytest.raises(NameError, match="Variable 'a.x' is not defined"):
        lookup_variable(context, "a.x")


def test_lookup_null_result_for_key():
    """
    Test that lookup_variable raises NameError when the JSON conversion
    of a defined key produces a null result.
    In this case, context contains a key with a value of None.
    """
    context = {"a": {"x": None}}
    # "a.x" is defined in Python, but json.dumps will convert None to null,
    # causing jq to return [None] and thus triggering the error branch.
    with pytest.raises(NameError, match="Variable 'a.x' is not defined"):
        lookup_variable(context, "a.x")



def test_lookup_top_level_variable():
    """
    Test the optimization for top-level variables in lookup_variable.
    Covers line 21: `if "." not in path and path in obj:`.
    """
    context = {"a": 42}
    result = lookup_variable(context, "a")
    assert result == 42

def test_lookup_top_level_variable_no_dot():
    """
    Test the optimization for top-level variables in lookup_variable.
    Covers line 21: `if "." not in path and path in obj:`.
    """
    context = {"simple_key": "simple_value"}
    result = lookup_variable(context, "simple_key")
    assert result == "simple_value"

def test_lookup_null_result():
    """
    Test that lookup_variable returns None when the value in the context is None.
    """
    context = {"a": None}
    result = lookup_variable(context, "a")
    assert result is None


# Strategy for generating valid variable names (alphanumeric, starting with
# a letter or underscore)
# Exclude "or" and "and" as they are now reserved keywords.
variable_names_st = st.from_regex(r"[a-zA-Z_][a-zA-Z0-9_]*", fullmatch=True).filter(
    lambda x: x not in ["or", "and"]
)

# Strategy for generating simple values (integers, floats, booleans)
simple_values_st = st.one_of(
    st.integers(), st.floats(allow_nan=False, allow_infinity=False), st.booleans()
)


@given(var_name=variable_names_st, value=simple_values_st)
def test_evaluate_single_variable(var_name, value):
    """Test evaluating an expression that is just a single variable."""
    expression = var_name
    variables = {var_name: value}
    if (
        isinstance(value, float) and abs(value) < 1e-9
    ):  # Handle potential precision issues with zero floats
        assert abs(evaluate(expression, variables) - value) < 1e-9
    else:
        assert evaluate(expression, variables) == value


@given(var_name=variable_names_st, value=st.integers())
def test_evaluate_variable_as_integer(var_name, value):
    """Test that a variable holding an integer is evaluated correctly."""
    expression = var_name
    variables = {var_name: value}
    result = evaluate(expression, variables)
    assert isinstance(result, int)
    assert result == value


@given(var_name=variable_names_st, value=st.floats(allow_nan=False, allow_infinity=False))
def test_evaluate_variable_as_float(var_name, value):
    """Test that a variable holding a float is evaluated correctly."""
    expression = var_name
    variables = {var_name: value}
    result = evaluate(expression, variables)
    assert isinstance(result, float)
    if abs(value) < 1e-9:  # Handle potential precision issues with zero floats
        assert abs(result - value) < 1e-9
    else:
        assert result == pytest.approx(value)


@given(var_name=variable_names_st, value=st.booleans())
def test_evaluate_variable_as_boolean(var_name, value):
    """Test that a variable holding a boolean is evaluated correctly."""
    # Note: Booleans are not directly part of the grammar as literals,
    # but can be results of comparisons or stored in variables.
    # Here, we are testing if a variable *can hold* a boolean value
    # and if that value is returned correctly.
    expression = var_name
    variables = {var_name: value}
    result = evaluate(expression, variables)
    # Booleans are numbers in some contexts (0 or 1), ensure strict bool type if
    # that's the intent. For now, if value is bool, result should be bool.
    assert isinstance(result, bool)
    assert result == value


@given(var_name=variable_names_st)
def test_evaluate_undefined_variable(var_name):
    """Test that evaluating an undefined variable raises a NameError."""
    expression = var_name
    with pytest.raises(NameError, match=f"Variable '{var_name}' is not defined."):
        evaluate(expression, {})  # Empty variables dictionary


@given(var_name=variable_names_st, defined_value=simple_values_st)
def test_evaluate_variable_among_others(var_name, defined_value):
    """Test evaluating a variable when other variables are also defined."""
    expression = var_name
    variables = {var_name: defined_value, "another_var": 123, "yet_another": 45.6}
    if isinstance(defined_value, float) and abs(defined_value) < 1e-9:
        assert abs(evaluate(expression, variables) - defined_value) < 1e-9
    else:
        assert evaluate(expression, variables) == defined_value


def test_evaluate_variable_case_sensitive():
    """Test that variable names are case-sensitive."""
    variables = {"myVar": 10, "myvar": 20}
    assert evaluate("myVar", variables) == 10
    assert evaluate("myvar", variables) == 20
    with pytest.raises(NameError, match="Variable 'MYVAR' is not defined."):
        evaluate("MYVAR", variables)


@given(var_name=st.sampled_from(["or", "and"]))  # Actual reserved keywords
def test_evaluate_reserved_keyword_as_variable_name_fails_parsing(var_name):
    """
    Test that using an actual reserved keyword ("or", "and") as if it were a
    variable name causes a parse error (ValueError).
    """
    with pytest.raises(ValueError):  # Expecting a parse error from Lark
        evaluate(var_name, {var_name: 1})


@given(
    var_name=st.sampled_from(["if", "else", "then", "MyVar"]), value=simple_values_st
)  # Non-reserved strings
def test_evaluate_non_keyword_strings_as_variable_names(var_name, value):
    """
    Test that strings that resemble keywords but are not reserved (e.g., "if", "else")
    can be used as valid variable names.
    """
    expression = var_name
    variables = {var_name: value}
    if isinstance(value, float) and abs(value) < 1e-9:
        assert abs(evaluate(expression, variables) - value) < 1e-9
    else:
        assert evaluate(expression, variables) == value


@given(var_name=variable_names_st)  # Uses the updated strategy that excludes "or", "and"
def test_evaluate_undefined_variable_with_valid_name(var_name):
    """Test NameError for valid (non-reserved) but undefined variable names."""
    # The filter `lambda x: x not in ["or", "and"]` is no longer needed here
    # because variable_names_st already excludes them.
    with pytest.raises(NameError, match=f"Variable '{var_name}' is not defined."):
        evaluate(var_name, {})

