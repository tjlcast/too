"""
Multi-line Input Example
========================

This example demonstrates how to handle multi-line input with prompt_toolkit.
"""

from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML


def run():
    """Run the multi-line input example."""
    print("=== Multi-line Input Example ===\n")

    # Simple multi-line input
    print("1. Simple multi-line input:")
    print("Press [Meta+Enter] or [Esc] followed by [Enter] to accept input.")
    text = prompt("Enter multi-line text: ", multiline=True)
    print(f"You entered:\n{text}\n")

    # Multi-line input with custom key bindings
    print("2. Multi-line input with custom key bindings:")

    bindings = KeyBindings()

    @bindings.add('c-c')
    def _(event):
        """Clear the current input."""
        event.app.current_buffer.reset()

    @bindings.add('c-s')
    def _(event):
        """Save and submit the current input."""
        event.app.exit(result=event.app.current_buffer.text)

    print("Available key bindings:")
    print("  [Enter]     - New line")
    print("  [Alt+Enter] - Submit")
    print("  Ctrl+C      - Clear input")
    print("  Ctrl+S      - Save and submit")
    print()

    try:
        text = prompt(
            HTML('<b>Enter your story:</b> '),
            multiline=True,
            key_bindings=bindings
        )
        print(f"Your story:\n{text}\n")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")

    # Multi-line with custom validator
    from prompt_toolkit.validation import Validator, ValidationError

    class PythonValidator(Validator):
        def validate(self, document):
            text = document.text
            if text and not text.endswith(':'):
                # Just a simple check for demo purposes
                if 'def ' in text and not text.strip().endswith(':'):
                    raise ValidationError(
                        message='Function definitions should end with a colon (:)',
                        cursor_position=len(text))

    print("3. Multi-line with Python code validation:")
    print("Try entering a function definition (should end with colon)")
    try:
        code = prompt(
            "Enter Python code: ",
            multiline=True,
            validator=PythonValidator()
        )
        print(f"You entered:\n{code}\n")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")

    input("Press Enter to continue...")
