"""
Syntax Highlighting Example
===========================

This example demonstrates syntax highlighting capabilities in prompt_toolkit.
"""

from prompt_toolkit import prompt
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.formatted_text import HTML
from pygments.lexers import PythonLexer, JavascriptLexer, HtmlLexer
from pygments.style import Style
from pygments.token import Token


def run():
    """Run the syntax highlighting example."""
    print("=== Syntax Highlighting Example ===\n")

    # Check if pygments is installed
    try:
        import pygments
    except ImportError:
        print("Pygments is not installed. Install it with: pip install pygments")
        input("\nPress Enter to continue...")
        return

    # Simple Python syntax highlighting in prompt
    print("1. Python syntax highlighting:")
    print("Enter Python code (press Enter to finish):")

    try:
        text = prompt(
            '> ',
            lexer=PygmentsLexer(PythonLexer),
            multiline=True
        )
        print(f"You entered:\n{text}\n")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")

    # JavaScript syntax highlighting
    print("2. JavaScript syntax highlighting:")
    print("Enter JavaScript code (press Enter to finish):")

    try:
        text = prompt(
            'js> ',
            lexer=PygmentsLexer(JavascriptLexer),
            multiline=True
        )
        print(f"You entered:\n{text}\n")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")

    # HTML syntax highlighting
    print("3. HTML syntax highlighting:")
    print("Enter HTML code (press Enter to finish):")

    try:
        text = prompt(
            'html> ',
            lexer=PygmentsLexer(HtmlLexer),
            multiline=True
        )
        print(f"You entered:\n{text}\n")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")

    # Display formatted code with syntax highlighting
    print("4. Display formatted code with syntax highlighting:")
    python_code = '''
def hello_world(name):
    """Print a greeting message."""
    print(f"Hello, {name}!")

if __name__ == "__main__":
    hello_world("World")
'''

    from prompt_toolkit.shortcuts import print_formatted_text
    from pygments import highlight
    from pygments.formatters import TerminalFormatter

    print("Here's a sample Python code with syntax highlighting:")
    print_formatted_text(
        HTML(f"<ansiwhite>{python_code}</ansiwhite>")
    )

    input("\nPress Enter to continue...")
