from typing import Callable
from contextlib import contextmanager

from lark.exceptions import UnexpectedCharacters, UnexpectedEOF, UnexpectedToken


from .examples import ERROR_EXAMPLES
from .exc import UnexpectedCharacterError, UnexpectedEOFError, UnexpectedTokenError


def suggest_correction(interactive_parser, token):
    """
    Suggest possible corrections based on expected tokens at the error position.

    Args:
        interactive_parser: Lark's InteractiveParser instance from UnexpectedToken
                           exception. This parser maintains the state at the point
                           of failure and can tell us what tokens would have been
                           accepted at that position.
        token: The token that caused the error. Contains information about the
              actual token received (type, value, line, column).

    Returns:
        list: Suggestions for how to fix the error, based on what tokens
              were expected at this position in the grammar.

    Notes:
        The interactive_parser.accepts() method returns a set of terminal names
        that would have been valid at the error position. This can be used to
        create context-aware suggestions like "Did you mean to use '+' instead
        of ','?" or "Variable names cannot be reserved keywords like 'and'."
    """
    suggestions = []
    if interactive_parser:
        accepts = interactive_parser.accepts()

        # Map cryptic token names to user-friendly suggestions
        token_suggestions = {
            "PLUS": "+ (plus)",
            "MINUS": "- (minus)",
            "MULT": "* (multiply)",
            "DIV": "/ (divide)",
        }

        # Generate readable suggestions
        readable = [token_suggestions.get(t, t) for t in accepts]
        if readable:
            suggestions.append(f"Expected: {', '.join(readable)}")

        # Suggest corrections for common mistakes
        if token.type == "VARIABLE" and any(kw in accepts for kw in ["AND", "OR"]):
            suggestions.append(
                f"'{token.value}' might be a reserved keyword. Try quoting it."
            )

    return suggestions


@contextmanager
def parsing_error_handling(expression: str, parse_func: Callable):
    """
    Handle syntax and parsing errors with useful context and suggestions.

    Args:
        expression: The expression string being parsed
        parse_func: A callable that takes an expression string and returns
                   a parse tree, typically parser.parse from a Lark parser
    """
    try:
        yield
    except UnexpectedToken as e:
        error_context = e.get_context(expression)
        error_pattern = None

        if hasattr(e, "state") and e.state is not None:
            error_pattern = e.match_examples(parse_func, ERROR_EXAMPLES)

        suggestions = (
            suggest_correction(e.interactive_parser, e.token)
            if e.interactive_parser
            else []
        )

        raise UnexpectedTokenError(
            template_key=error_pattern or "unexpected_token",
            details=str(e),
            context=error_context,
            line=e.line,
            column=e.column,
            suggestions=suggestions,
        )
    except UnexpectedCharacters as e:
        error_context = e.get_context(expression)
        raise UnexpectedCharacterError(
            template_key="unexpected_character",
            details=str(e),
            context=error_context,
            line=e.line,
            column=e.column,
        )
    except UnexpectedEOF as e:
        raise UnexpectedEOFError(
            template_key="unexpected_eof", details=str(e), expected=list(e.expected)
        )
