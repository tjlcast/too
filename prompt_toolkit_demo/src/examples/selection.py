"""
Selection Example
=================

This example demonstrates how to create user selection interfaces with prompt_toolkit.
"""

from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import radiolist_dialog, checkboxlist_dialog, yes_no_dialog
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window, HSplit, VSplit
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.application import Application
from prompt_toolkit.widgets import RadioList, CheckboxList, Box, Frame


def create_radio_selection(title, options, default=None):
    """Create a custom radio list selection interface."""
    radio_list = RadioList(options)
    
    # Create key bindings
    kb = KeyBindings()

    @kb.add('c-c')
    @kb.add('c-q')
    def _(event):
        """Cancel with Ctrl-C or Ctrl-Q."""
        event.app.exit(result=None)

    @kb.add('enter', eager=True)
    def _(event):
        """Accept selection with Enter."""
        event.app.exit(result=radio_list.current_value)

    # Build the layout
    body = HSplit([
        Window(FormattedTextControl(title), height=1),
        Frame(Box(radio_list, padding=1)),
        Window(
            FormattedTextControl(
                HTML("Press <b>Enter</b> to confirm, <b>Ctrl-C</b> to cancel.")
            ),
            height=1
        )
    ])

    application = Application(
        layout=Layout(body),
        key_bindings=kb,
        mouse_support=True,
        full_screen=False
    )
    
    return application.run()


def create_checkbox_selection(title, options, default_values=None):
    """Create a custom checkbox list selection interface."""
    if default_values is None:
        default_values = []
    
    checkbox_list = CheckboxList(options)
    
    # Set initial values
    for i, (value, _) in enumerate(options):
        if value in default_values:
            checkbox_list.current_values.append(value)
    
    # Create key bindings
    kb = KeyBindings()

    @kb.add('c-c')
    @kb.add('c-q')
    def _(event):
        """Cancel with Ctrl-C or Ctrl-Q."""
        event.app.exit(result=None)

    @kb.add('enter', eager=True)
    def _(event):
        """Accept selection with Enter."""
        event.app.exit(result=checkbox_list.current_values)

    @kb.add('space')
    def _(event):
        """Toggle selection with Space."""
        checkbox_list._handle_enter()
        # Keep the focus
        return

    # Build the layout
    body = HSplit([
        Window(FormattedTextControl(title), height=1),
        Frame(Box(checkbox_list, padding=1)),
        Window(
            FormattedTextControl(
                HTML("Press <b>Space</b> to toggle, <b>Enter</b> to confirm, <b>Ctrl-C</b> to cancel.")
            ),
            height=1
        )
    ])

    application = Application(
        layout=Layout(body),
        key_bindings=kb,
        mouse_support=True,
        full_screen=False
    )
    
    return application.run()


def run():
    """Run the selection example."""
    print("=== Enhanced Selection Example ===\n")

    # 1. Simple selection with WordCompleter
    print("1. Simple selection with auto-completion:")
    options = ['Python', 'JavaScript', 'Java', 'C++', 'Go', 'Rust', 'Swift']
    completer = WordCompleter(options, ignore_case=True)
    
    language = prompt(
        "Choose your favorite programming language: ",
        completer=completer
    )
    print(f"You selected: {language}\n")

    # 2. Custom Radio list selection
    print("2. Custom Radio List Selection:")
    color_options = [
        ("#FF0000", "Red"),
        ("#00FF00", "Green"), 
        ("#0000FF", "Blue"),
        ("#FFFF00", "Yellow"),
        ("#FF00FF", "Magenta"),
        ("#00FFFF", "Cyan"),
    ]
    
    color_result = create_radio_selection(
        "What is your favorite color?",
        color_options
    )
    
    if color_result:
        print(f"You selected color: {color_result}")
    else:
        print("Selection cancelled.")
    print()

    # 3. Custom Checkbox list selection
    print("3. Custom Checkbox List Selection:")
    food_options = [
        ("pizza", "Pizza"),
        ("burger", "Burger"),
        ("sushi", "Sushi"), 
        ("tacos", "Tacos"),
        ("pasta", "Pasta"),
        ("salad", "Salad"),
    ]
    
    food_result = create_checkbox_selection(
        "Select one or more favorite foods:",
        food_options
    )
    
    if food_result:
        print(f"You selected: {', '.join(food_result)}")
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
    print(f"You selected: {choice}\n")

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
        print("\nOperation cancelled.")
    print()

    # 6. Enhanced radio list with custom interface
    print("6. Enhanced Selection Interface:")
    enhanced_options = [
        ("beginner", "👶 Beginner"),
        ("intermediate", "🚀 Intermediate"), 
        ("advanced", "🔥 Advanced"),
        ("expert", "🏆 Expert")
    ]
    
    level_result = create_radio_selection(
        "What is your programming skill level?",
        enhanced_options
    )
    
    if level_result:
        print(f"You selected: {level_result}")
    else:
        print("Selection cancelled.")
    print()

    # 7. Simple yes/no dialog
    print("7. Yes/No Dialog:")
    confirm = yes_no_dialog(
        title="Confirmation",
        text="Do you want to proceed?"
    ).run()
    
    if confirm:
        print("You chose to proceed!")
    else:
        print("You chose to cancel.")
    print()

    input("Press Enter to continue...")


if __name__ == "__main__":
    run()