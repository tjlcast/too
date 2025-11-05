from typing import Dict, Any
import os

import xml.etree.ElementTree as ET
from .write_to_file import WriteToFileArgs, write_to_file


def run(xml_string: str, basePath: str = None) -> str:
    args = parse_write_file_xml(xml_string)
    return execute(args, basePath)


def execute(args: WriteToFileArgs, basePath: str = None) -> str:
    result = write_to_file(args, basePath)

    # 如果有错误，返回错误信息
    if "error" in result:
        return f"Error: {result['error']}"

    # 获取结果列表
    results = result.get("results", [])

    # 构建返回的字符串格式，按照示例格式
    if results:
        file_result = results[0]  # 只处理第一个文件
        path = file_result.get("path", "")
        operation = file_result.get("operation", "modified")
        user_edits = file_result.get("user_edits", "no edits applied")
        line_count = file_result.get("line_count", 0)

        # 构建输出字符串
        output_lines = [f"[write_to_file for '{path}'] Result:"]
        output_lines.append("<file_write_result>")
        output_lines.append(f"<path>{path}</path>")
        output_lines.append(f"<operation>{operation}</operation>")

        # 添加user_edits部分，根据实际内容构建
        # 首先解析XML以获取内容
        output_lines.append(f"<user_edits>{user_edits.strip()}")

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


def parse_write_file_xml(xml_string: str) -> WriteToFileArgs:
    """
    Parse XML string into the args structure for write_to_file tool.

    Args:
        xml_string: XML string representing a write_to_file tool call

    Returns:
        WriteToFileArgs with the parsed args structure
    """
    try:
        # 用特殊方法处理包含XML标签的文本内容
        # 首先将content标签内容临时替换为占位符
        import re

        # 提取所有content内容，使用非贪婪模式
        content_matches = re.findall(
            r'<content>(.*?)</content>', xml_string, re.DOTALL)
        content_texts = []
        for match in content_matches:
            content_texts.append(match)

        # 将原始XML中的content内容替换为占位符，使用非贪婪模式
        placeholder_xml = re.sub(
            r'<content>.*?</content>', '<content>__CONTENT_PLACEHOLDER__</content>', xml_string, flags=re.DOTALL)

        # 解析替换后的XML
        root = ET.fromstring(placeholder_xml)

        content_index = 0
        path_element = root.find('path')
        content_element = root.find('content')
        line_count_element = root.find('line_count')

        file_info = {"path": "", "content": "", "line_count": 0}

        if path_element is not None and path_element.text:
            file_info["path"] = path_element.text.strip()

        if content_element is not None and content_element.text:
            # 使用之前提取的完整content内容
            if content_index < len(content_texts):
                file_info["content"] = content_texts[content_index]
                content_index += 1

        if line_count_element is not None and line_count_element.text:
            try:
                file_info["line_count"] = int(
                    line_count_element.text.strip())
            except ValueError:
                file_info["line_count"] = 0

        return WriteToFileArgs(file=[file_info])

    except ET.ParseError as e:
        raise ValueError(f"XML parsing error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing XML: {str(e)}")


if __name__ == "__main__":
    xml_string = """
<write_to_file>
<path>test.json</path>
<content>
<apple></apple><adsfasf>
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
<line_count>17</line_count>
</write_to_file>
    """

    print(run(xml_string))
