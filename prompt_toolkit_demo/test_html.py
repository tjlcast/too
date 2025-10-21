#!/usr/bin/env python3

from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import print_formatted_text

def main():
    print("Testing HTML formatted text rendering:")
    print("=" * 40)
    
    # Test 1: Direct print of HTML object
    print("Test 1 - Direct print:")
    print_formatted_text(HTML('<ansiblue>AI:</ansiblue> Hello, World!'))
    
    # Test 2: Using print_formatted_text function
    print("\nTest 2 - Using print_formatted_text:")
    print_formatted_text(HTML('<ansigreen>You:</ansigreen> Hello, World!'))
    
    # Test 3: Mixed colors
    print("\nTest 3 - Mixed colors:")
    print_formatted_text(HTML('<ansired>Red</ansired> <ansigreen>Green</ansigreen> <ansiblue>Blue</ansiblue>'))
    
    print("\n" + "=" * 40)
    print("If you see colored text above, HTML formatting works correctly.")
    print("If you see the literal HTML tags, there might be an issue with your terminal.")

if __name__ == "__main__":
    main()