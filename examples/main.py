"""
This module contains examples of Python code.
"""

import dilemma


def main() -> None:
    """Main function."""
    vec1 = dilemma.Vector2D(-1, 1)
    vec2 = dilemma.Vector2D(2.5, -2.5)
    print(vec1 - vec2)


if __name__ == "__main__":
    main()
