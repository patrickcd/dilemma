"""
This module is a sketch of a an idea for running Dilemma expressions
asynchronously, fetching data from url and evaluating them within the same
expression.
"""

from datetime import datetime
from contextvars import ContextVar

from lark import Lark, Tree

from ..lang import ExpressionTransformer, CompiledExpression, _process_variables, grammar
from ..errors import parsing_error_handling, execution_error_handling
from ..logconf import get_logger

log = get_logger(__name__)


_context_var: ContextVar[Lark] = ContextVar("_context_var")


def build_parser() -> Lark:
    """
    Returns a context-var local instance of the Lark parser.
    """
    if not _context_var.get(False):
        log.info("Building parser from grammar and assigning to thread local")
        _context_var.set(Lark(grammar, start="expr", parser="lalr"))
    return _context_var.get()


class AsyncExpressionTransformer(ExpressionTransformer):
    """Asynchronous version of ExpressionTransformer."""

    async def transform_async(self, tree):
        """Transform a parse tree asynchronously."""
        # Get the tree's data which is the name of the rule
        rule = tree.data

        # If we have a specific async handler for this rule, use it
        if hasattr(self, f"{rule}_async"):
            children = [
                await self.transform_async(child) if isinstance(child, Tree) else child
                for child in tree.children
            ]
            handler = getattr(self, f"{rule}_async")
            return await handler(children)

        # Otherwise, fall back to the sync handler but handle async children
        children = []
        for child in tree.children:
            if isinstance(child, Tree):
                child_result = await self.transform_async(child)
            else:
                child_result = child
            children.append(child_result)

        # Call the sync handler with the processed children
        handler = getattr(self, rule)
        return handler(children)

    async def resolver_expression_async(self, items):
        """Process a backticked expression asynchronously."""
        # Extract the expression from the token
        raw_expr = items[0].value[1:-1]  # Remove backticks

        # Use the async resolver system
        from ..resolvers import resolve_path_async

        value = await resolve_path_async(raw_expr, self.processed_json, raw=True)

        # Handle datetime reconstruction
        if isinstance(value, dict) and "__datetime__" in value:
            return datetime.fromisoformat(value["__datetime__"])

        return value


async def evaluate_async(expression, variables=None):
    """Asynchronous version of evaluate()."""
    processed_json = _process_variables(variables)
    parser = build_parser()

    with parsing_error_handling(expression, parser.parse):
        tree = parser.parse(expression)

    with execution_error_handling(expression):
        transformer = AsyncExpressionTransformer(processed_json=processed_json)
        return await transformer.transform_async(tree)


class AsyncCompiledExpression(CompiledExpression):
    """Async version of CompiledExpression."""

    async def evaluate_async(self, variables=None):
        """Evaluate this compiled expression asynchronously."""
        processed_json = _process_variables(variables)

        with execution_error_handling(self.expression):
            transformer = AsyncExpressionTransformer(processed_json=processed_json)
            return await transformer.transform_async(self.parse_tree)


async def compile_expression_async(expression):
    """Compile an expression for async evaluation."""
    parser = build_parser()
    with parsing_error_handling(expression, parser.parse):
        tree = parser.parse(expression)
        return AsyncCompiledExpression(expression, tree)
