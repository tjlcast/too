"""
AI Chat Simulation Example
==========================

This example simulates an AI chat interface using prompt_toolkit.
It demonstrates how to create a chatbot-like experience with:
- Continuous conversation loop
- Multi-line input support
- Custom key bindings
- Real AI responses using chat/completion API with streaming
"""

import random
import time
import os
import sys
from typing import List, Dict
import json
from datetime import datetime
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory
import urllib.request
from prompt_toolkit import print_formatted_text


def load_env_config():
    """Load configuration from .env file."""
    # Fixed path resolution to correctly find .env file
    env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    config = {}

    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key] = value.strip('"\'')

    return config


def call_ai_api(messages: List[Dict[str, str]], config: dict):
    """
    Call the AI API with streaming response.
    Yields chunks of the response as they arrive.
    """
    api_base_url = config.get('API_BASE_URL', 'https://api.openai.com/v1')
    api_key = config.get('API_KEY', '')
    model = config.get('API_MODEL', 'gpt-3.5-turbo')

    if not api_key or api_key == 'your-api-key-here':
        # Fallback to simulated response if no API key configured
        raise Exception(
            "No API key configured. Please set API_KEY in .env file.")
        yield from simulate_ai_response_streaming(messages[-1]['content'])
        return

    url = f"{api_base_url}/chat/completions"

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    data = {
        'model': model,
        'messages': messages,
        'stream': True
    }

    json_data = json.dumps(data).encode('utf-8')

    req = urllib.request.Request(
        url, data=json_data, headers=headers, method='POST')

    try:
        response = urllib.request.urlopen(req)
        for line in response:
            line = line.decode('utf-8').strip()
            if line.startswith('data: ') and line != 'data: [DONE]':
                data_str = line[6:]  # Remove 'data: ' prefix
                try:
                    chunk_data = json.loads(data_str)
                    if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                        delta = chunk_data['choices'][0].get('delta', {})
                        if 'content' in delta:
                            yield delta['content']
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        yield f"[Error calling API: {str(e)}]\n"


def simulate_ai_response_streaming(user_input: str):
    """
    Simulate a streaming AI response based on user input.
    In a real application, this would be replaced by actual API streaming.
    """
    # Simple response simulation based on keywords
    user_input = user_input.lower()

    if 'hello' in user_input or 'hi' in user_input:
        responses = [
            "Hello there! How can I assist you today?",
            "Hi! What can I help you with?",
            "Greetings! How may I be of service?"
        ]
    elif 'how are you' in user_input:
        responses = [
            "I'm just a program, but I'm functioning perfectly! How can I help you?",
            "I'm doing well, thank you for asking! What would you like to discuss?",
        ]
    elif 'bye' in user_input or 'goodbye' in user_input:
        responses = [
            "Goodbye! Feel free to come back if you have more questions.",
            "See you later! Have a great day!",
            "Farewell! It was nice chatting with you."
        ]
    elif 'help' in user_input:
        responses = [
            "I can help you with various topics. Try asking me questions about technology, science, or general knowledge!",
            "I'm here to assist with any questions you might have. What would you like to know?",
        ]
    elif 'name' in user_input:
        responses = [
            "I'm an AI assistant created with prompt_toolkit. You can call me whatever you like!",
            "I'm your friendly AI assistant. What would you prefer to call me?",
        ]
    elif '?' in user_input:
        responses = [
            "That's an interesting question. Based on my knowledge, I'd say that's a complex topic worth exploring further.",
            "I understand your curiosity. While I don't have all the answers, I can tell you that it depends on several factors.",
            "Great question! From what I know, there are multiple perspectives on that topic.",
        ]
    else:
        responses = [
            "I understand. Could you tell me more about that?",
            "That's fascinating! Is there anything specific you'd like to know?",
            "Thanks for sharing. How does that make you feel?",
            "I see. What else would you like to discuss?",
            "Interesting perspective. Can you elaborate on that?",
        ]

    response = random.choice(responses)

    # Simulate streaming by yielding parts of the response
    words = response.split(' ')
    for i, word in enumerate(words):
        # Simulate varying delays between words
        if i > 0:
            time.sleep(random.uniform(0.05, 0.2))
        yield word + (' ' if i < len(words) - 1 else '')


def display_streaming_response(generator):
    """
    Display streaming response in real-time.
    Returns the full response.
    """
    from prompt_toolkit import print_formatted_text

    full_response = ""
    print_formatted_text(HTML('<ansiblue>AI:</ansiblue> '), end='', flush=True)

    for chunk in generator:
        print(chunk, end='', flush=True)
        full_response += chunk

    print()  # New line after response
    return full_response


def run():
    """Run the AI chat simulation example."""
    print("=== AI Chat Simulation Example ===\\n")

    # Load API configuration
    config = load_env_config()

    # Define custom style
    style = Style.from_dict({
        'prompt': '#00ff00 bold',     # Green prompt
        'ai': '#0088ff',              # Blue AI responses
        'info': '#ffff00',            # Yellow info text
        'error': '#ff0000 bold',      # Red error text
    })

    # Custom key bindings
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

    @bindings.add('c-r')
    def _(event):
        """Reset the conversation."""
        nonlocal messages
        messages = []
        print("\\n" + "="*50)
        print("Conversation history cleared.")
        print("="*50)

    # Print instructions
    print_formatted_text(HTML('<ansiyellow>AI Chat Interface</ansiyellow>'))
    print("=" * 50)
    print("Type your message and press [Enter] to send.")
    print(
        "Press [Alt+Enter] or [Esc] followed by [Enter] for multi-line messages.")
    print()
    print("Special key bindings:")
    print("  Ctrl+C - Clear current input or exit if empty")
    print("  Ctrl+D - Exit chat")
    print("  Ctrl+R - Reset conversation history")
    print("=" * 50)
    print()

    # Initialize conversation history (using messages list for both internal state and saving)
    messages = []

    # Main conversation loop
    try:
        while True:
            try:
                # 在用户输入前显示一些上下文信息
                if messages:
                    # 显示对话历史统计
                    user_messages = [
                        m for m in messages if m["role"] == "user"]
                    ai_messages = [
                        m for m in messages if m["role"] == "assistant"]
                    print_formatted_text(HTML(
                        f'<ansiwhite>Context: Conversation history - {len(user_messages)} user messages, {len(ai_messages)} AI responses</ansiwhite>'))
                else:
                    print_formatted_text(
                        HTML('<ansiwhite>Context: Starting new conversation</ansiwhite>'))

                # 也可以显示当前时间或其他信息
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print_formatted_text(
                    HTML(f'<ansicyan>Current time: {current_time}</ansicyan>'))

                user_message = prompt(
                    HTML('<ansigreen>You:</ansigreen> '),
                    multiline=True,
                    key_bindings=bindings,
                    style=style
                ).strip()

                # Check for exit conditions
                if user_message.lower() in ['quit', 'exit', 'bye']:
                    print_formatted_text(
                        HTML('<ansiblue>AI:</ansiblue> Goodbye!'))
                    break

                if not user_message:
                    continue

                # Store user message in history with timestamp
                messages.append({"role": "user", "content": user_message,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

                # Get AI response
                response_generator = call_ai_api(messages, config)
                ai_response = display_streaming_response(response_generator)

                # Store AI response in history with timestamp
                messages.append({"role": "assistant", "content": ai_response,
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

                # Immediately save the latest exchange to file
                try:
                    with open('.ai_chat_history', 'a', encoding='utf-8') as f:
                        user_entry = messages[-2]  # Last user message
                        ai_entry = messages[-1]     # Last AI response

                        f.write(
                            f"[User] [{user_entry['timestamp']}]: {user_entry['content']}\n")
                        f.write(
                            f"[AI] [{ai_entry['timestamp']}]: {ai_entry['content']}\n")
                        f.write("\n")  # Empty line between exchanges
                except Exception as e:
                    print(f"Failed to save conversation exchange: {e}")

                print()  # Empty line for readability

            except KeyboardInterrupt:
                print_formatted_text(
                    "\\n" + HTML('<ansired>Chat interrupted. Goodbye!</ansired>'))
                break
            except EOFError:
                print_formatted_text(
                    "\\n" + HTML('<ansired>Chat ended. Goodbye!</ansired>'))
                break
    finally:
        # Conversation is saved incrementally, no need to save at exit
        pass

    input("\nPress Enter to continue...")
