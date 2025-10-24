

from typing import List, Dict

from .utils.time_util import get_current_timestamp
from .views import ViewInterface
from .llm.llm_provider import LLMProvider
from .llm.llm_proxy import LLMProxy
from .tool_task import ToolTask


class TooTask:
    """
    Main class for the modular AI chat application.
    Integrates ViewInterface, LLMProvider, and ToolTask components.
    """

    def __init__(self):
        """Initialize the modular AI chat application."""
        self.view_interface = ViewInterface()
        self.llm_provider = LLMProvider()
        self.tool_task = ToolTask(self.view_interface, self.llm_provider)
        self.llm_proxy = LLMProxy(self.view_interface, self.llm_provider)
        self.conversation_history: List[Dict[str, str]] = []

    def run(self):
        """Run the modular AI chat application."""
        # Display initial instructions
        self.view_interface.show_instructions()

        # Main conversation loop
        try:
            while True:
                try:
                    # Display conversation context
                    self.view_interface.display_conversation_context(
                        self.conversation_history)

                    # Get user input
                    user_message = self.view_interface.get_user_input()

                    # Check for exit conditions
                    if user_message.lower() in ['quit', 'exit', 'bye']:
                        self.view_interface.show_goodbye_message()
                        break

                    if not user_message:
                        continue

                    # Process user input
                    task_data = self.llm_proxy.process_user_input(
                        user_message, self.conversation_history)

                    # Execute task
                    execution_result = self.llm_proxy.execute_task(
                        task_data)

                    # Process and display response
                    processing_result = self.llm_proxy.process_response(
                        execution_result['response_stream'],
                        execution_result['conversation_history']
                    )

                    # Update conversation history
                    self.conversation_history = processing_result['conversation_history']

                    # Save conversation (in a real app, this might be done differently)
                    self._save_conversation_exchange(
                        task_data, processing_result)

                    self.view_interface.display_newline()

                except KeyboardInterrupt:
                    self.view_interface.show_interrupt_message()
                    break
                except EOFError:
                    self.view_interface.show_interrupt_message()
                    break

        finally:
            self.view_interface.wait_for_enter()

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
                    "timestamp": get_current_timestamp()
                }

                f.write(
                    f"[User] [{user_entry['timestamp']}]: {user_entry['content']}\\n")
                f.write(
                    f"[AI] [{ai_entry['timestamp']}]: {ai_entry['content']}\\n")
                f.write("\\n")  # Empty line between exchanges
        except Exception as e:
            print(f"Failed to save conversation exchange: {e}")
