"""
Modular AI Chat Application
===========================

This is a modular implementation of the AI chat application,
organized into three main components:
1. ViewInterface - Handles UI interactions
2. LLMProvider - Manages AI model interactions
3. ToolTask - Processes tasks and handles tool execution
"""

from typing import List, Dict
import os

# from views import ViewInterface
# from llm_provider import LLMProvider
# from tool_task import ToolTask
from .views import ViewInterface
from .llm_provider import LLMProvider
from .tool_task import ToolTask


class ModularAIChat:
    """
    Main class for the modular AI chat application.
    Integrates ViewInterface, LLMProvider, and ToolTask components.
    """

    def __init__(self):
        """Initialize the modular AI chat application."""
        self.view = ViewInterface()
        self.llm_provider = LLMProvider()
        self.task_handler = ToolTask(self.view, self.llm_provider)
        self.conversation_history: List[Dict[str, str]] = []

    def run(self):
        """Run the modular AI chat application."""
        # Display initial instructions
        self.view.show_instructions()

        # Main conversation loop
        try:
            while True:
                try:
                    # Display conversation context
                    self.view.display_conversation_context(
                        self.conversation_history)

                    # Get user input
                    user_message = self.view.get_user_input()

                    # Check for exit conditions
                    if user_message.lower() in ['quit', 'exit', 'bye']:
                        self.view.show_goodbye_message()
                        break

                    if not user_message:
                        continue

                    # Process user input
                    task_data = self.task_handler.process_user_input(
                        user_message, self.conversation_history)

                    # Execute task
                    execution_result = self.task_handler.execute_task(
                        task_data)

                    # Process and display response
                    processing_result = self.task_handler.process_response(
                        execution_result['response_stream'],
                        execution_result['conversation_history']
                    )

                    # Update conversation history
                    self.conversation_history = processing_result['conversation_history']

                    # Save conversation (in a real app, this might be done differently)
                    self._save_conversation_exchange(
                        task_data, processing_result)

                    self.view.display_newline()

                except KeyboardInterrupt:
                    self.view.show_interrupt_message()
                    break
                except EOFError:
                    self.view.show_interrupt_message()
                    break

        finally:
            self.view.wait_for_enter()

    def _save_conversation_exchange(self, task_data: Dict, processing_result: Dict):
        """
        Save the conversation exchange to a file.

        Args:
            task_data: Data about the user's task
            processing_result: Results of processing the AI response
        """
        try:
            with open('.ai_chat_history', 'a', encoding='utf-8') as f:
                # Last user message
                user_entry = task_data['conversation_history'][-1]
                ai_entry = {
                    "role": "assistant",
                    "content": processing_result['response'],
                    "timestamp": self.task_handler._get_current_timestamp()
                }

                f.write(
                    f"[User] [{user_entry['timestamp']}]: {user_entry['content']}\\n")
                f.write(
                    f"[AI] [{ai_entry['timestamp']}]: {ai_entry['content']}\\n")
                f.write("\\n")  # Empty line between exchanges
        except Exception as e:
            print(f"Failed to save conversation exchange: {e}")


def run():
    """Run the modular AI chat example."""
    print("=== Modular AI Chat Example ===\\n")
    app = ModularAIChat()
    app.run()


if __name__ == "__main__":
    run()
