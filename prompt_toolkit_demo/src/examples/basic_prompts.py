"""
Basic Prompts Example
=====================

This example demonstrates basic usage of prompt_toolkit for getting user input.
"""

from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory


def run():
    """Run the basic prompts example."""
    print("=== Basic Prompts Example ===\n")

    # Simple prompt
    name = prompt("Enter your name: ")
    print(f"Hello, {name}!")

    # Prompt with default value
    age = prompt("Enter your age (default: 18): ", default="18")
    print(f"You are {age} years old.")

    # Prompt with history
    print("\nTry entering some text, then press UP arrow to see history:")
    food = prompt("What's your favorite food? ",
                  history=FileHistory("food_history.txt"))
    print(f"Yum! {food} sounds delicious!")

    # Password input
    from prompt_toolkit import prompt
    password = prompt("Enter a secret password: ", is_password=True)
    print("Password received (but not shown for security)!")

    input("\nPress Enter to continue...")
