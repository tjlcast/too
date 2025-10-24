from .too_task import TooTask


def run():
    """Run the modular AI chat example."""
    print("=== Modular AI Chat Example ===\n")
    app = TooTask()
    app.run()


"""
Run command: python -m src.examples.ai_chat_modular.main
"""
if __name__ == "__main__":
    run()
