"""
Expression language implementation using Lark
"""

from lark import Lark, Transformer, exceptions as lark_exceptions
from lark import Token

# Define the grammar for our simple expression language
grammar = """
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

    ?term: INTEGER -> number
         | "-" INTEGER -> negative_number
         | "(" expr ")" -> paren

    INTEGER: /[0-9]+/

    %import common.WS
    %ignore WS
"""


# Transformer to evaluate expressions
class ExpressionTransformer(Transformer):
    def number(self, items: list[Token]) -> int:
        return int(items[0])

    def negative_number(self, items: list[Token]) -> int:
        # Convert the token to a negative integer
        return -int(items[0])

    def add(self, items: list[int]) -> int:
        return items[0] + items[1]

    def sub(self, items: list[int]) -> int:
        return items[0] - items[1]

    def mul(self, items: list[int]) -> int:
        return items[0] * items[1]

    def div(self, items: list[int]) -> int:
        # Handle division by zero
        if items[1] == 0:
            raise ZeroDivisionError("Division by zero")
        return items[0] // items[1]  # Using integer division

    def paren(self, items: list) -> int:
        """Handle parenthesized expressions by returning the inner value"""
        return items[0]

    # Comparison operations
    def eq(self, items: list) -> bool:
        return items[0] == items[1]

    def ne(self, items: list) -> bool:
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
def evaluate(expression: str) -> int | bool:
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
