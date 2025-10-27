
from datetime import datetime
from typing import Any, Dict, List

from ..environment.user_message_environment_detail import get_environment_details
from ..environment.environment_proxy import EnvironmentProxy

from ..utils.tpl_util import replace_template_vars

from ..utils.time_util import get_current_timestamp


class LLMProxy:
    def __init__(self, view_interface, llm_provider):
        """
        Initialize the tool task handler.

        Args:
            view_interface: The view interface for displaying information
            llm_provider: The LLM provider for interacting with AI models
        """
        self.view = view_interface
        self.llm = llm_provider
        self.tools = {}  # Dictionary to hold available tools

    def process_user_input(self, user_input: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Process user input and determine if tools are needed.

        Args:
            user_input: The user's input message
            conversation_history: The conversation history

        Returns:
            Dictionary with processing results
        """
        # For now, we'll just add the user input to the conversation history
        # In a more complex implementation, this would analyze the input
        # to determine if tools are needed

        result = {
            'requires_tool': False,
            'tool_name': None,
            'tool_args': None,
            'user_message': user_input,
            'conversation_history': conversation_history.copy()
        }

        # Build user task entry
        env_proxy = EnvironmentProxy()
        details = get_environment_details(env_proxy)
        user_message_tpl = """<task>{{user_task}}</task>\n{{env_details}}
        """
        user_input = replace_template_vars(
            user_message_tpl, {"{{user_task}}": user_input, "{{env_details}}": details})

        # Add user message to conversation history
        result['conversation_history'].append({
            "role": "user",
            "content": user_input,
            "timestamp": get_current_timestamp()
        })

        return result

    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task, potentially using tools.

        Args:
            task_data: Data about the task to execute

        Returns:
            Dictionary with execution results
        """
        # For now, we'll just get a response from the LLM
        # In a more complex implementation, this would check if tools are needed
        # and execute them before or after getting an LLM response

        response_stream = self.llm.get_response_stream(
            task_data['conversation_history'])

        result = {
            'response_stream': response_stream,
            'conversation_history': task_data['conversation_history']
        }

        return result

    def process_response(self, response_stream, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Process the AI response stream.

        Args:
            response_stream: Stream of response chunks from the LLM
            conversation_history: The conversation history

        Returns:
            Dictionary with processing results
        """
        full_response = ""
        self.view.display_ai_header()

        # 收集流式响应的token
        for chunk in response_stream:
            self.view.display_ai_message_chunk(chunk)
            full_response += chunk

        self.view.display_newline()

        # Add AI response to conversation history
        conversation_history.append({
            "role": "assistant",
            "content": full_response,
            "timestamp": get_current_timestamp()
        })

        result = {
            'response': full_response,
            'conversation_history': conversation_history
        }

        return result
