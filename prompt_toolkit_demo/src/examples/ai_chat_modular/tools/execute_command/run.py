from typing import Dict, Any

import xml.etree.ElementTree as ET
from .execute_command import ExecuteCommandArgs, execute_command


def run(xml_string: str, basePath: str = None) -> str:
    parsed_args = parse_execute_command_xml(xml_string)
    # Check for parsing errors
    if "error" in parsed_args:
        return parsed_args

    # Convert parsed args dict to ExecuteCommandArgs object
    args_obj = ExecuteCommandArgs(
        command=parsed_args["args"]["command"],
        cwd=parsed_args["args"].get("cwd")
    )
    return execute(args_obj, basePath)


def execute(args: ExecuteCommandArgs, basePath: str):

    result = execute_command(args, basePath)

    # 如果有错误，返回错误信息
    if "error" in result:
        return f"Error: {result['error']}"

    # 获取执行结果
    command = result.get("command", "")
    cwd = result.get("cwd", "")
    stdout = result.get("stdout", "")
    stderr = result.get("stderr", "")
    returncode = result.get("returncode", 0)
    status = result.get("status", "unknown")

    # 构建返回的字符串格式
    output_lines = [f"[execute_command for '{command}'] Result:"]
    output_lines.append(
        f"Command executed in terminal  within working directory '{cwd}'.")
    output_lines.append(f"Exit code: {returncode}")
    output_lines.append(f"Status: {status}")

    if stdout:
        output_lines.append("Output:")
        output_lines.append(stdout.strip())  # Remove trailing newlines

    if stderr:
        output_lines.append("Error:")
        output_lines.append(stderr.strip())  # Remove trailing newlines

    return "\n".join(output_lines)


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
        command = command_element.text.strip(
        ) if command_element is not None and command_element.text else None

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

    xml_example = """
    <execute_command>
    <args>
      <command>echo Hello</command>
    </args>
    </execute_command>
    """
    print(run(xml_example, current_working_directory))

    xml_example = """
    <execute_command>
    <args>
      <command>ls .</command>
    </args>
    </execute_command>
    """
    print(run(xml_example, current_working_directory))

    xml_example = """
    <execute_command>
    <args>
      <command>dir .</command>
    </args>
    </execute_command>
    """
    print(run(xml_example, current_working_directory))
    
    
    xml_example = """
    <execute_command>
    <args>
      <command>pwd</command>
    </args>
    </execute_command>
    """
    print(run(xml_example, current_working_directory))
