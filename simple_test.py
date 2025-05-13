# Simple test script for error message templates

import dilemma

# Test default error message
try:
    dilemma.evaluate("1 / 0")
except Exception as e:
    print(f"Default error: {e}")

# Test custom error message
templates = dilemma.error_messages.get_default_templates()
templates["zero_division"] = "🚫 Cannot divide by zero! 🚫"
dilemma.error_messages.configure_templates(templates)

try:
    dilemma.evaluate("1 / 0")
except Exception as e:
    print(f"Custom error: {e}")
