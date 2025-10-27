from typing import Dict, Any

from prompt_toolkit_demo.src.examples.ai_agent.tools.insert_content.insert_content import insert_content


def run(xml_string: str, basePath: str = None) -> str:
    result = insert_content(xml_string, basePath)

    # 如果有错误，返回错误信息
    if "error" in result:
        return f"Error: {result['error']}"

    # 获取结果列表
    results = result.get("results", [])
    result = results[0]
    path = result.get("path", "")
    operation = result.get("operation", "")
    user_edits = result.get("user_edits", "")

    # 构建返回的字符串格式
    output_lines = [f"[insert_content for '{path}'] Result:"]
    output_lines.append("<file_write_result>")
    output_lines.append(f"<path>{path}</path>")
    output_lines.append(f"<operation>{operation}</operation>")

    output_lines.append(f"<user_edits>{user_edits}")
    output_lines.append("</file_write_result>")

    # 添加notice部分
    output_lines.append("<notice>")
    output_lines.append(
        "<i>You do not need to re-read the file, as you have seen all changes</i>")
    output_lines.append(
        "<i>Proceed with the task using these changes as the new baseline.</i>")
    output_lines.append(
        "<i>If the user's edits have addressed part of the task or changed the requirements, adjust your approach accordingly.</i>")
    output_lines.append("</notice>")
    output_lines.append("</file_write_result>")

    return "\n".join(output_lines)


# For testing purposes
if __name__ == "__main__":
    from pathlib import Path
    current_working_directory = Path.cwd()

    xml_example = """
    <insert_content>
    <args>
      <insertion>
        <path>test.json</path>
        <line>1</line>
        <content>This is a test line</content>
      </insertion>
    </args>
    </insert_content>
    """
    print(run(xml_example, current_working_directory))
