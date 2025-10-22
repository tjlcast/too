"""
Selection Example
=================

This example demonstrates how to create user selection interfaces with prompt_toolkit.
"""

from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import radiolist_dialog, checkboxlist_dialog
from prompt_toolkit.completion import WordCompleter


def run():
    """Run the selection example."""
    print("=== Selection Example ===\\n")

    # 1. Simple selection with WordCompleter
    print("1. Simple selection with auto-completion:")
    options = ['Python', 'JavaScript', 'Java', 'C++', 'Go', 'Rust', 'Swift']
    completer = WordCompleter(options, ignore_case=True)
    
    language = prompt(
        "Choose your favorite programming language: ",
        completer=completer
    )
    print(f"You selected: {language}\\n")

    # 2. Radio list dialog
    print("2. Radio list dialog:")
    result = radiolist_dialog(
        title="Radio List Dialog",
        text="What is your favorite color?",
        values=[
            ("#FF0000", "Red"),
            ("#00FF00", "Green"),
            ("#0000FF", "Blue"),
            ("#FFFF00", "Yellow"),
            ("#FF00FF", "Magenta"),
            ("#00FFFF", "Cyan"),
        ],
    ).run()
    
    if result:
        print(f"You selected color: {result}")
    else:
        print("Selection cancelled.")
    print()

    # 3. Checkbox list dialog
    print("3. Checkbox list dialog:")
    result = checkboxlist_dialog(
        title="Checkbox List Dialog",
        text="Select one or more favorite foods:",
        values=[
            ("pizza", "Pizza"),
            ("burger", "Burger"),
            ("sushi", "Sushi"),
            ("tacos", "Tacos"),
            ("pasta", "Pasta"),
            ("salad", "Salad"),
        ],
    ).run()
    
    if result:
        print(f"You selected: {', '.join(result)}")
    else:
        print("Selection cancelled.")
    print()

    # 4. Styled selection
    print("4. Styled selection:")
    style = Style.from_dict({
        'prompt': '#ansigreen',
        'selection': '#ansiblue',
        'choice': '#ansiyellow'
    })
    
    options = ['Option A', 'Option B', 'Option C', 'Option D']
    completer = WordCompleter(options)
    
    choice = prompt(
        [('class:prompt', 'Please select an option: ')],
        completer=completer,
        style=style
    )
    print(f"You selected: {choice}\\n")

    # 5. Selection with validation
    from prompt_toolkit.validation import Validator, ValidationError
    
    class OptionValidator(Validator):
        def __init__(self, valid_options):
            self.valid_options = valid_options

        def validate(self, document):
            text = document.text
            if text not in self.valid_options:
                raise ValidationError(
                    message=f'Please choose one of: {", ".join(self.valid_options)}',
                    cursor_position=len(text)
                )

    print("5. Selection with validation:")
    valid_options = ['yes', 'no', 'maybe']
    completer = WordCompleter(valid_options)
    
    try:
        answer = prompt(
            "Do you like prompt_toolkit? (yes/no/maybe): ",
            completer=completer,
            validator=OptionValidator(valid_options)
        )
        print(f"You answered: {answer}")
    except KeyboardInterrupt:
        print("\\nOperation cancelled.")
    print()

    input("Press Enter to continue...")