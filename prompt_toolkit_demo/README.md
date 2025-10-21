# Prompt Toolkit Comprehensive Demo

A comprehensive demonstration of the [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) library features.

## Overview

This project showcases the powerful features of the prompt_toolkit library, which is used to build rich, interactive command-line applications in Python. The demo includes examples of:

- Basic prompts with history
- Colored and styled prompts
- Auto-completion (word, fuzzy, path)
- Custom key bindings
- Multi-line input with validation
- Progress bars
- Dialogs and message boxes
- Syntax highlighting

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required dependencies:

```bash
pip install prompt_toolkit pygments
```

## Running the Demo

Navigate to the `src` directory and run:

```bash
python main.py
```

Then follow the on-screen menu to explore different examples.

## Examples

### 1. Basic Prompts
Demonstrates simple text input, password input, and input with history.

### 2. Colored Prompts
Shows how to style prompts and output with colors and formatting using HTML and ANSI codes.

### 3. Auto Completion
Examples of different auto-completion mechanisms:
- Word completion
- Fuzzy word completion
- Path completion
- Nested completion

### 4. Custom Key Bindings
How to create custom keyboard shortcuts for enhanced user experience.

### 5. Multi-line Input
Working with multi-line text input with custom key bindings and validation.

### 6. Progress Bars
Various progress bar implementations including parallel task processing.

### 7. Dialogs
Different types of dialogs:
- Message dialogs
- Input dialogs
- Yes/No dialogs
- Button dialogs

### 8. Syntax Highlighting
Code input with real-time syntax highlighting for various programming languages.

## Features Demonstrated

- Rich text formatting
- Keyboard shortcuts
- History management
- Input validation
- Concurrent task processing
- Cross-platform compatibility

## Learning Outcomes

By exploring this demo, you will learn how to:

1. Create interactive command-line applications with enhanced user experience
2. Implement various input methods and validations
3. Add visual enhancements like colors, progress bars, and dialogs
4. Handle complex user interactions with custom key bindings
5. Provide intelligent auto-completion for user inputs
6. Process multiple tasks with visual feedback

## Project Structure

```
src/
├── main.py              # Main application and menu system
├── examples/            # Individual example modules
│   ├── basic_prompts.py
│   ├── colored_prompts.py
│   ├── completion.py
│   ├── key_bindings.py
│   ├── multiline.py
│   ├── progress_bars.py
│   ├── dialogs.py
│   └── syntax_highlighting.py
```

## Dependencies

- [prompt_toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) - The main library
- [pygments](https://pygments.org/) - For syntax highlighting (optional)

## Resources

- [Official prompt_toolkit documentation](https://python-prompt-toolkit.readthedocs.io/)
- [GitHub repository](https://github.com/prompt-toolkit/python-prompt-toolkit)

## License

This demo is provided for educational purposes. Feel free to use and modify the code as needed.