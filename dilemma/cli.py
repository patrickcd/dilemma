import click
import yaml
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dilemma.lang import evaluate


@click.group()
def cmd():
    """Dilemma Expression Engine CLI."""
    pass


@cmd.command(name="x")
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


@cmd.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="docs/examples.md",
    help="Output markdown file path",
)
def gendocs(output):
    """Generate documentation from test examples."""
    try:
        # Find the examples directory
        tests_dir = Path(__file__).parents[1] / "tests" / "examples"
        if not tests_dir.exists():
            click.echo(f"Error: Examples directory not found at {tests_dir}", err=True)
            raise click.Abort()

        # Ensure the output directory exists
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Load examples from YAML files
        examples_by_category = {}
        time_values = create_time_values()

        yaml_files = list(tests_dir.glob("*.y*ml"))
        if not yaml_files:
            click.echo("No YAML files found in the examples directory", err=True)
            raise click.Abort()

        for yaml_file in sorted(yaml_files, key=lambda x: x.stem):
            with open(yaml_file, 'r') as f:
                examples = yaml.safe_load(f)

            for example in examples:
                category = example.get("category", "Uncategorized")
                if category not in examples_by_category:
                    examples_by_category[category] = []
                examples_by_category[category].append(example)

        # Generate documentation
        md_content = generate_markdown_docs(examples_by_category, time_values)

        # Write to file
        with open(output_path, 'w') as f:
            f.write(md_content)

        click.echo(f"Documentation generated successfully: {output_path.absolute()}")

    except Exception as e:
        click.echo(f"Error generating documentation: {e}", err=True)
        raise click.Abort() from e


def create_time_values():
    """Create a dictionary of time values for documentation."""
    now = datetime.now(timezone.utc)
    return {
        "__NOW__": now,
        "__YESTERDAY__": now - timedelta(days=1),
        "__TOMORROW__": now + timedelta(days=1),
        "__HOUR_AGO__": now - timedelta(hours=1),
        "__IN_TWO_HOURS__": now + timedelta(hours=2),
        "__LAST_WEEK__": now - timedelta(days=7),
        "__NEXT_MONTH__": now + timedelta(days=30),
    }


def generate_markdown_docs(examples_by_category, time_values):
    """Generate formatted markdown documentation from examples."""
    from markdowngenerator import MarkdownGenerator
    import tempfile
    from pathlib import Path

    # Use a temporary file to generate the markdown
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.md', delete=False) as temp_file:
        temp_path = temp_file.name

    # Create the markdown document, writing directly to the temporary file
    with MarkdownGenerator(filename=temp_path, enable_write=True) as doc:
        doc.addHeader(1, "Dilemma Expression Examples")
        doc.writeTextLine("This document contains examples of using the Dilemma expression language.")
        doc.writeTextLine("")  # Instead of writeNewLine, use an empty string

        # Sort categories
        categories = list(examples_by_category.keys())

        for category in categories:
            # Format category name - convert snake_case to Title Case
            formatted_category = category.replace('_', ' ').title()
            doc.addHeader(3, formatted_category)

            examples = examples_by_category[category]
            for i, example in enumerate(examples):
                # Add heading for each example
                title = example.get('name', example.get('description', f"Example {i+1}"))
                ft = title.replace("_", " ").title()

                # Add description if available
                if 'description' in example and example['name'] != example['description']:
                    doc.writeTextLine(example['description'])
                else:
                    doc.writeTextLine(ft)
                doc.writeTextLine("")  # Empty line instead of writeNewLine

                # Create a table with expression and expected result
                # We need to create the table manually to avoid HTML escaping of quotes
                doc.writeTextLine("| Expression | Expected Result |")
                doc.writeTextLine("|:---:|:---:|")

                # Handle the expression properly, escaping special characters for markdown table
                expression = example['expression']
                # Replace any raw " in the expression with escaped form for markdown
                expression = expression.replace('"', '\\"')
                # Replace pipe characters with their HTML entity code to prevent table breakage
                expression = expression.replace('|', '\\|')

                doc.writeTextLine(f"| `{expression}` | `{example['expected']}` |")
                doc.writeTextLine("")  # Empty line instead of writeNewLine

                # Add context if available
                if example.get('context'):
                    doc.addHeader(4, "Context")

                    # Process context to replace time placeholders with real dates
                    context = process_time_values_for_docs(example['context'], time_values)

                    # Format context as JSON
                    context_json = json.dumps(context, indent=2, default=str)
                    doc.addCodeBlock(context_json, "json")

                doc.addHorizontalRule()

    # Read the generated content from the temporary file
    with open(temp_path, 'r') as f:
        content = f.read()

    # Clean up the temporary file
    Path(temp_path).unlink()

    # Post-process to fix HTML entities
    content = content.replace('&#x27;', "'")
    content = content.replace('&quot;', '"')
    content = content.replace('&gt;', '>')
    content = content.replace('&lt;', '<')
    content = content.replace('&amp;', '&')

    return content


def process_time_values_for_docs(data, time_values):
    """Recursively process a data structure and replace time placeholders with readable dates."""
    if isinstance(data, dict):
        return {k: process_time_values_for_docs(v, time_values) for k, v in data.items()}
    elif isinstance(data, list):
        return [process_time_values_for_docs(item, time_values) for item in data]
    elif isinstance(data, str) and data in time_values:
        # Format the datetime for documentation
        dt = time_values[data]
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    else:
        return data


if __name__ == "__main__":
    cmd()  # Use the group instead of the evaluate_expression function
