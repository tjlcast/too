"""
Auto Completion Example
=======================

This example demonstrates various auto-completion features in prompt_toolkit.
"""

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, FuzzyWordCompleter, PathCompleter
import os


def run():
    """Run the auto completion example."""
    print("=== Auto Completion Example ===\n")
    
    # Simple word completion
    print("1. Simple word completion:")
    print("Available words: cat, dog, elephant, fox, giraffe, horse")
    animal_completer = WordCompleter(['cat', 'dog', 'elephant', 'fox', 'giraffe', 'horse'])
    animal = prompt("Choose an animal: ", completer=animal_completer)
    print(f"You chose: {animal}\n")
    
    # Fuzzy word completion
    print("2. Fuzzy word completion:")
    print("Try typing 'elpt' to match 'elephant'")
    fuzzy_completer = FuzzyWordCompleter(['cat', 'dog', 'elephant', 'fox', 'giraffe', 'horse'])
    fuzzy_animal = prompt("Choose an animal (fuzzy): ", completer=fuzzy_completer)
    print(f"You chose: {fuzzy_animal}\n")
    
    # Path completion
    print("3. Path completion:")
    print("Try navigating your filesystem (use TAB to autocomplete)")
    path_completer = PathCompleter(expanduser=True)
    path = prompt("Enter a path: ", completer=path_completer)
    print(f"You entered: {path}\n")
    
    # Nested completion
    commands = {
        'git': ['status', 'commit', 'push', 'pull', 'clone'],
        'docker': ['run', 'build', 'ps', 'images', 'stop'],
        'ls': ['-l', '-a', '-la']
    }
    
    print("4. Nested completion:")
    print("Available commands: git, docker, ls")
    command_words = list(commands.keys()) + [subitem for sublist in commands.values() for subitem in sublist]
    command_completer = WordCompleter(command_words, sentence=True)
    command = prompt("Enter a command: ", completer=command_completer)
    print(f"You entered: {command}\n")
    
    input("Press Enter to continue...")