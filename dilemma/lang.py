"""
Expression language implementation using Lark
"""

import threading
import json
from datetime import datetime

from lark import Lark, Transformer, exceptions as lark_exceptions
from lark import Token

from dilemma.lookup import lookup_variable, DateTimeEncoder
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
               | sum "contains" sum -> contained_in
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
         | JQ_EXPR -> jq_expression
         | "(" expr ")" -> paren

    // Define reserved keywords
    // But use string literals in rules above for "or", "and", "True", "False"
    // Use a negative lookahead in VARIABLE to exclude these as variable names
    // Support both simple variables and slash-notation paths
    // Leading forward slash in paths is optional, e.g. both "user/name" and "/user/name" work
    VARIABLE: /(?!or\b|and\b|True\b|False\b|false\b|true\b)(([a-zA-Z][a-zA-Z0-9_]*)(\/[a-zA-Z0-9_]+)*|(\/[a-zA-Z0-9_]+)+)/

    // JQ expression syntax: <expression> - must be matched as a single token
    // Define this before the STRING token to give it higher precedence
    JQ_EXPR: /\<[^>]*\>/

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

    def __init__(self, processed_json: dict | None = None):
        super().__init__()
        self.processed_json = processed_json or {}

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

    def variable(
        self, items: list[Token]
    ) -> int | float | bool | str | list | dict | datetime:
        var_path = items[0].value
        value = lookup_variable(var_path, self.processed_json)

        # Handle datetime reconstruction
        if isinstance(value, dict) and "__datetime__" in value:
            return datetime.fromisoformat(value["__datetime__"])

        return value

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
        return items[0][1:-1].encode("utf-8").decode("unicode_escape")

    # Comparison operations
    def eq(self, items: list) -> bool:
        if isinstance(items[0], str) or isinstance(items[1], str):
            return items[0] == items[1]
        # Handle floating point comparisons with a small epsilon
        if isinstance(items[0], float) or isinstance(items[1], float):
            return abs(items[0] - items[1]) < self.EPSILON
        # Handle collections (lists, dicts)
        if isinstance(items[0], (list, dict)) or isinstance(items[1], (list, dict)):
            return items[0] == items[1]
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
        # Check if second operand (container) is a collection or string
        if isinstance(items[1], (list, tuple)):
            return items[0] in items[1]
        elif isinstance(items[1], dict):
            return items[0] in items[1]  # Check if key exists in dict
        elif isinstance(items[0], str) and isinstance(items[1], str):
            return items[0] in items[1]  # String in string
        else:
            raise TypeError(
                "'in' operator requires a collection (string, list, dict) as the right operand"
            )

    def contained_in(self, items: list) -> bool:
        # Check if first operand (container) is a collection or string
        if isinstance(items[0], (list, tuple)):
            return items[1] in items[0]
        elif isinstance(items[0], dict):
            return items[1] in items[0]  # Check if key exists in dict
        elif isinstance(items[0], str) and isinstance(items[1], str):
            return items[1] in items[0]  # String contains string
        else:
            raise TypeError(
                "'contains' operator requires a collection (string, list, dict) as the left operand"
            )

    def jq_expression(self, items: list[Token]) -> int | float | bool | str | list | dict | datetime:
        """Process a raw JQ expression to access data in the variables"""
        # Extract the JQ expression from the token: <expression> -> expression
        jq_expr = items[0].value[1:-1]  # Remove < prefix and > suffix

        # Import here to avoid circular imports
        from dilemma.lookup import evaluate_jq_expression

        # Evaluate the JQ expression against the processed JSON
        value = evaluate_jq_expression(jq_expr, self.processed_json)

        # Handle datetime reconstruction
        if isinstance(value, dict) and "__datetime__" in value:
            return datetime.fromisoformat(value["__datetime__"])

        return value


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


class CompiledExpression:
    """
    Represents a pre-compiled expression that can be evaluated multiple times
    with different variable contexts for improved performance.
    """

    def __init__(self, expression: str, parse_tree):
        self.expression = expression
        self.parse_tree = parse_tree

    def evaluate(self, variables: dict | str | None = None) -> int | float | bool | str:
        """
        Evaluate this compiled expression with the provided variables.

        Args:
            variables: Dictionary or JSON string containing variable values

        Returns:
            The result of evaluating the expression
        """
        # Use the helper function to process variables
        processed_json = _process_variables(variables)

        # Evaluate with processed JSON
        try:
            transformer = ExpressionTransformer(processed_json=processed_json)
            result = transformer.transform(self.parse_tree)
            return result
        except lark_exceptions.VisitError as e:
            # Error handling logic remains unchanged
            if isinstance(e.__context__, ZeroDivisionError):
                raise ZeroDivisionError("Division by zero") from e
            if isinstance(e.__context__, NameError):
                raise NameError(str(e.__context__)) from e
            if isinstance(e.__context__, TypeError):
                raise TypeError(str(e.__context__)) from e

            # Show the actual error rather than a generic message
            print(f"DEBUG - Original error: {type(e.__context__).__name__}: {e.__context__}")

            # Re-raise other VisitErrors with the original cause
            raise ValueError(
                f"Error evaluating expression: {self.expression} - Caused by: {type(e.__context__).__name__}: {e.__context__}"
            ) from e


# Helper function to process variables
def _process_variables(variables: dict | str | None = None) -> dict:
    """
    Process variables into a standardized JSON-compatible format.

    Args:
        variables: Dictionary or JSON string containing variable values

    Returns:
        Processed JSON object ready for expression evaluation

    Raises:
        ValueError: If the variables cannot be processed
    """
    processed_json = {}
    if variables:
        try:
            if isinstance(variables, str):
                # Parse JSON string directly
                processed_json = json.loads(variables)
            else:
                # Convert dictionary to JSON-compatible structure
                processed_json = json.loads(json.dumps(variables, cls=DateTimeEncoder))
        except (TypeError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to process variables: {e}")
    return processed_json


def compile(expression: str) -> CompiledExpression:
    """
    Compile an expression into a reusable CompiledExpression object that can be
    evaluated multiple times with different variable contexts.

    Args:
        expression: The expression string to compile

    Returns:
        A CompiledExpression object that can be evaluated with different contexts

    Raises:
        ValueError: If the expression has invalid syntax
    """
    parser = build_parser()
    try:
        tree = parser.parse(expression)
        return CompiledExpression(expression, tree)
    except lark_exceptions.UnexpectedToken as e:
        raise ValueError(f"Invalid expression syntax: {e}")
    except lark_exceptions.UnexpectedCharacters as e:
        raise ValueError(f"Invalid expression syntax: {e}")


# Function to evaluate expressions
def evaluate(expression: str, variables: dict | str | None = None) -> int | float | bool | str:
    """
    Evaluate an expression with integers, arithmetic operations, comparisons,
    and variables.

    For better performance when evaluating the same expression multiple times with
    different variable contexts, use the compile() function instead.
    """
    # Use the helper function to process variables
    processed_json = _process_variables(variables)

    # Parse the expression
    parser = build_parser()
    try:
        tree = parser.parse(expression)
    except lark_exceptions.UnexpectedToken as e:
        raise ValueError(f"Invalid expression syntax: {e}")
    except lark_exceptions.UnexpectedCharacters as e:
        raise ValueError(f"Invalid expression syntax: {e}")

    # Evaluate with processed JSON
    try:
        transformer = ExpressionTransformer(processed_json=processed_json)
        result = transformer.transform(tree)
        return result
    except lark_exceptions.VisitError as e:
        # Error handling logic remains unchanged
        if isinstance(e.__context__, ZeroDivisionError):
            raise ZeroDivisionError("Division by zero") from e
        if isinstance(e.__context__, NameError):
            raise NameError(str(e.__context__)) from e
        if isinstance(e.__context__, TypeError):
            raise TypeError(str(e.__context__)) from e

        # Show the actual error rather than a generic message
        print(f"DEBUG - Original error: {type(e.__context__).__name__}: {e.__context__}")

        # Re-raise other VisitErrors with the original cause
        raise ValueError(
            f"Error evaluating expression: {expression} - Caused by: {type(e.__context__).__name__}: {e.__context__}"
        ) from e
