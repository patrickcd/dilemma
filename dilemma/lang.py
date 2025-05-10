"""
Expression language implementation using Lark
"""

from lark import Lark, Transformer, exceptions as lark_exceptions
from lark import Token

# Define the grammar for our simple expression language
grammar = """
    expr: sum

    sum: product
       | sum "+" product -> add
       | sum "-" product -> sub

    product: term
           | product "*" term -> mul
           | product "/" term -> div

    term: INTEGER -> number
        | "-" INTEGER -> negative_number

    INTEGER: /[0-9]+/

    %import common.WS
    %ignore WS
"""


# Transformer to evaluate expressions
class ExpressionTransformer(Transformer):
    def number(self, items: list[Token]) -> int:
        return int(items[0])

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

    def expr(self, items: list[int]) -> int:
        # Pass through the value from the sum node
        return items[0]

    def sum(self, items: list[int]) -> int:
        # Pass through the value from its child
        return items[0]

    def product(self, items: list[int]) -> int:
        # Pass through the value from its child
        return items[0]

    def negative_number(self, items: list[Token]) -> int:
        # Convert the token to a negative integer
        return -int(items[0])


# Create the parser
parser = Lark(grammar, start="expr", parser="lalr")


# Function to evaluate expressions
def evaluate(expression: str) -> int:
    """
    Evaluate a simple arithmetic expression with integers, addition, subtraction,
    multiplication, and division

    Args:
        expression: String containing the expression to evaluate

    Returns:
        Integer result of the evaluation
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
