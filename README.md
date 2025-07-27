# Dilemma Expression Language

[![CI](https://github.com/patrickcd/dilemma/workflows/CI/badge.svg)](https://github.com/patrickcd/dilemma/actions)
[![codecov](https://codecov.io/gh/patrickcd/dilemma/branch/main/graph/badge.svg)](https://codecov.io/gh/patrickcd/dilemma)
[![PyPI version](https://badge.fury.io/py/dilemma.svg)](https://badge.fury.io/py/dilemma)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-312/)

A secure, powerful expression evaluation engine for Python applications that makes complex logical expressions readable and maintainable.

## Why Dilemma?

Instead of writing complex Python conditionals like this:
```python
if (user.get('profile', {}).get('age', 0) >= 18 and 
    user.get('subscription', {}).get('status') == 'active' and
    datetime.now() - user.get('last_login', datetime.min) < timedelta(days=30)):
    # grant access
```

Write this:
```python
from dilemma import evaluate

expr = "user.profile.age >= 18 and user.subscription.status == 'active' and user.last_login within 30 days"

if evaluate(expr, context):
    # grant access
```

## Features

- **Secure evaluation** - No arbitrary code execution, only safe expressions
- **Rich data access** - Navigate nested dictionaries and lists with ease
- **Date/time operations** - Natural language date comparisons
- **Multiple resolvers** - JsonPath, JQ, and basic dictionary lookup
- **Performance optimized** - Compile expressions once, evaluate many times
- **Type safe** - Built-in type checking and validation

## Quick Start

```bash
pip install dilemma
```

```python
from dilemma import evaluate

# Basic arithmetic and logic
result = evaluate("2 * (3 + 4)")  # Returns 14
result = evaluate("age >= 18 and status == 'active'", {"age": 25, "status": "active"})

# Date operations
result = evaluate("user.last_login within 7 days", context)
result = evaluate("subscription.end_date is $future", context)

# Complex data access
result = evaluate("user.permissions contains 'admin'", context)
result = evaluate("`users[].roles[] | select(. == 'admin')` | length > 0", context)
```

## Language Features

### Data Access Patterns

```python
# Dot notation for nested objects
"user.profile.settings.theme == 'dark'"

# Natural possessive syntax  
"user's subscription's status == 'premium'"

# Array/list access
"users[0].name == 'Alice'"

# Check membership
"'admin' in user.roles"
"user.permissions contains 'read'"
```

### Date and Time Operations

```python
# Relative time checks
"user.created_at within 30 days"
"order.shipped_date older than 1 week"

# State comparisons
"subscription.expires is $future"
"last_backup is $past"
"meeting.date is $today"

# Date comparisons
"start_date before end_date"
"event.date same_day_as $now"
```

### Advanced JQ Integration

For complex data manipulation, use JQ expressions in backticks:

```python
# Filter and transform arrays
evaluate('`users[] | select(.active == true) | .name`')

# Mathematical operations on arrays
evaluate('`sales[].amount | add` > 10000')

# Complex conditionals
evaluate('`products[] | select(.price > 100 and .category == "electronics") | length` > 5')
```

## Performance Optimization

For repeated evaluations, compile expressions once:

```python
from dilemma import compile_expression

# Compile once
eligibility_check = compile_expression(
    "user.age >= 18 and user.subscription.active and user.last_login within 30 days"
)

# Evaluate many times with different contexts
for user_data in users:
    if eligibility_check.evaluate(user_data):
        send_premium_content(user_data)
```

## Error Handling

Dilemma provides clear, actionable error messages:

```python
try:
    result = evaluate("user.invalidfield == 'test'", context)
except ExpressionError as e:
    print(f"Expression error: {e}")
    # Suggests available fields and common fixes
```

## Use Cases

- **Form validation rules** - `"email matches '^[^@]+@[^@]+$' and age >= 13"`
- **Business logic** - `"order.total > 100 and customer.tier == 'premium'"`
- **Access control** - `"user.roles contains 'admin' or resource.owner == user.id"`
- **Data filtering** - `"created_at within 24 hours and status == 'pending'"`
- **Workflow conditions** - `"approval.status == 'approved' and budget.remaining >= cost"`

## Safety & Security

- ✅ No arbitrary Python code execution
- ✅ No access to imports or builtins  
- ✅ Sandboxed evaluation environment
- ✅ Input validation and sanitization
- ✅ Memory and complexity limits

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.