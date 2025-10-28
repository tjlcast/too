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
        # Check if this is the simple format (no args/file wrappers)
        root = ET.fromstring(xml_string)

        # If root tag is 'write_to_file', parse in the simple format
        # 1 for  <write_to_file><args>
        # 2 for  <write_to_file><args><file>
        xml_contain_file = 2

        if xml_contain_file == 1:
            args_element = root.find("args")
            path_element = args_element.find('path')
            content_element = args_element.find('content')
            line_count_element = args_element.find('line_count')

            file_info = {"path": "", "content": "", "line_count": 0}

            if path_element is not None and path_element.text:
                file_info["path"] = path_element.text.strip()

            if content_element is not None:
                # Handle CDATA or plain text content
                file_info["content"] = content_element.text or ""

            if line_count_element is not None and line_count_element.text:
                try:
                    file_info["line_count"] = int(
                        line_count_element.text.strip())
                except ValueError:
                    file_info["line_count"] = 0

            return WriteToFileArgs(file=[file_info])
        else:
            # Handle the args/file format
            write_to_file_element = root if root.tag == 'write_to_file' else root.find(
                'write_to_file')

            if write_to_file_element is None:
                return {"error": "Invalid XML format"}

            # Parse args
            args_element = write_to_file_element.find('args')
            if args_element is None:
                return {"error": "Missing <args> element"}

            # Parse files
            file_elements = args_element.findall('file')
            files = []

            for file_element in file_elements:
                path_element = file_element.find('path')
                content_element = file_element.find('content')
                line_count_element = file_element.find('line_count')

                file_info = {"path": "", "content": "", "line_count": 0}

                if path_element is not None and path_element.text:
                    file_info["path"] = path_element.text.strip()

                if content_element is not None:
                    # Handle CDATA or plain text content
                    file_info["content"] = content_element.text or ""

                if line_count_element is not None and line_count_element.text:
                    try:
                        file_info["line_count"] = int(
                            line_count_element.text.strip())
                    except ValueError:
                        file_info["line_count"] = 0

                files.append(file_info)

            return WriteToFileArgs(file=files)

    except ET.ParseError as e:
        raise ValueError(f"XML parsing error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing XML: {str(e)}")


if __name__ == "__main__":
    xml_string = """
    <write_to_file>
    <args>
    <file>
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
    </file>
    </args>
    </write_to_file>
    """

    print(run(xml_string))
