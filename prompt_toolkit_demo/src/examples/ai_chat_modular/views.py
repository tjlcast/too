"""
View Interface for AI Chat Application
=====================================

This module handles all UI interactions including displaying messages,
getting user input, and showing status updates.
"""

import os
from typing import Any, List, Dict
from datetime import datetime

from prompt_toolkit import print_formatted_text, prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
from prompt_toolkit.completion import NestedCompleter, PathCompleter
from prompt_toolkit.widgets import Frame, Box
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout import Layout
from prompt_toolkit.application import Application
import asyncio


class ViewInterface:
    """
    Handles all user interface interactions for the AI chat application.
    Uses prompt_toolkit for enhanced terminal interactions.
    """

    def __init__(self):
        """Initialize the view interface with styles and key bindings."""
        self.style = Style.from_dict({
            'prompt': '#00ff00 bold',     # Green prompt
            'ai': '#0088ff',              # Blue AI responses
            'info': '#ffff00',            # Yellow info text
            'error': '#ff0000 bold',      # Red error text
            'user': '#ff00ff',            # Magenta user messages
            'context': '#aaaaaa italic',  # Gray context info
            'pending-tools-frame': '#ffff00',  # Yellow border for pending tools
        })

        self.bindings = self._setup_key_bindings()
        self.history_file = '.ai_chat_history'
        self.completer = self._create_completer()
        self.pending_tools = []  # 存储待批准的工具列表

    def _setup_key_bindings(self) -> KeyBindings:
        """Set up custom key bindings for the chat interface."""
        bindings = KeyBindings()

        @bindings.add('c-c')
        def _(event):
            """Clear the current input or exit."""
            buffer = event.app.current_buffer
            if buffer.text:
                buffer.reset()
            else:
                event.app.exit(result=None)

        @bindings.add('c-d')
        def _(event):
            """Exit the chat."""
            event.app.exit(result=None)

        return bindings

    def _create_completer(self):
        """Create a completer with support for $ commands and file paths."""
        # Create a path completer for the current directory
        path_completer = PathCompleter(
            expanduser=True,
            file_filter=None,
            min_input_len=0,
            get_paths=None
        )
        
        # Create a nested completer with $ commands
        completer = NestedCompleter.from_nested_dict({
            '$add': path_completer,
            '$help': None,
            '$clear': None,
            '$exit': None,
            '$reset': None,
            '$pwd': None,
            '$cd': path_completer,
            '$approve': None,  # 添加批准工具的命令
        })
        
        return completer

    def display_system_message(self, message: str, msg_type: str = 'info'):
        """
        Display a system message to the user.

        Args:
            message: The message to display
            msg_type: Type of message (info, error, context)
        """
        if msg_type == 'info':
            print_formatted_text(HTML(f'<ansiwhite>{message}</ansiwhite>'))
        elif msg_type == 'error':
            print_formatted_text(HTML(f'<ansired>{message}</ansired>'))
        elif msg_type == 'context':
            print_formatted_text(HTML(f'<ansicyan>{message}</ansicyan>'))

    def display_conversation_context(self, messages: List[Dict[str, str]]):
        """
        Display context information about the conversation.

        Args:
            messages: List of message dictionaries with role and content
        """
        if messages:
            user_messages = [m for m in messages if m["role"] == "user"]
            ai_messages = [m for m in messages if m["role"] == "assistant"]
            context_msg = f"Context: Conversation history - {len(user_messages)} user messages, {len(ai_messages)} AI responses"
            self.display_system_message(context_msg, 'context')
        else:
            self.display_system_message(
                "Context: Starting new conversation", 'context')

        # Show current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.display_system_message(f"Current time: {current_time}", 'context')
        
        # Show current working directory
        current_dir = os.getcwd()
        self.display_system_message(f"Current directory: {current_dir}", 'context')

        # 显示待批准的工具列表
        if self.pending_tools:
            # 打印带黄色边框的待批准工具列表
            border_line = "+" + "=" * 48 + "+"
            separator_line = "+" + "-" * 48 + "+"
            self.display_system_message(border_line, 'info')
            header = "Pending tools for approval:"
            self.display_system_message(f"| {header.ljust(46)} |", 'info')
            self.display_system_message(border_line, 'info')
            for i, tool in enumerate(self.pending_tools):
                tool_desc = f"  {i+1}. {tool.get('desc', 'Unknown tool')}"
                # 确保文本适合边框内
                if len(tool_desc) > 46:
                    tool_desc = tool_desc[:43] + "..."
                self.display_system_message(f"| {tool_desc.ljust(46)} |", 'info')
            self.display_system_message(separator_line, 'info')
            footer = "Type '$approve' to execute all pending tools"
            self.display_system_message(f"| {footer.ljust(46)} |", 'info')
            self.display_system_message(border_line, 'info')

    def display_ai_header(self):
        """Display the AI response header."""
        print_formatted_text(
            HTML('<ansiblue>AI:</ansiblue> '), end='', flush=True)

    def display_ai_message_chunk(self, chunk: str):
        """
        Display a chunk of AI response.

        Args:
            chunk: A part of the AI response to display
        """
        print(chunk, end='', flush=True)

    def display_newline(self):
        """Display a newline character."""
        print()

    def display_user_message(self, message: str):
        """
        Display a user message.

        Args:
            message: The user message to display
        """
        print_formatted_text(HTML(f'<ansigreen>You:</ansigreen> {message}'))

    def display_ai_message(self, message: str):
        """
        Display a complete AI message.

        Args:
            message: The AI message to display
        """
        print_formatted_text(HTML(f'<ansiblue>AI:</ansiblue> {message}'))

    def get_user_input(self) -> str:
        """
        Get input from the user with command completion support.

        Returns:
            User input as a string
        """
        user_input = prompt(
            HTML('<ansigreen>You:</ansigreen> '),
            multiline=True,
            key_bindings=self.bindings,
            style=self.style,
            completer=self.completer,
            history=FileHistory(self.history_file) if os.path.exists(
                self.history_file) else None
        )
        return user_input.strip()

    def process_command(self, user_input: str) -> Dict[str, Any]:
        """
        Process special $ commands that affect the view layer.
        
        Args:
            user_input: The user's command input
            
        Returns:
            Dictionary with processing results
        """
        parts = user_input.split(' ', 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        result = {
            'command': command,
            'args': args,
            'handled': False
        }
        
        if command == '$pwd':
            # Show current directory
            current_dir = os.getcwd()
            self.display_system_message(f"Current directory: {current_dir}", 'info')
            result['handled'] = True
        elif command == '$cd' and args:
            # Change directory
            try:
                # Expand user path (e.g., ~/directory)
                expanded_path = os.path.expanduser(args)
                
                # If it's a relative path, make it relative to the current directory
                if not os.path.isabs(expanded_path):
                    expanded_path = os.path.join(os.getcwd(), expanded_path)
                
                # Change directory
                os.chdir(expanded_path)
                
                # Show success message
                self.display_system_message(f"Changed directory to: {expanded_path}", 'info')
                result['handled'] = True
                
            except Exception as e:
                error_msg = f"Error changing directory to {args}: {str(e)}"
                self.display_system_message(error_msg, 'error')
                result['handled'] = True
        elif command == '$cd':
            # Change to home directory if no args
            try:
                home_dir = os.path.expanduser("~")
                os.chdir(home_dir)
                self.display_system_message(f"Changed to home directory: {home_dir}", 'info')
                result['handled'] = True
            except Exception as e:
                error_msg = f"Error changing directory to home: {str(e)}"
                self.display_system_message(error_msg, 'error')
                result['handled'] = True
        elif command == '$approve':
            # 批准执行工具
            if self.pending_tools:
                self.display_system_message(f"Approved execution of {len(self.pending_tools)} tool(s)", 'info')
                result['handled'] = True
                result['approved_tools'] = self.pending_tools.copy()
                self.pending_tools.clear()
            else:
                self.display_system_message("No pending tools to approve", 'info')
                result['handled'] = True
                
        return result

    def show_instructions(self):
        """Display instructions for using the chat interface."""
        print("=" * 50)
        print("AI Chat Interface")
        print("=" * 50)
        print("Type your message and press [Enter] to send.")
        print(
            "Press [Alt+Enter] or [Esc] followed by [Enter] for multi-line messages.")
        print()
        print("Special commands:")
        print("  $add [path] - Add content from a file")
        print("  $help       - Show this help message")
        print("  $clear      - Clear the current input")
        print("  $exit       - Exit the chat")
        print("  $reset      - Reset conversation history")
        print("  $pwd        - Show current directory")
        print("  $cd [path]  - Change directory")
        print("  $approve    - Approve and execute pending tools")
        print()
        print("Special key bindings:")
        print("  Ctrl+C - Clear current input or exit if empty")
        print("  Ctrl+D - Exit chat")
        print("=" * 50)
        print()

    def show_goodbye_message(self):
        """Display a goodbye message."""
        print_formatted_text(HTML('<ansiblue>AI:</ansiblue> Goodbye!'))

    def show_interrupt_message(self):
        """Display an interrupt message."""
        print("\n" + HTML('<ansired>Chat interrupted. Goodbye!</ansired>'))

    def wait_for_enter(self):
        """Wait for the user to press Enter."""
        input("\nPress Enter to continue...")