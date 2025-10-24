"""
Tool Task Handler for AI Chat Application
=========================================

This module handles tool-based tasks, processing user input,
determining if tools are needed, and executing them.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import os


class ToolTask:
    """
    Handles tool-based tasks in the AI chat application.
    Processes user input, determines if tools are needed,
    and executes them as required.
    """

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

    def register_tool(self, name: str, func):
        """
        Register a tool with the task handler.
        
        Args:
            name: Name of the tool
            func: Function to execute when tool is called
        """
        self.tools[name] = func

    def process_user_input(self, user_input: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Process user input and determine if tools are needed.
        
        Args:
            user_input: The user's input message
            conversation_history: The conversation history
            
        Returns:
            Dictionary with processing results
        """
        # Check if the input is a special command
        if user_input.startswith('$'):
            return self._process_command(user_input, conversation_history)
        
        # For regular messages, add the user input to the conversation history
        result = {
            'requires_tool': False,
            'tool_name': None,
            'tool_args': None,
            'user_message': user_input,
            'conversation_history': conversation_history.copy()
        }
        
        # Add user message to conversation history
        result['conversation_history'].append({
            "role": "user", 
            "content": user_input,
            "timestamp": self._get_current_timestamp()
        })
        
        return result

    def _process_command(self, user_input: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Process special $ commands.
        
        Args:
            user_input: The user's command input
            conversation_history: The conversation history
            
        Returns:
            Dictionary with processing results
        """
        parts = user_input.split(' ', 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        result = {
            'requires_tool': False,
            'tool_name': None,
            'tool_args': None,
            'user_message': user_input,
            'conversation_history': conversation_history.copy()
        }
        
        if command == '$add' and args:
            # Handle $add command with file path
            return self._process_add_command(args, conversation_history)
        elif command == '$help':
            # Handle $help command
            help_text = self._get_help_text()
            self.view.display_system_message(help_text, 'info')
        elif command == '$clear':
            # Clear is handled by the view interface
            pass
        elif command == '$exit':
            # Exit is handled by the main loop
            pass
        elif command == '$reset':
            # Reset is handled by the main loop
            pass
        else:
            # Unknown command
            error_msg = f"Unknown command: {command}. Type $help for available commands."
            self.view.display_system_message(error_msg, 'error')
            
        return result

    def _process_add_command(self, file_path: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Process the $add command to include file content in the conversation.
        
        Args:
            file_path: Path to the file to add
            conversation_history: The conversation history
            
        Returns:
            Dictionary with processing results
        """
        try:
            # Expand user path (e.g., ~/file.txt)
            expanded_path = os.path.expanduser(file_path)
            
            # If it's a relative path, make it relative to the current directory
            if not os.path.isabs(expanded_path):
                expanded_path = os.path.join(os.getcwd(), expanded_path)
            
            # Check if file exists
            if not os.path.exists(expanded_path):
                error_msg = f"File not found: {expanded_path}"
                self.view.display_system_message(error_msg, 'error')
                return {
                    'requires_tool': False,
                    'tool_name': None,
                    'tool_args': None,
                    'user_message': f"Error: {error_msg}",
                    'conversation_history': conversation_history
                }
            
            # Read file content
            with open(expanded_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            
            # Create a message that includes the file content
            message_content = f"File content from {expanded_path}:\n\n{file_content}"
            
            result = {
                'requires_tool': False,
                'tool_name': None,
                'tool_args': None,
                'user_message': message_content,
                'conversation_history': conversation_history.copy()
            }
            
            # Add file content as user message to conversation history
            result['conversation_history'].append({
                "role": "user", 
                "content": message_content,
                "timestamp": self._get_current_timestamp()
            })
            
            success_msg = f"Added content from {expanded_path} to the conversation."
            self.view.display_system_message(success_msg, 'info')
            
            return result
            
        except Exception as e:
            error_msg = f"Error reading file {file_path}: {str(e)}"
            self.view.display_system_message(error_msg, 'error')
            return {
                'requires_tool': False,
                'tool_name': None,
                'tool_args': None,
                'user_message': f"Error: {error_msg}",
                'conversation_history': conversation_history
            }

    def _get_help_text(self) -> str:
        """Get help text for available commands."""
        return """
Available commands:
  $add [path] - Add content from a file to the conversation
  $help       - Show this help message
  $clear      - Clear the current input
  $exit       - Exit the chat
  $reset      - Reset conversation history
        """.strip()

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
        
        response_stream = self.llm.get_response_stream(task_data['conversation_history'])
        
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
        
        for chunk in response_stream:
            self.view.display_ai_message_chunk(chunk)
            full_response += chunk
            
        self.view.display_newline()
        
        # Add AI response to conversation history
        conversation_history.append({
            "role": "assistant",
            "content": full_response,
            "timestamp": self._get_current_timestamp()
        })
        
        result = {
            'response': full_response,
            'conversation_history': conversation_history
        }
        
        return result

    def _get_current_timestamp(self) -> str:
        """
        Get the current timestamp.
        
        Returns:
            Current timestamp as a string
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")