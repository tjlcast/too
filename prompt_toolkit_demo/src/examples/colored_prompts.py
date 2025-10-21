"""
Colored Prompts Example
=======================

This example demonstrates how to create styled prompts and output with prompt_toolkit.
"""

from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML, ANSI
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator, ValidationError


class NumberValidator(Validator):
    def validate(self, document):
        text = document.text

        if text and not text.isdigit():
            i = 0

            # Get index of first non-digit character.
            for i, c in enumerate(text):
                if not c.isdigit():
                    break

            raise ValidationError(message='This input contains non-numeric characters',
                                  cursor_position=i)


def run():
    """Run the colored prompts example."""
    print("=== Colored Prompts Example ===\n")

    # Using HTML formatted text
    answer = prompt(HTML('<b>Enter your name:</b> '))
    print(f"Hello, {answer}!")

    # Using custom styles
    style = Style.from_dict({
        'prompt': '#ansigreen',
        'warning': '#ansired',
        'input': '#ansiblue'
    })

    number = prompt([('class:prompt', 'Enter a number: ')],
                    style=style,
                    validator=NumberValidator())
    print(f"You entered: {number}")

    # Multiline colored output
    print(HTML('\n<b><style fg="ansiyellow">This is a yellow bold text!</style></b>'))
    print(HTML('<aaa fg="ansipurple">This is purple text using inline style!</aaa>'))

    # ANSI colors example
    print(ANSI('\x1b[31mThis is red text using ANSI escape codes\x1b[0m'))
    print(ANSI('\x1b[1m\x1b[4mBold underlined text using ANSI\x1b[0m'))

    input("\nPress Enter to continue...")
