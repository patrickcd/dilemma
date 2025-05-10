import pytest
from click.testing import CliRunner
from dilemma.cli import evaluate_expression


@pytest.fixture
def runner():
    """Create a Click CLI runner for testing."""
    return CliRunner()


def test_basic_arithmetic(runner):
    """Test basic arithmetic expressions."""
    result = runner.invoke(evaluate_expression, ["2 + 3"])
    assert result.exit_code == 0
    assert result.output.strip() == "5"


def test_complex_expression(runner):
    """Test more complex expressions."""
    result = runner.invoke(evaluate_expression, ["2 + 3 * 4"])
    assert result.exit_code == 0
    assert result.output.strip() == "14"


def test_boolean_expression(runner):
    """Test boolean expressions."""
    result = runner.invoke(evaluate_expression, ["5 > 3 and 2 < 4"])
    assert result.exit_code == 0
    assert result.output.strip() == "True"


def test_verbose_output(runner):
    """Test the --verbose flag."""
    result = runner.invoke(evaluate_expression, ["2 + 3", "--verbose"])
    assert result.exit_code == 0
    assert "Expression: 2 + 3" in result.output
    assert "Result: 5" in result.output
    assert "Type: int" in result.output


def test_invalid_expression(runner):
    """Test handling of invalid expressions."""
    result = runner.invoke(evaluate_expression, ["2 + * 3"])
    assert result.exit_code == 1
    assert "Error evaluating expression" in result.output


def test_division_by_zero(runner):
    """Test handling of division by zero."""
    result = runner.invoke(evaluate_expression, ["5 / 0"])
    # Print debug info
    print(f"Exit code: {result.exit_code}")
    print(f"Output: {result.output}")
    assert result.exit_code == 1
    assert "Division by zero" in result.output
