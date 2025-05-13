import functools
import logging
from contextlib import contextmanager


log = logging.getLogger(__name__)

def binary_op(func):
    """
    Decorator that extracts items[0] and items[1] into left and right variables

    Lark calls transformer methods with a list. Most methods in dilemma's
    ExpressionTransformer perform binary comparisons so they need to extract
    items [0] and[1] from the list. This decorator takes care of that for the common
    case. Decoratored methods can be called with either a single list argument (as
    occurs when called by Lark) or with two left and right arguments.
    """
    @functools.wraps(func)
    def wrapper(self, *args):
        arg_length = len(args)
        if arg_length == 1:
            left, right = args[0][0], args[0][1]
        elif arg_length == 2:
            left, right = args
        else:
            raise ValueError(
                "Functions decorated with binary_op take either a single list argument,"
                " 'items', or two arguments, 'left' + 'right'"
            )
        return func(self, left, right)
    return wrapper

def both_strings(left, right):
    return isinstance(left, str) and isinstance(right, str)


def either_string(left, right):
    return isinstance(left, str) or isinstance(right, str)


def reject_strings(left, right, op_symbol: str):
    """Raise TypeError if either operand is a string type"""
    if either_string(left, right):
        raise TypeError(f"'{op_symbol}' operator not supported with string operands")


@contextmanager
def error_handling(expression: str):
    """
    Context manager for handling common expression evaluation errors
    with consistent error reporting.

    Args:
        e: The caught VisitError exception

    Raises:
        ZeroDivisionError, NameError, TypeError: Re-raised with clean messages
        ValueError: For all other evaluation errors
    """

    try:
        yield
    except Exception as e:
        # Re-raise common errors with clean messages
        if isinstance(e.__context__, ZeroDivisionError):
            raise ZeroDivisionError("Division by zero") from e
        if isinstance(e.__context__, NameError):
            raise NameError(str(e.__context__)) from e
        if isinstance(e.__context__, TypeError):
            raise TypeError(str(e.__context__)) from e

        # Log the original error for debugging
        log.error(
            f"Evaluation error: {type(e.__context__).__name__}: {e.__context__}"
        )

        # Raise a ValueError with details about what went wrong
        err_name = type(e.__context__).__name__
        err = e.__context__
        raise ValueError(
            f"Error evaluating expression: {expression} - Caused by: {err_name}: {err}"
        ) from e


def check_containment(container, item, container_position: str) -> bool:
    """
    Helper function to check if an item is contained in a container.

    Args:
        container: The container object (list, tuple, dict, or str)
        item: The item to check for containment
        container_position: Position descriptor for error message ("left" or "right")

    Returns:
        True if the item is in the container, False otherwise

    Raises:
        TypeError: If the container is not a valid container type
    """
    match container:
        case list() | tuple():
            return item in container
        case dict():
            return item in container  # Check if key exists in dict
        case str() if isinstance(item, str):
            return item in container  # String contains string
        case _:
            raise TypeError(
                f"'{container_position}' operand must be a collection "
                "(string, list, dict)"
            )
