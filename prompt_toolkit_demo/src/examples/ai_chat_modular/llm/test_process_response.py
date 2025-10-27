import sys
import os
from typing import Generator, List, Dict

# Add the parent directory to the path so we can import the LLMProxy class

from .llm_proxy import LLMProxy


class MockViewInterface:
    """Mock view interface for testing"""
    def display_ai_header(self):
        print("AI: ", end="", flush=True)
        
    def display_ai_message_chunk(self, chunk: str):
        print(chunk, end="", flush=True)
        
    def display_newline(self):
        print()
        
    def display_system_message(self, message: str, msg_type: str = 'info'):
        print(f"[{msg_type.upper()}] {message}")


class MockLLMProvider:
    """Mock LLM provider for testing"""
    pass


def create_mock_response_stream(text: str) -> Generator[str, None, None]:
    """
    Create a mock response stream by splitting text into chunks
    
    Args:
        text: The text to split into chunks
        
    Yields:
        Chunks of text
    """
    # Split text into chunks of random size between 1 and 10 characters
    i = 0
    while i < len(text):
        chunk_size = min(10, len(text) - i)
        yield text[i:i+chunk_size]
        i += chunk_size


def test_process_response():
    """Test the process_response method with various XML tool calls"""
    
    # Create mock objects
    view_interface = MockViewInterface()
    llm_provider = MockLLMProvider()
    
    # Create LLMProxy instance
    llm_proxy = LLMProxy(view_interface, llm_provider)
    
    # Test case 1: Simple response without tool calls
    print("=" * 50)
    print("Test 1: Simple response without tool calls")
    print("=" * 50)
    
    simple_text = "Hello! How can I help you today?"
    response_stream = create_mock_response_stream(simple_text)
    conversation_history: List[Dict[str, str]] = []
    
    result = llm_proxy.process_response(response_stream, conversation_history)
    print(f"\nFull response: {result['response']}")
    print(f"Conversation history length: {len(conversation_history)}")
    assert 'tools_situations' in result
    assert len(result['tools_situations']) == 0
    
    # Test case 2: Response with execute_command tool call
    print("\n" + "=" * 50)
    print("Test 2: Response with execute_command tool call")
    print("=" * 50)
    
    command_text = """I'll run the ls command for you.
<execute_command>
<args>
  <command>ls -la</command>
</args>
</execute_command>
That's the result of the ls command."""
    
    response_stream = create_mock_response_stream(command_text)
    conversation_history = []
    
    result = llm_proxy.process_response(response_stream, conversation_history)
    print(f"\nFull response: {result['response']}")
    print(f"Conversation history length: {len(conversation_history)}")
    assert 'tools_situations' in result
    assert len(result['tools_situations']) == 1
    
    # Test case 3: Response with write_to_file tool call
    print("\n" + "=" * 50)
    print("Test 3: Response with write_to_file tool call")
    print("=" * 50)
    
    write_text = """I'll create a file for you.
<write_to_file>
<args>
  <file>
    <path>test.txt</path>
    <content>Hello, World!</content>
  </file>
</args>
</write_to_file>
The file has been created."""
    
    response_stream = create_mock_response_stream(write_text)
    conversation_history = []
    
    result = llm_proxy.process_response(response_stream, conversation_history)
    print(f"\nFull response: {result['response']}")
    print(f"Conversation history length: {len(conversation_history)}")
    assert 'tools_situations' in result
    assert len(result['tools_situations']) == 1
    
    # Test case 4: Response with multiple tool calls
    print("\n" + "=" * 50)
    print("Test 4: Response with multiple tool calls")
    print("=" * 50)
    
    multiple_text = """I'll run a few commands for you.
                  <execute_command>
                  <args>
                    <command>pwd</command>
                  </args>
                  </execute_command>
                  Now I'll list the files:
                  <list_files>
                  <args>
                    <path>.</path>
                  </args>
                  </list_files>
                  Finally, I'll create a file:
                  <write_to_file>
                  <args>
                    <file>
                      <path>demo.txt</path>
                      <content>This is a demo file.</content>
                    </file>
                  </args>
                  </write_to_file>
                  All done!"""
    
    response_stream = create_mock_response_stream(multiple_text)
    conversation_history = []
    
    result = llm_proxy.process_response(response_stream, conversation_history)
    print(f"\nFull response: {result['response']}")
    print(f"Conversation history length: {len(conversation_history)}")
    assert 'tools_situations' in result
    assert len(result['tools_situations']) == 3


"""
Run command: python -m src.examples.ai_chat_modular.llm.test_process_response
"""
if __name__ == "__main__":
    test_process_response()