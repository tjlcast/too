import os
import subprocess
from typing import Dict, Any
import json
from dataclasses import dataclass
from typing import Optional
import platform


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
            # 在Windows系统上使用PowerShell执行命令，以支持Unix风格的命令如pwd
            if platform.system() == "Windows":
                # 使用PowerShell执行命令
                result = subprocess.run(
                    ["powershell", "-Command", command],
                    cwd=str(full_cwd),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
            else:
                # 非Windows系统保持原有逻辑
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=str(full_cwd),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

            return {
                "command": command,
                "cwd": str(full_cwd),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "status": "success" if result.returncode == 0 else "error"
            }
        except Exception as e:
            return {
                "command": command,
                "cwd": str(full_cwd),
                "stdout": "",
                "stderr": str(e),
                "returncode": -1,
                "status": "error"
            }

    except Exception as e:
        return {"error": f"Failed to process execute_command request: {str(e)}"}


"""
Run command: python -m .src.examples.ai_chat_modular.tools.execute_command.run
"""
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
    <command>echo Hello World</command>
    </execute_command>
    """

    from .run import parse_execute_command_xml
    parsed_args = parse_execute_command_xml(xml_example)
    result = _execute_command(parsed_args, current_working_directory)
    print(json.dumps(result, indent=2))

    xml_example = """
    <execute_command>
    <command>echo Hello World</command>
    <cwd>.</cwd>
    </execute_command>
    """
    parsed_args = parse_execute_command_xml(xml_example)
    print(execute_command(parsed_args))
