"""
LLM Provider for AI Chat Application
====================================

This module handles interactions with AI language models,
including both real API calls and simulated responses.
"""

import random
import time
import os
import json
from typing import List, Dict, Generator
import urllib.request


class LLMProvider:
    """
    Provider for interacting with AI language models.
    Supports both real API calls and simulated responses.
    """

    def __init__(self):
        """Initialize the LLM provider and load configuration."""
        self.config = self._load_env_config()

    def _load_env_config(self) -> Dict[str, str]:
        """Load configuration from .env file."""
        # Fixed path resolution to correctly find .env file
        env_path = os.path.join(os.path.dirname(
            __file__), '..', '..', '..', '..', '.env')
        config = {}

        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        config[key] = value.strip('"\'')

        return config

    def get_response_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        Get a streaming response from the AI model.

        Args:
            messages: List of message dictionaries with role and content

        Yields:
            Chunks of the AI response
        """
        api_base_url = self.config.get(
            'API_BASE_URL', 'https://api.openai.com/v1')
        api_key = self.config.get('API_KEY', '')
        model = self.config.get('API_MODEL', 'gpt-3.5-turbo')
        print(f"api_key: {api_key}")

        # If no API key is configured, use simulated response
        if not api_key or api_key == 'your-api-key-here':
            yield from self._simulate_ai_response_streaming(messages[-1]['content'])
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
            yield f"[Error calling API: {str(e)}]\\n"

    def _simulate_ai_response_streaming(self, user_input: str) -> Generator[str, None, None]:
        """
        Simulate a streaming AI response based on user input.
        In a real application, this would be replaced by actual API streaming.

        Args:
            user_input: The user's input message

        Yields:
            Chunks of a simulated AI response
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

        # mark this is simulated response
        response = f"[Simulated Response] {response}"

        # Simulate streaming by yielding parts of the response
        words = response.split(' ')
        for i, word in enumerate(words):
            # Simulate varying delays between words
            if i > 0:
                time.sleep(random.uniform(0.05, 0.2))
            yield word + (' ' if i < len(words) - 1 else '')

    def get_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Get a complete response from the AI model.

        Args:
            messages: List of message dictionaries with role and content

        Returns:
            Complete AI response as a string
        """
        response = ""
        for chunk in self.get_response_stream(messages):
            response += chunk
        return response
