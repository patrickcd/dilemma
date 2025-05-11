"""
Expression language implementation using Lark
"""
import threading
from datetime import datetime

from lark import Lark, Transformer, exceptions as lark_exceptions
from lark import Token

from dilemma.lookup import lookup_variable
from dilemma.dates import DateMethods
# ruff: noqa: E501
grammar = r"""
    ?start: expr

    ?expr: or_expr

    ?or_expr: and_expr
            | or_expr "or" and_expr -> or_op

    ?and_expr: comparison
             | and_expr "and" comparison -> and_op

    ?comparison: sum
               | sum "==" sum -> eq
               | sum "!=" sum -> ne
               | sum "<" sum -> lt
               | sum ">" sum -> gt
               | sum "<=" sum -> le
               | sum ">=" sum -> ge
               | sum "in" sum -> contains
               | sum "is" "past" -> date_is_past
               | sum "is" "future" -> date_is_future
               | sum "is" "today" -> date_is_today
               | sum "within" INTEGER time_unit -> date_within
               | sum "older" "than" INTEGER time_unit -> date_older_than
               | sum "before" sum -> date_before
               | sum "after" sum -> date_after
               | sum "same_day_as" sum -> date_same_day

    ?sum: product
       | sum "+" product -> add
       | sum "-" product -> sub

    ?product: term
           | product "*" term -> mul
           | product "/" term -> div

    ?term: INTEGER -> int_number
         | FLOAT -> float_number
         | STRING -> string_literal
         | "-" INTEGER -> negative_int
         | "-" FLOAT -> negative_float
         | "True" -> true_value
         | "False" -> false_value
         | "true" -> true_value
         | "false" -> false_value
         | VARIABLE -> variable
         | "(" expr ")" -> paren

    // Define reserved keywords
    // But use string literals in rules above for "or", "and", "True", "False"
    // Use a negative lookahead in VARIABLE to exclude these as variable names
    VARIABLE: /(?!or\b|and\b|True\b|False\b|false\b|true)[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)*/
    INTEGER: /[0-9]+/
    FLOAT: /([0-9]+\.[0-9]*|\.[0-9]+)([eE][-+]?[0-9]+)?|[0-9]+[eE][-+]?[0-9]+/i
    STRING: /"(\\.|[^\\"])*"|\'(\\.|[^\\\'])*\'/

    ?time_unit: "minute" -> minute_unit
             | "minutes" -> minute_unit
             | "hour" -> hour_unit
             | "hours" -> hour_unit
             | "day" -> day_unit
             | "days" -> day_unit
             | "week" -> week_unit
             | "weeks" -> week_unit
             | "month" -> month_unit
             | "months" -> month_unit
             | "year" -> year_unit
             | "years" -> year_unit

    %import common.WS
    %ignore WS
"""


# Transformer to evaluate expressions
class ExpressionTransformer(Transformer, DateMethods):
    # Epsilon value for float comparison
    EPSILON = 1e-10

    def __init__(self, variables: dict | None = None):
        super().__init__()
        self.variables = variables if variables is not None else {}

    def int_number(self, items: list[Token]) -> int:
        return int(items[0])

    def float_number(self, items: list[Token]) -> float:
        return float(items[0])

    def negative_int(self, items: list[Token]) -> int:
        return -int(items[0])

    def negative_float(self, items: list[Token]) -> float:
        return -float(items[0])

    def true_value(self, _) -> bool:
        return True

    def false_value(self, _) -> bool:
        return False

    def variable(self, items: list[Token]) -> int | float | bool | str| list | dict | datetime:
        var_path = items[0].value
        return lookup_variable(self.variables, var_path)

    def add(self, items: list) -> float:
        return items[0] + items[1]

    def sub(self, items: list) -> float:
        return items[0] - items[1]

    def mul(self, items: list) -> float:
        return items[0] * items[1]

    def div(self, items: list) -> float:
        # Handle division by zero
        if items[1] == 0:
            raise ZeroDivisionError("Division by zero")
        return items[0] / items[1]  # Now using true division

    def paren(self, items: list) -> float:
        """Handle parenthesized expressions by returning the inner value"""
        return items[0]

    def string_literal(self, items: list[Token]) -> str:
        # Remove surrounding quotes and unescape
        return items[0][1:-1].encode('utf-8').decode('unicode_escape')

    # Comparison operations
    def eq(self, items: list) -> bool:
        if isinstance(items[0], str) or isinstance(items[1], str):
            return items[0] == items[1]
        # Handle floating point comparisons with a small epsilon
        if isinstance(items[0], float) or isinstance(items[1], float):
            return abs(items[0] - items[1]) < self.EPSILON
        return items[0] == items[1]

    def ne(self, items: list) -> bool:
        if isinstance(items[0], str) or isinstance(items[1], str):
            return items[0] != items[1]
        # Handle floating point comparisons with a small epsilon
        if isinstance(items[0], float) or isinstance(items[1], float):
            return abs(items[0] - items[1]) >= self.EPSILON
        return items[0] != items[1]

    def lt(self, items: list) -> bool:
        return items[0] < items[1]

    def gt(self, items: list) -> bool:
        return items[0] > items[1]

    def le(self, items: list[int | float]) -> bool:
        return items[0] <= items[1]

    def ge(self, items: list) -> bool:
        return items[0] >= items[1]

    # Logical operations
    def and_op(self, items: list) -> bool:
        return bool(items[0]) and bool(items[1])

    def or_op(self, items: list) -> bool:
        return bool(items[0]) or bool(items[1])

    def contains(self, items: list) -> bool:
        if isinstance(items[0], str) and isinstance(items[1], str):
            return items[0] in items[1]
        raise TypeError("'in' operator is only supported for strings")


# Thread-local storage for the parser
_thread_local = threading.local()

def build_parser() -> Lark:
    """
    Returns a thread-local instance of the Lark parser.
    Ensures thread safety by creating a separate parser for each thread.
    """
    if not hasattr(_thread_local, "parser"):
        _thread_local.parser = Lark(grammar, start="expr", parser="lalr")
    return _thread_local.parser


# Function to evaluate expressions
def evaluate(expression: str, variables: dict | None = None) -> int | float | bool | str:
    """
    Evaluate an expression with integers, arithmetic operations, comparisons,
    and variables.

    Args:
        expression: String containing the expression to evaluate
        variables: Optional dictionary of variable names to their values

    Returns:
        Result of the evaluation (integer, float, boolean, or string)
    """
    # First try to parse
    try:
        parser = build_parser()  # Use thread-local parser
        tree = parser.parse(expression)
    except Exception as e:
        # Handle parse errors
        raise ValueError(f"Invalid expression syntax: {expression}") from e

    # Then try to evaluate
    try:
        transformer = ExpressionTransformer(variables=variables)
        result = transformer.transform(tree)
        return result
    except lark_exceptions.VisitError as e:
        # Check if the underlying error is a ZeroDivisionError, NameError, or TypeError
        if isinstance(e.__context__, ZeroDivisionError):
            raise ZeroDivisionError("Division by zero") from e
        if isinstance(e.__context__, NameError):
            raise NameError(str(e.__context__)) from e
        if isinstance(e.__context__, TypeError):
            raise TypeError(str(e.__context__)) from e

        # Show the actual error rather than a generic message
        print(f"DEBUG - Original error: {type(e.__context__).__name__}: {e.__context__}")

        # Re-raise other VisitErrors with the original cause
        raise ValueError(f"Error evaluating expression: {expression} - Caused by: {type(e.__context__).__name__}: {e.__context__}") from e
