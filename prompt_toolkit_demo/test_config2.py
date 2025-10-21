#!/usr/bin/env python3

import os
import sys

# Add src to path so we can import the ai_chat module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from examples.ai_chat import load_env_config

def main():
    print("Testing API configuration loading from ai_chat module...")
    config = load_env_config()
    
    print("Configuration loaded:")
    for key, value in config.items():
        # Mask the API key for security
        if key == 'API_KEY':
            print(f"  {key}: {'*' * len(value) if value else 'None'}")
        else:
            print(f"  {key}: {value}")
    
    # Check if API is properly configured
    api_key = config.get('API_KEY', '')
    if not api_key or api_key == 'your-api-key-here':
        print("\n❌ API is NOT properly configured - will use simulated responses")
    else:
        print("\n✅ API is properly configured - will use real API")

if __name__ == "__main__":
    main()