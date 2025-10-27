from typing import Dict, Any

from prompt_toolkit_demo.src.examples.ai_agent.tools.execute_command.execute_command import execute_command


def run(xml_string: str, basePath: str = None) -> str:
    result = execute_command(xml_string, basePath)

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
