from typing import List, Dict, Optional, Any

from .environment.system_message import get_message_message
from .utils.time_util import get_current_timestamp
from .views import ViewInterface
from .llm.llm_provider import LLMProvider
from .llm.llm_proxy import LLMProxy
from .tools.tool_task import ToolTask


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
                    finish_task_executions = []

                    # Display conversation context
                    # Include Pending Tools Execution if any
                    self.view_interface.display_conversation_context(
                        self.conversation_history)

                    # Get user input
                    user_message = self.view_interface.get_user_input()

                    # Check if it's a view-level command (like $pwd, $cd)
                    if user_message.startswith('$'):
                        command_result = self.view_interface.process_command(
                            user_message)
                        if command_result['handled']:
                            # 如果是批准工具的命令，执行工具
                            if 'approved_tools' in command_result:
                                self._execute_approved_tools(
                                    command_result['approved_tools'])
                                finish_task_executions = command_result['approved_tools']
                            else:
                                continue

                    # Check for exit conditions
                    if user_message.lower() in ['quit', 'exit', 'bye'] or user_message == '$exit':
                        self.view_interface.show_goodbye_message()
                        break

                    # Check for reset command
                    if user_message == '$reset':
                        self.conversation_history = []
                        self.view_interface.display_system_message(
                            "Conversation history cleared.", 'info')
                        continue

                    if not user_message:
                        continue

                    if len(self.conversation_history) == 0:
                        self.conversation_history.append({
                            "role": "system",
                            "content": get_message_message(),
                            "timestamp": get_current_timestamp()
                        })

                    # Check if we have tool execution results to process
                    if finish_task_executions:
                        # Process tools input
                        task_data = self.llm_proxy.process_tools_input(
                            finish_task_executions, self.conversation_history)
                    else:
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

                    # 更新对话历史
                    self.conversation_history = processing_result['conversation_history']

                    # 保存对话交换
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

    def _execute_approved_tools(self, approved_tools: List[Dict[str, Any]]):
        """
        执行用户批准的工具
        """
        for tool in approved_tools:
            if "__callback" in tool:
                try:
                    result = tool["__callback"]()
                    tool["__execution_result"] = result
                    self.view_interface.display_system_message(
                        f"Tool execution result: {result[:32]}", 'info')
                except Exception as e:
                    self.view_interface.display_system_message(
                        f"Error executing tool: {str(e)}", 'error')

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
                    f"[User] [{user_entry['timestamp']}]: {user_entry['content']}\n")
                f.write(
                    f"[AI] [{ai_entry['timestamp']}]: {ai_entry['content']}\n")
                f.write("\n")  # Empty line between exchanges
        except Exception as e:
            print(f"Failed to save conversation exchange: {e}")
