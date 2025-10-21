#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from examples.ai_chat import simulate_ai_response_streaming, display_streaming_response

def main():
    print("Testing AI display rendering:")
    print("=" * 40)
    
    # Test with a sample message
    test_message = "你好"
    print(f"Input: {test_message}")
    print("Output:")
    
    # Get response generator
    response_generator = simulate_ai_response_streaming(test_message)
    
    # Display response using our function
    display_streaming_response(response_generator)

if __name__ == "__main__":
    main()