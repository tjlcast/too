"""
Dialogs Example
===============

This example demonstrates how to create dialogs with prompt_toolkit.
"""

from prompt_toolkit.shortcuts import message_dialog, input_dialog, yes_no_dialog, button_dialog
from prompt_toolkit.formatted_text import HTML


def run():
    """Run the dialogs example."""
    print("=== Dialogs Example ===\n")
    
    # Message dialog
    print("1. Message dialog:")
    message_dialog(
        title='Information',
        text='This is a simple message dialog.\nPress OK to continue.'
    ).run()
    
    # Input dialog
    print("\n2. Input dialog:")
    name = input_dialog(
        title='Input Dialog',
        text='Please enter your name:'
    ).run()
    
    if name:
        print(f"Hello, {name}!")
    else:
        print("No name entered.")
    
    # Yes/No dialog
    print("\n3. Yes/No dialog:")
    result = yes_no_dialog(
        title='Confirmation',
        text='Do you want to continue?'
    ).run()
    
    if result:
        print("You chose to continue!")
    else:
        print("You chose not to continue.")
    
    # Button dialog
    print("\n4. Button dialog:")
    choice = button_dialog(
        title='Button Dialog',
        text='Select your favorite color:',
        buttons=[
            ('Red', '#FF0000'),
            ('Green', '#00FF00'),
            ('Blue', '#0000FF'),
            ('Cancel', None)
        ]
    ).run()
    
    if choice:
        print(f"You selected color: {choice}")
    else:
        print("Selection cancelled.")
    
    # Complex dialog with HTML
    print("\n5. Complex dialog with HTML:")
    result = yes_no_dialog(
        title=HTML('<style bg="blue fg="white">Important Confirmation</style>'),
        text=HTML('Do you want to delete <b>all</b> files?\n'
                  '<red>This action cannot be undone!</red>')
    ).run()
    
    if result:
        message_dialog(
            title='Success',
            text=HTML('<green>Files deleted successfully!</green>')
        ).run()
    else:
        message_dialog(
            title='Cancelled',
            text='Operation was cancelled.'
        ).run()
    
    input("\nPress Enter to continue...")