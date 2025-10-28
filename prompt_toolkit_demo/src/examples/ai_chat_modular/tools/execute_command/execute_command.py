import os
import subprocess
from typing import Dict, Any
import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExecuteCommandArgs:
    """Arguments for the execute command tool."""
    command: str
    cwd: Optional[str] = None


def execute_command(args_obj: ExecuteCommandArgs, basePath: str = None) -> Dict[str, Any]:
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

    return _execute_command(args_obj, basePath)


def _execute_command(args: ExecuteCommandArgs, basePath: str) -> Dict[str, Any]:
    """
    Execute a CLI command on the system.

    Args:
        args: ExecuteCommandArgs containing command to execute and optional working directory
        basePath: Base path to resolve relative working directory paths

    Returns:
        Dictionary with results of command execution including stdout, stderr and return code
    """
    try:
        command = args.command
        cwd = args.cwd

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


# For testing purposes
if __name__ == "__main__":
    from pathlib import Path
    current_working_directory = Path.cwd()

    # Test the function
    test_args = ExecuteCommandArgs(
        command="echo Hello World"
    )
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

    # Convert to ExecuteCommandArgs for testing
    args_obj = ExecuteCommandArgs(
        command=parsed_args["args"]["command"],
        cwd=parsed_args["args"].get("cwd")
    )
    result = _execute_command(args_obj, current_working_directory)
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
