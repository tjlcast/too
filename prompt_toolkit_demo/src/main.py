#!/usr/bin/env python3
"""
Prompt Toolkit Demo Application
================================

A comprehensive demo showcasing the features of the prompt_toolkit library.
This application demonstrates various capabilities including:
- Basic prompts with autocompletion
- Colored prompts and styled output
- Custom key bindings
- Multi-line input
- Progress bars
- Dialogs and menus
- Syntax highlighting
- AI chat simulation
"""

from prompt_toolkit import print_formatted_text
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit import prompt
import os
import sys

# 添加src目录到Python路径，以便能正确导入examples模块
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))


# Demo modules will be added later
def main_menu():
    """Display the main menu and handle user selection."""
    style = Style.from_dict({
        'menu': '#ffffff bg:#ff0000',
        'menu-title': '#ffffff bg:#00aa00 underline',
        'menu-item': '#000000 bg:#aaaaaa',
        'menu-item-selected': '#ffffff bg:#0000aa',
    })

    examples = [
        ('1', 'Basic Prompts', 'basic_prompts'),
        ('2', 'Colored Prompts', 'colored_prompts'),
        ('3', 'Auto Completion', 'completion'),
        ('4', 'Custom Key Bindings', 'key_bindings'),
        ('5', 'Multi-line Input', 'multiline'),
        ('6', 'Progress Bars', 'progress_bars'),
        ('7', 'Dialogs', 'dialogs'),
        ('8', 'Syntax Highlighting', 'syntax_highlighting'),
        ('9', 'AI Chat Simulation', 'ai_chat'),
        ('10', 'User Selection', 'selection'),
        ('11', 'Modular AI Chat', 'ai_chat_modular.main'),
        ('0', 'Exit', 'exit')
    ]

    # Create a completer for the menu options
    option_numbers = [example[0] for example in examples]
    completer = WordCompleter(option_numbers, ignore_case=True)

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_formatted_text(HTML('<b>Prompt Toolkit Comprehensive Demo</b>'))
        print("=" * 50)
        print()

        for key, description, _ in examples:
            print(f"  {key}. {description}")

        print()
        print("=" * 50)

        try:
            choice = prompt(
                HTML('<b>Please select an option:</b> '),
                completer=completer,
                style=style
            ).strip()

            if choice == '0':
                print("Thank you for trying the prompt_toolkit demo!")
                sys.exit(0)

            # Find the matching example
            selected_example = None
            for key, _, module_name in examples:
                if key == choice:
                    selected_example = module_name
                    break

            if selected_example:
                # Import and run the selected example
                try:
                    module = __import__(
                        f'examples.{selected_example}', fromlist=['run'])
                    module.run()
                except ImportError:
                    print(
                        f"Example {selected_example} not found or not implemented yet.")
                    input("Press Enter to continue...")
            else:
                print("Invalid option. Please try again.")
                input("Press Enter to continue...")

        except KeyboardInterrupt:
            print("\\n\\nGoodbye!")
            sys.exit(0)
        except EOFError:
            print("\\n\\nGoodbye!")
            sys.exit(0)


if __name__ == '__main__':
    main_menu()
