from typing import Dict, Any
import os

from prompt_toolkit_demo.src.examples.ai_agent.tools.write_to_file.write_to_file import write_to_file


def run(xml_string: str, basePath: str = None) -> str:
    result = write_to_file(xml_string, basePath)

    # 如果有错误，返回错误信息
    if "error" in result:
        return f"Error: {result['error']}"

    # 获取结果列表
    results = result.get("results", [])

    # 构建返回的字符串格式，按照示例格式
    if results:
        file_result = results[0]  # 只处理第一个文件
        path = file_result.get("path", "")
        operation = "created"  # 默认操作为创建
        line_count = file_result.get("line_count", 0)

        # 构建输出字符串
        output_lines = [f"[write_to_file for '{path}'] Result:"]
        output_lines.append("<file_write_result>")
        output_lines.append(f"<path>{path}</path>")
        output_lines.append(f"<operation>{operation}</operation>")

        # 添加user_edits部分，根据实际内容构建
        # 首先解析XML以获取内容
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_string)
        if root.tag == 'write_to_file':
            content_element = root.find('content')
            content = content_element.text if content_element is not None else ""
            lines = content.split('\n') if content else []
            # 移除最后的空行（如果有的话）
            if lines and lines[-1] == "":
                lines = lines[:-1]

            # 构建user_edits部分
            output_lines.append(f"<user_edits>@@ -1,{len(lines)} +0,0 @@")
            for line in lines:
                # 转义引号
                escaped_line = line.replace('"', '\\"')
                output_lines.append(f'-{escaped_line}')
            output_lines.append("\\ No newline at end of file")
        else:
            # 处理args/file格式
            args_element = root.find('args')
            if args_element is not None:
                file_elements = args_element.findall('file')
                if file_elements:
                    content_element = file_elements[0].find('content')
                    content = content_element.text if content_element is not None else ""
                    lines = content.split('\n') if content else []
                    # 移除最后的空行（如果有的话）
                    if lines and lines[-1] == "":
                        lines = lines[:-1]

                    # 构建user_edits部分
                    output_lines.append(
                        f"<user_edits>@@ -1,{len(lines)} +0,0 @@")
                    for line in lines:
                        # 转义引号
                        escaped_line = line.replace('"', '\\"')
                        output_lines.append(f'-{escaped_line}')
                    output_lines.append("\\ No newline at end of file")

        output_lines.append("</user_edits>")
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

        return "\n".join(output_lines)
    else:
        return "[write_to_file] Result: No files processed"


if __name__ == "__main__":
    xml_string = """
    <write_to_file>
    <path>test.json</path>
    <content>
{
  "apiEndpoint": "https://api.example.com",
  "theme": {
    "primaryColor": "#007bff",
    "secondaryColor": "#6c757d",
    "fontFamily": "Arial, sans-serif"
  },
  "features": {
    "darkMode": true,
    "notifications": true,
    "analytics": false
  },
  "version": "1.0.0"
}
</content>
<line_count>14</line_count>
</write_to_file>
    """

    print(run(xml_string))
