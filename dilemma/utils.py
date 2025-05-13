import functools
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone


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
        log.error(f"Evaluation error: {type(e.__context__).__name__}: {e.__context__}")

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


def temporal_unit_comparison(func):
    """
    Decorator for DateMethods' methods that expect a date-like value,
    a numeric quantity, and a string unit from Lark's 'items' list.

    It unpacks 'items', calls self._ensure_datetime() on the first element,
    casts the second to float, and passes them along with the third (unit)
    to the decorated function.
    """

    @functools.wraps(func)
    def wrapper(self, items: list):  # 'self' will be an instance of DateMethods
        if len(items) != 3:
            raise ValueError(
                "Temporal comparison operation expects 3 items: "
                "a date-like value, a quantity, and a unit string."
            )

        date_val = ensure_datetime(items[0])
        quantity_val = float(
            items[1]
        )  # Assumes items[1] is a number or string convertible to float
        unit_val = items[2]  # Assumes items[2] is already a string (e.g., "minute")

        return func(self, date_val, quantity_val, unit_val)

    return wrapper


# Helper methods
def ensure_datetime(value) -> datetime:
    """Convert value to datetime if it's not already"""
    if isinstance(value, datetime):
        return value
    elif isinstance(value, str):
        # Try different formats
        for fmt in [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S%z",
        ]:
            try:
                dt = datetime.strptime(value, fmt)
                # Make naive datetimes timezone-aware with UTC
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except ValueError:
                continue
        raise ValueError(f"Could not parse date string: {value}")
    elif isinstance(value, (int, float)):
        # Assume Unix timestamp
        return datetime.fromtimestamp(value, timezone.utc)
    else:
        raise TypeError(f"Cannot convert {type(value)} to datetime")


def create_timedelta(quantity, unit) -> timedelta:
    """Create a timedelta object based on quantity and unit"""
    # Now unit should be a simple string from one of our unit methods
    log.debug(f"Unit received: {unit} (type: {type(unit)})")

    if unit == "minute":
        return timedelta(minutes=quantity)
    elif unit == "hour":
        return timedelta(hours=quantity)
    elif unit == "day":
        return timedelta(days=quantity)
    elif unit == "week":
        return timedelta(weeks=quantity)
    elif unit == "month":
        # Approximate month as 30 days
        return timedelta(days=30 * quantity)
    elif unit == "year":
        # Approximate year as 365 days
        return timedelta(days=365 * quantity)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")


def unpack_datetimes(items: list) -> tuple[datetime, datetime]:
    """
    Extracts items 0 and 1 from the list and passes the values through
    ensure_datetime
    """
    date1 = ensure_datetime(items[0])
    date2 = ensure_datetime(items[1])
    return date1, date2
