from .lookup import compile_getter
from .lang import parser, ExpressionTransformer


class OptimizedExpressionTransformer(ExpressionTransformer):
    """
    An optimized version of ExpressionTransformer that supports
    pre-compiled variable getters.
    """

    def __init__(
        self, variables: dict | None = None, optimized_getters: dict | None = None
    ):
        super().__init__(variables=variables)
        self.optimized_getters = optimized_getters or {}

    def variable(self, items: list) -> int | float | bool:
        var_path = items[0].value

        # Use optimized getter if available
        if var_path in self.optimized_getters:
            try:
                # Call the pre-compiled getter function
                return self.optimized_getters[var_path](self.variables)
            except Exception:
                # Fall back to regular lookup if the optimized getter fails
                pass

        # Fall back to the standard implementation
        return super().variable(items)


def create_optimized_evaluator(expression, sample_variables_json=None):
    """
    Create an optimized evaluator function for a specific expression.

    Args:
        expression: The expression to be evaluated
        sample_variables_json: JSON string representing the sample variables structure

    Returns:
        A function that evaluates the expression with given variables
    """
    # Parse the expression once
    tree = parser.parse(expression)

    # If sample variables provided, compile getters for variable paths
    compiled_getters = {}
    if sample_variables_json:
        var_paths = extract_variable_paths(tree)
        for path in var_paths:
            try:
                compiled_getters[path] = compile_getter(path, sample_variables_json)
            except Exception:
                # Fall back to regular lookup if compilation fails
                pass

    def evaluator(variables):
        transformer = OptimizedExpressionTransformer(
            variables=variables, optimized_getters=compiled_getters
        )
        return transformer.transform(tree)

    return evaluator


def extract_variable_paths(tree):
    """
    Extract variable paths from the parsed expression tree.

    Args:
        tree: The parsed expression tree

    Returns:
        A list of variable paths
    """
    paths = set()

    # Define a visitor function to extract variables
    def _extract_vars(node):
        # Check if this is a variable node
        if hasattr(node, "data") and node.data == "variable" and node.children:
            # The first child should be the token with the variable path
            token = node.children[0]
            if hasattr(token, "value"):
                paths.add(token.value)

        # Recursively process all children
        if hasattr(node, "children"):
            for child in node.children:
                _extract_vars(child)

    # Start extraction from the root
    _extract_vars(tree)
    return list(paths)
