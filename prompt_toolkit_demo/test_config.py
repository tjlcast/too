#!/usr/bin/env python3

import os
import sys

def load_env_config_debug():
    """Debug version of load_env_config to see what's happening."""
    # Use the same path resolution as in ai_chat.py
    env_path = os.path.join(os.path.dirname(__file__), 'src', 'examples', '..', '..', '.env')
    config = {}
    
    print(f"Looking for .env file at: {os.path.abspath(env_path)}")
    print(f".env file exists: {os.path.exists(env_path)}")
    
    if os.path.exists(env_path):
        print("Reading .env file contents:")
        with open(env_path, 'r') as f:
            for i, line in enumerate(f):
                line = line.strip()
                print(f"  Line {i}: {repr(line)}")
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        stripped_value = value.strip('"\'')
                        config[key] = stripped_value
                        print(f"    Parsed: {key} = {repr(stripped_value)}")
                    else:
                        print(f"    Skipping line (no = sign)")
    
    return config

def main():
    print("Testing API configuration loading...")
    config = load_env_config_debug()
    
    print("\nConfiguration loaded:")
    for key, value in config.items():
        # Show actual values for debugging
        print(f"  {key}: {repr(value)}")
    
    print("\nDetailed API key check:")
    api_key = config.get('API_KEY', '')
    print(f"  API_KEY value: {repr(api_key)}")
    print(f"  API_KEY length: {len(api_key)}")
    print(f"  API_KEY is empty: {not bool(api_key)}")
    print(f"  API_KEY equals 'your-api-key-here': {api_key == 'your-api-key-here'}")
    
    # Check if API is properly configured
    if not api_key or api_key == 'your-api-key-here':
        print("\n❌ API is NOT properly configured - will use simulated responses")
    else:
        print("\n✅ API is properly configured - will use real API")

if __name__ == "__main__":
    main()