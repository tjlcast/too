import os
import xml.etree.ElementTree as ET
import subprocess
from typing import Dict, Any
import json


"""
@function
"""
def execute_command(xml_string: str, basePath: str = None) -> Dict[str, Any]:
    """
    Execute a CLI command on the system.

    Args:
        xml_string: XML string representing a execute_command tool call
        basePath: Base path to resolve relative working directory paths

    Returns:
        Dictionary with results of command execution
    """
    if basePath is None:
        basePath = os.getcwd()
    args = parse_execute_command_xml(xml_string)
    return _execute_command(args, basePath)


def _execute_command(args: Dict[str, Any], basePath: str) -> Dict[str, Any]:
    """
    Execute a CLI command on the system.

    Args:
        args: Dictionary containing command to execute and optional working directory
        basePath: Base path to resolve relative working directory paths

    Returns:
        Dictionary with results of command execution including stdout, stderr and return code
    """
    try:
        # Extract command and cwd from args
        command_args = args.get('args', {})
        command = command_args.get('command')
        cwd = command_args.get('cwd')
        
        if not command:
            return {"error": "No command specified"}

        # Resolve working directory
        if cwd:
            full_cwd = os.path.join(basePath, cwd)
            # Check if directory exists
            if not os.path.exists(full_cwd):
                return {"error": f"Working directory does not exist: {full_cwd}"}
            if not os.path.isdir(full_cwd):
                return {"error": f"Working directory path is not a directory: {full_cwd}"}
        else:
            full_cwd = basePath

        # Execute the command
        try:
            # Using shell=True to support command chaining and complex commands
            result = subprocess.run(
                command,
                shell=True,
                cwd=full_cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            return {
                "command": command,
                "cwd": full_cwd,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "status": "success" if result.returncode == 0 else "error"
            }
        except Exception as e:
            return {
                "command": command,
                "cwd": full_cwd,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "status": "error"
            }

    except Exception as e:
        return {"error": f"Failed to process execute_command request: {str(e)}"}


def parse_execute_command_xml(xml_string: str) -> Dict[str, Any]:
    """
    Parse XML string into the args structure for execute_command tool.

    Args:
        xml_string: XML string representing a execute_command tool call

    Returns:
        Dictionary with the parsed args structure
    """
    try:
        # Wrap the XML in a root element if it doesn't have one
        if not xml_string.strip().startswith('<execute_command>'):
            xml_string = f"<root>{xml_string}</root>"
            root = ET.fromstring(xml_string)
            execute_command_element = root.find('execute_command')
        else:
            execute_command_element = ET.fromstring(xml_string)

        if execute_command_element is None:
            return {"error": "Invalid XML format"}

        # Parse args
        args_element = execute_command_element.find('args')
        if args_element is None:
            return {"error": "Missing <args> element"}

        # Parse command
        command_element = args_element.find('command')
        command = command_element.text.strip() if command_element is not None and command_element.text else None

        # Parse cwd (optional)
        cwd_element = args_element.find('cwd')
        cwd = cwd_element.text.strip() if cwd_element is not None and cwd_element.text else None

        return {
            "args": {
                "command": command,
                "cwd": cwd
            }
        }

    except ET.ParseError as e:
        return {"error": f"XML parsing error: {str(e)}"}
    except Exception as e:
        return {"error": f"Error parsing XML: {str(e)}"}


# For testing purposes
if __name__ == "__main__":
    from pathlib import Path
    current_working_directory = Path.cwd()

    # Test the function
    test_args = {
        "args": {
            "command": "echo Hello World",
        }
    }
    result = _execute_command(test_args, current_working_directory)
    print(json.dumps(result, indent=2))

    # Test XML parsing
    xml_example = """
    <execute_command>
    <args>
      <command>echo Hello World</command>
    </args>
    </execute_command>
    """

    parsed_args = parse_execute_command_xml(xml_example)
    print("\nParsed XML:")
    print(json.dumps(parsed_args, indent=2))
    result = _execute_command(parsed_args, current_working_directory)
    print(json.dumps(result, indent=2))
    
    
    xml_example = """
    <execute_command>
    <args>
      <command>echo Hello World</command>
      <cwd>.</cwd>
    </args>
    </execute_command>
    """
    print(execute_command(xml_example))