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

## Language

### Paths

Dilemma uses a powerful path lookup system based on [JQ](https://stedolan.github.io/jq/) to access nested data within variables. This allows you to:

- Navigate deeply nested structures with dot notation (`user.profile.preferences.theme`)
- Access elements in arrays using index notation (`items[0]`, `users[2].name`)
- Use JQ-compatible path expressions for powerful data access

The path resolution works by converting your dot notation paths into JQ expressions and executing them against the variable context. This provides several benefits:

- Robust handling of missing values and null checks
- Consistent behavior across different data structures (dicts, lists)
- Efficient lookup of deeply nested values
- Familiar syntax for developers used to JavaScript/Python object access

#### Supported Operations

You can use these paths in various operations:

- Check if a key exists in a dictionary: `'address' in user.profile`
- Check if a value exists in a list: `'admin' in user.roles`
- Compare nested values: `user.settings.theme == 'dark'`
- Date operations on nested dates: `user.account.created_at is past`

Behind the scenes, the path lookups are optimized to provide the best performance even with complex nested structures.


#### Date Comparisons

Dilemma provides powerful date and time comparison operations that make it easy to work with temporal data:

- **State comparisons**:
  - `date is past` - Checks if a date is in the past
  - `date is future` - Checks if a date is in the future
  - `date is today` - Checks if a date falls on the current day

- **Time window comparisons**:
  - `date within N unit` - Checks if a date is within the specified time period from now
  - `date older than N unit` - Checks if a date is older than the specified time period
  - Supported time units: `minute(s)`, `hour(s)`, `day(s)`, `week(s)`, `month(s)`, `year(s)`

- **Date-to-date comparisons**:
  - `date1 before date2` - Checks if the first date is chronologically before the second
  - `date1 after date2` - Checks if the first date is chronologically after the second
  - `date1 same_day_as date2` - Checks if both dates fall on the same calendar day

- **Format flexibility**:
  - Works with Python `datetime` objects
  - Automatically parses ISO 8601 date strings (`"2023-05-10T14:30:00Z"`)
  - Supports simple date strings (`"2023-05-10"`)
  - Handles Unix timestamps

Examples:

```python
# Check if account has expired
evaluate("user.subscription.end_date is past", context)

# Check for recent activity
evaluate("user.last_login within 24 hours", context)

# Check if a date range contains today
evaluate("start_date before today and end_date after today", context)

# Check account age
evaluate("user.created_at older than 1 year", context)
```

## Optimization Details

Dilemma offers two levels of optimization:

1. **Pre-parsed evaluation**: Parses the expression once and reuses the parse tree for subsequent evaluations (4.28x speedup)


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
