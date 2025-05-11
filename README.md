# Dilemma Expression Engine

A lightweight yet powerful expression evaluation engine with optimized performance for Python applications.

## Features

- Secure evaluation of mathematical and logical expressions
- Support for variables with dot notation (e.g., `user.profile.settings.enabled`)
- Rich comparison operations with proper handling of floating-point values
- Logical operations (`and`, `or`) for boolean expressions
- Performance optimization strategies for repeated evaluations

## Async Note

The current implementation is **not** suitable for async code because it using threading.local to
maintain different parsers per thread.

## Installation

```bash
pip install dilemma
```

## Basic Usage

```python
from dilemma.lang import evaluate

# Evaluate a simple expression
result = evaluate("2 * (3 + 4)")  # Returns 14

# Use variables in expressions
variables = {
    "user": {
        "profile": {
            "age": 32,
            "preferences": {
                "theme": "dark"
            }
        }
    },
    "settings": {
        "min_age": 18
    }
}

# Evaluate with variables
is_adult = evaluate("user.profile.age >= settings.min_age", variables)  # Returns True
```


## Optimization Details

Dilemma offers two levels of optimization:

1. **Pre-parsed evaluation**: Parses the expression once and reuses the parse tree for subsequent evaluations (4.28x speedup)

2. **Fully optimized evaluation**: Combines pre-parsing with compiled variable getters for extremely efficient variable resolution (7.25x speedup)

## Use Cases

- Form validation rules
- Business logic expressions
- Dynamic filtering of datasets
- Guard conditions in workflows
- Configuration-driven behavior

## Safety

Unlike Python's built-in `eval()`, Dilemma provides a secure evaluation environment:

- No execution of arbitrary Python code
- No access to builtins or imports
- Limited to mathematical and logical operations
- Explicit variable passing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
