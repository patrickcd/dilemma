import click
from dilemma.lang import evaluate

@click.command()
@click.argument("expression")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def evaluate_expression(expression, verbose):
    """Evaluate a mathematical or logical expression.

    EXPRESSION: The expression to evaluate, e.g. "2 + 3 * 4" or "5 > 3 and 2 < 4"
    """
    try:
        result = evaluate(expression)
        if verbose:
            click.echo(f"Expression: {expression}")
            click.echo(f"Result: {result}")
            click.echo(f"Type: {type(result).__name__}")
        else:
            click.echo(result)
        return 0
    except Exception as e:
        click.echo(f"Error evaluating expression: {e}", err=True)
        return 1

if __name__ == "__main__":
    evaluate_expression()
