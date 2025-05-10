"""
Expression language implementation using Lark
"""

from lark import Lark, Transformer, exceptions as lark_exceptions
from lark import Token

# Define the grammar for our simple expression language
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

    ?sum: product
       | sum "+" product -> add
       | sum "-" product -> sub

    ?product: term
           | product "*" term -> mul
           | product "/" term -> div

    ?term: INTEGER -> int_number
         | FLOAT -> float_number
         | "-" INTEGER -> negative_int
         | "-" FLOAT -> negative_float
         | "(" expr ")" -> paren

    INTEGER: /[0-9]+/
    FLOAT: /([0-9]+\.[0-9]*|\.[0-9]+)([eE][-+]?[0-9]+)?|[0-9]+[eE][-+]?[0-9]+/i

    %import common.WS
    %ignore WS
"""


# Transformer to evaluate expressions
class ExpressionTransformer(Transformer):
    # Epsilon value for float comparison
    EPSILON = 1e-10

    def int_number(self, items: list[Token]) -> int:
        return int(items[0])

    def float_number(self, items: list[Token]) -> float:
        return float(items[0])

    def negative_int(self, items: list[Token]) -> int:
        return -int(items[0])

    def negative_float(self, items: list[Token]) -> float:
        return -float(items[0])

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

    # Comparison operations
    def eq(self, items: list) -> bool:
        # Handle floating point comparisons with a small epsilon
        if isinstance(items[0], float) or isinstance(items[1], float):
            return abs(items[0] - items[1]) < self.EPSILON
        return items[0] == items[1]

    def ne(self, items: list) -> bool:
        # Handle floating point comparisons with a small epsilon
        if isinstance(items[0], float) or isinstance(items[1], float):
            return abs(items[0] - items[1]) >= self.EPSILON
        return items[0] != items[1]

    def lt(self, items: list) -> bool:
        return items[0] < items[1]

    def gt(self, items: list) -> bool:
        return items[0] > items[1]

    def le(self, items: list) -> bool:
        return items[0] <= items[1]

    def ge(self, items: list) -> bool:
        return items[0] >= items[1]

    # Logical operations
    def and_op(self, items: list) -> bool:
        return bool(items[0]) and bool(items[1])

    def or_op(self, items: list) -> bool:
        return bool(items[0]) or bool(items[1])


# Create the parser
parser = Lark(grammar, start="expr", parser="lalr")


# Function to evaluate expressions
def evaluate(expression: str) -> int | float | bool:
    """
    Evaluate an expression with integers, arithmetic operations, and comparisons

    Args:
        expression: String containing the expression to evaluate

    Returns:
        Result of the evaluation (integer or boolean)
    """
    # First try to parse
    try:
        tree = parser.parse(expression)
    except Exception as e:
        # Handle parse errors
        raise ValueError(f"Invalid expression syntax: {expression}") from e

    # Then try to evaluate
    try:
        return ExpressionTransformer().transform(tree)
    except lark_exceptions.VisitError as e:
        # Check if the underlying error is a ZeroDivisionError
        if isinstance(e.__context__, ZeroDivisionError):
            raise ZeroDivisionError("Division by zero") from e
        # Re-raise other VisitErrors
        raise ValueError(f"Error evaluating expression: {expression}") from e
