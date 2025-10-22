from typing import Dict, Any
import os

from prompt_toolkit_demo.src.examples.ai_agent.tools.search_and_replace.search_and_replace import search_and_replace


def run(xml_string: str, basePath: str = None) -> str:
    result = search_and_replace(xml_string, basePath)

    # 如果有错误，返回错误信息
    if "error" in result:
        return f"Error: {result['error']}"

    # 获取结果列表
    results = result.get("results", [])

    # 构建返回的字符串格式，按照示例格式
    if results:
        file_result = results[0]  # 只处理第一个文件
        path = file_result.get("path", "")
        operation = file_result.get("operation", "no changes")
        user_edits = file_result.get("user_edits", "no edits applied")

        # 构建输出字符串
        output_lines = [f"[search_and_replace for '{path}'] Result:"]
        output_lines.append("<file_write_result>")
        output_lines.append(f"<path>{path}</path>")
        output_lines.append(f"<operation>{operation}</operation>")

        # 添加user_edits部分
        output_lines.append(f"<user_edits>{user_edits}")

        output_lines.append("</user_edits>")
        output_lines.append("</file_write_result>")

        # 只有在确实有更改时才添加notice部分
        if operation != "no changes":
            # 添加notice部分
            output_lines.append("<notice>")
            output_lines.append(
                "<i>You do not need to re-read the file, as you have seen all changes</i>")
            output_lines.append(
                "<i>Proceed with the task using these changes as the new baseline.</i>")
            output_lines.append("</notice>")

        return "\n".join(output_lines)
    else:
        return "[search_and_replace] Result: No files processed"


if __name__ == "__main__":
    # 创建测试文件
    test_file_path = "test.json"
    with open(test_file_path, "w") as f:
        f.write("This is oldText.\nAnother oldText line.\nFinal line.")

    xml_string = """
    <search_and_replace>
    <path>test.json</path>
    <search>oldText</search>
    <replace>newText</replace>
    </search_and_replace>
    """

    print(run(xml_string))
