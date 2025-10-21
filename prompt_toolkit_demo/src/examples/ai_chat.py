"""
AI Chat Simulation Example
==========================

This example simulates an AI chat interface using prompt_toolkit.
It demonstrates how to create a chatbot-like experience with:
- Continuous conversation loop
- Multi-line input support
- Custom key bindings
- Simulated AI responses
"""

import random
import time
from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.history import FileHistory


def simulate_ai_response(user_input):
    """
    Simulate an AI response based on user input.
    In a real application, this would call an actual AI model API.
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
    
    # Simulate thinking delay
    time.sleep(random.uniform(0.5, 2.0))
    
    return random.choice(responses)


def run():
    """Run the AI chat simulation example."""
    print("=== AI Chat Simulation Example ===\\n")
    
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
        nonlocal conversation_history
        conversation_history = []
        print("\\n" + "="*50)
        print("Conversation history cleared.")
        print("="*50)
    
    # Print instructions
    print(HTML('<ansiyellow>AI Chat Interface</ansiyellow>'))
    print("=" * 50)
    print("Type your message and press [Enter] to send.")
    print("Press [Alt+Enter] or [Esc] followed by [Enter] for multi-line messages.")
    print()
    print("Special key bindings:")
    print("  Ctrl+C - Clear current input or exit if empty")
    print("  Ctrl+D - Exit chat")
    print("  Ctrl+R - Reset conversation history")
    print("=" * 50)
    print()
    
    # Initialize conversation history
    conversation_history = []
    
    # Main conversation loop
    while True:
        try:
            user_message = prompt(
                HTML('<ansigreen>You:</ansigreen> '),
                multiline=True,
                key_bindings=bindings,
                history=FileHistory('.ai_chat_history'),
                style=style
            ).strip()
            
            # Check for exit conditions
            if user_message.lower() in ['quit', 'exit', 'bye']:
                print(HTML('<ansiblue>AI:</ansiblue> Goodbye!'))
                break
            
            if not user_message:
                continue
                
            # Store user message in history
            conversation_history.append(f"You: {user_message}")
            
            # Get AI response
            ai_response = simulate_ai_response(user_message)
            
            # Display AI response
            print(HTML(f'<ansiblue>AI:</ansiblue> {ai_response}'))
            
            # Store AI response in history
            conversation_history.append(f"AI: {ai_response}")
            print()  # Empty line for readability
            
        except KeyboardInterrupt:
            print("\\n" + HTML('<ansired>Chat interrupted. Goodbye!</ansired>'))
            break
        except EOFError:
            print("\\n" + HTML('<ansired>Chat ended. Goodbye!</ansired>'))
            break
    
    input("\\nPress Enter to continue...")