"""
Modular AI Chat Application
===========================

This is a modular implementation of the AI chat application,
organized into three main components:
1. ViewInterface - Handles UI interactions
2. LLMProvider - Manages AI model interactions
3. ToolTask - Processes tasks and handles tool execution
"""


from .too_task import TooTask


def run():
    """Run the modular AI chat example."""
    print("=== Modular AI Chat Example ===\\n")
    app = TooTask()
    app.run()


if __name__ == "__main__":
    run()
