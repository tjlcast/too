"""
Custom Key Bindings Example
===========================

This example demonstrates how to create custom key bindings in prompt_toolkit.
"""

from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
import datetime


def run():
    """Run the key bindings example."""
    print("=== Custom Key Bindings Example ===\n")
    
    # Create a KeyBindings object
    bindings = KeyBindings()
    
    # Define custom key bindings
    @bindings.add('c-t')
    def _(event):
        """Insert current time when Ctrl+T is pressed."""
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        event.app.current_buffer.insert_text(current_time)
    
    @bindings.add('c-a')
    def _(event):
        """Insert 'Hello, World!' when Ctrl+A is pressed."""
        event.app.current_buffer.insert_text("Hello, World!")
    
    @bindings.add('c-d')
    def _(event):
        """Exit when Ctrl+D is pressed."""
        event.app.exit(result='exit')
    
    @bindings.add('f1')
    def _(event):
        """Show help when F1 is pressed."""
        print("\nAvailable shortcuts:")
        print("  Ctrl+T - Insert current time")
        print("  Ctrl+A - Insert 'Hello, World!'")
        print("  Ctrl+D - Exit")
        print("  F1     - Show this help")
        print("  Enter  - Submit")
    
    # Create a prompt with custom key bindings
    print("Try these key combinations:")
    print("  Ctrl+T - Insert current time")
    print("  Ctrl+A - Insert 'Hello, World!'")
    print("  Ctrl+D - Exit")
    print("  F1     - Show help")
    print("  Enter  - Submit")
    print()
    
    try:
        text = prompt("Enter text: ", key_bindings=bindings)
        if text != 'exit':
            print(f"You entered: {text}")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    
    input("\nPress Enter to continue...")