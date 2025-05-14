# Dilemma Expression Engine

A friendly yet powerful expression evaluation engine  for Python applications.

## Features

- Secure evaluation of mathematical and logical expressions
- Support for variables with nested structure (e.g., `user.profile.settings.enabled`)
- Rich comparison operations with proper handling of floating-point values
- Logical operations (`and`, `or`) for boolean expressions
- Natural language attribute lookups - " user's name is 'bob' "
- Friendly date comparisons - "user's expiry is after $today"
- Wildcard text matching
- Performance optimization strategies for repeated evaluations
 - **Is it too late reach the bar before last orders?**

```javascript
# It's 22:15
{
    bar: {
      closing_time: "23:30",
      distance: 10
    },
    bike{
      speed: 20,
      units: "mph"
    }
}

# dilemma expression:

>  bar's closing_time within (bar.distance/bike.speed) hours

Result: false (last orders very possible)
````

#### Async Note

The current implementation is **not** suitable for async code because it uses a thread local to
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
is_adult = evaluate("user.profile.age >= settings.min_age", variables)  # Returns true
```

## Language

### Paths

Dilemma uses a powerful path lookup system based on [JQ](https://stedolan.github.io/jq/) to access
nested data within variables. This allows you to:

- Navigate deeply nested structures with slash notation (`user.profile.preferences.theme`)
- Access elements in arrays using numeric indices in the path (`users[0].name`)

#### Advanced: Direct JQ Expressions

For advanced users who need more powerful data access patterns, Dilemma supports direct JQ expressions using backtick syntax:

```python
# Basic JQ expression to access array elements
evaluate('`.users[0].name` == "Alice"', variables)

# Complex JQ filtering and transformation
evaluate('`.users[] | select(.roles | contains(["admin"]))[].name` == "Alice"', variables)

# Combine with regular Dilemma expressions
evaluate('`.users | length` > 2 and settings.active == true', variables)
```

This provides full access to JQ's powerful features:
- Array filtering and iteration
- Object transformation
- Mathematical operations
- Conditionals and complex selections

The angle bracket syntax offers an escape hatch for complex data access patterns while still benefiting from
Dilemma's expression evaluation environment.

#### Supported Operations

You can use these paths in various operations:

- Check if a key exists in a dictionary: `'address' in user.profile`
- Check if a value exists in a list: `'admin' in user.roles`
- Compare nested values: `user.settings.theme == 'dark'`
- Date operations on nested dates: `user.account.created_at is past`

Behind the scenes, the path lookups are optimized to provide the best performance even with complex nested structures.


#### Date Comparisons

Dilemma provides convenient date and time comparison operations that make it easy to work with temporal data:

- **State comparisons**:
  - `date is $past` - Checks if a date is in the past
  - `date is $future` - Checks if a date is in the future
  - `date is $today` - Checks if a date falls on the current day

- **Time references**:
  - `$now` - References the current date and time for comparisons (e.g., `date > $now`)

- **Time window comparisons**:
  - `date within N unit` - Checks if a date is within the specified time period from now
  - `date older than N unit` - Checks if a date is older than the specified time period
  - Supported time units: `minute(s)`, `hour(s)`, `day(s)`, `week(s)`, `month(s)`, `year(s)`

- **Date-to-date comparisons**:
  - `date1 before date2` - Checks if the first date is chronologically before the second
  - `date1 after date2` - Checks if the first date is chronologically after the second
  - `date1 same_day_as date2` - Checks if both dates fall on the same calendar day

Examples:

```python
# Check if account has expired
evaluate("user.subscription.end_date is $past", context)

# Check for recent activity
evaluate("user.last_login within 24 hours", context)

# Check if a date range contains today
evaluate("start_date before $now and end_date after $now", context)

# Check account age
evaluate("user.created_at older than 1 year", context)

# Compare with current time
evaluate("meeting.start_time > $now", context)
```

### Container Emptiness Checks

Dilemma provides a convenient way to check if containers (lists and dictionaries) are empty:

- `container is $empty` - Returns `true` if the container has no elements

Examples:

```python
# Check if a user has any roles
evaluate("user.roles is $empty", context)  # true if roles list is empty

# Check if search results exist
evaluate("search_results is $empty", context)  # true if no results

# Combine with other conditions
evaluate("user.is_active and not (user.permissions is $empty)", context)
```

### Optimization Details

Dilemma offers two levels of optimization:

1. **Pre-parsed evaluation**: Parses the expression once and reuses the parse tree for subsequent evaluations (4.28x speedup)
2. **Compiled expressions**: Compile expressions once and evaluate them multiple times with different contexts

#### Using Compiled Expressions

For the best performance when evaluating the same expression multiple times with different variable contexts:

```python
from dilemma.lang import compile

# Compile the expression once (parse tree is created and stored)
age_check = compile("user.age >= 18")

# Evaluate with different variable contexts
result1 = age_check.evaluate({"user": {"age": 25}})  # Returns true
result2 = age_check.evaluate({"user": {"age": 16}})  # Returns false

# Works with complex expressions and nested paths
eligibility = compile("user.account.is_active and (user.subscription.level == 'premium' or user.account.credits > 100)")

# Apply to different users
user1_eligible = eligibility.evaluate(user1_data)
user2_eligible = eligibility.evaluate(user2_data)
```

This approach is significantly more efficient than repeatedly calling `evaluate()` with the same expression string, as it eliminates the parsing overhead for each evaluation.


## Pluggable Context Resolvers

Dilemma uses a flexible plugin system for resolving variable paths in expressions. This allows you to:

- Use different path resolution strategies
- Deploy in environments with different capabilities (e.g., browsers via pyodide)
- Create custom resolvers for specialized data structures

### Built-in Resolvers

Dilemma comes with three built-in resolvers:

1. **JqResolver**: Uses the [jq](https://stedolan.github.io/jq/) library for powerful JSON path resolution
   - Provides full jq query capabilities including conditionals and transformations
   - Requires a C extension (not compatible with pyodide/WebAssembly)
   - Used by default when available

2. **JsonPathResolver**: Uses [jsonpath-ng](https://github.com/h2non/jsonpath-ng) for pure Python path resolution
   - Works in all Python environments including pyodide
   - Slightly less powerful than jq but covers most use cases
   - Used as fallback when jq is unavailable

3. **BasicResolver**: A minimal resolver for simple dictionary lookups
   - No external dependencies
   - Only supports top-level dictionary keys
   - Used as a last resort when other resolvers are unavailable

### Creating a Custom Resolver

You can create your own resolver by extending the `ResolverSpec` class:

```python
from dilemma.resolvers.interface import ResolverSpec

class MyCustomResolver(ResolverSpec):
    """A custom resolver implementation."""

    def __init__(self):
        super().__init__()
        # Initialize any resources needed

    def _convert_path(self, path):
        """Convert dilemma path to your resolver's syntax."""
        # First apply the base class's possessive handling
        path = super()._convert_path(path)

        # Then apply your custom conversion logic
        # ...implementation specific to your resolver...
        return path

    def _execute_query(self, converted_path, context):
        """Execute the converted path against the context."""
        # Your resolution logic here
        # ...implementation specific to your resolver...

        # Return the result or None if not found
        return result

    def _execute_raw_query(self, raw_expr, context):
        """Execute a raw expression (from backtick syntax)."""
        # Handle raw expressions (if supported)
        # ...implementation specific to your resolver...
        return result
```

### Registering and Using Custom Resolvers

To use your custom resolver, register it with Dilemma's resolver system:

```python
from dilemma.resolvers import register_resolver
from mypackage.resolvers import MyCustomResolver

# Register your resolver (default=True makes it the preferred resolver)
register_resolver(MyCustomResolver, default=True)

# Or register with a specific name
register_resolver(MyCustomResolver, name="mycustom")

```

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