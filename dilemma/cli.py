import click
from dilemma.lang import evaluate


@click.command()
@click.argument("expression")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def evaluate_expression(expression: str, verbose: bool) -> None:
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
    except ZeroDivisionError as zde:
        click.echo("Error evaluating expression: Division by zero", err=True)
        # Use Click's built-in error handling
        raise click.Abort from zde
    except Exception as e:
        click.echo(f"Error evaluating expression: {e}", err=True)
        # Use Click's built-in error handling
        raise click.Abort from e


if __name__ == "__main__":
    evaluate_expression()  # No need for sys.exit when using click.Abort
