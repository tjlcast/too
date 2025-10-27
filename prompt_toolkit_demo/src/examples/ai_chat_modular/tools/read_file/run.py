from typing import Dict, Any

from .read_file import FileInfo, read_file
from .read_file import ReadFileArgs

import xml.etree.ElementTree as ET


def run(xml_string: str, basePath: str = None) -> str:
    args = parse_xml_args(xml_string)
    return execute(args, basePath)


def execute(args: ReadFileArgs, basePath: str = None) -> Dict[str, Any]:
    result = read_file(args, basePath)

    # 如果有错误，返回错误信息
    if "error" in result:
        return f"Error: {result['error']}"

    # 获取结果列表
    results = result.get("results", [])

    # 构建返回的字符串格式
    output_lines = [f"[read_file for {len(results)} files] Result:"]
    output_lines.append(
        "The user approved this operation and provided the following context:")
    output_lines.append("<feedback>")
    output_lines.append("VS Code/Untitled-2:1-5")
    output_lines.append("</feedback>")
    output_lines.append("<files>")

    # 添加每个文件的内容
    for file_result in results:
        if file_result.get("status") == "success":
            path = file_result.get("path", "")
            content = file_result.get("content", "")

            # 计算行数
            lines = content.split('\n') if content else []
            line_count = len(lines)
            line_range = f"1-{line_count}" if line_count > 0 else "1-0"

            output_lines.append(f"<file><path>{path}</path>")
            output_lines.append(f"<content lines=\"{line_range}\">")
            output_lines.append(content)
            output_lines.append("</content>")
            output_lines.append("</file>")
        else:
            # 处理错误情况
            path = file_result.get("path", "")
            error = file_result.get("error", "Unknown error")
            output_lines.append(f"<file><path>{path}</path>")
            output_lines.append(f"<error>{error}</error>")
            output_lines.append("</file>")

    output_lines.append("</files>")

    return "\n".join(output_lines)


def parse_xml_args(xml_string: str) -> ReadFileArgs:
    """
    Parse XML string into the args structure for read_file tool.

    Args:
        xml_string: XML string representing a read_file tool call

    Returns:
        ReadFileArgs with the parsed arguments
    """
    try:
        # Wrap the XML in a root element if it doesn't have one
        if not xml_string.strip().startswith('<read_file>'):
            xml_string = f"<root>{xml_string}</root>"
            root = ET.fromstring(xml_string)
            read_file_element = root.find('read_file')
        else:
            read_file_element = ET.fromstring(xml_string)

        if read_file_element is None:
            # Return empty args instead of dict with error
            return ReadFileArgs(file=[])

        # Parse args
        args_element = read_file_element.find('args')
        if args_element is None:
            # Return empty args instead of dict with error
            return ReadFileArgs(file=[])

        # Parse files
        file_elements = args_element.findall('file')
        files = []

        for file_element in file_elements:
            path_element = file_element.find('path')
            if path_element is not None and path_element.text:
                files.append(FileInfo(path=path_element.text.strip()))

        return ReadFileArgs(file=files)

    except ET.ParseError as e:
        # Return empty args instead of dict with error
        return ReadFileArgs(file=[])
    except Exception as e:
        # Return empty args instead of dict with error
        return ReadFileArgs(file=[])


# For testing purposes
if __name__ == "__main__":
    from pathlib import Path
    current_working_directory = Path.cwd()

    xml_example = """
    <read_file>
    <args>
      <file>
        <path>prompt_toolkit_demo/src/examples/ai_agent/tools/read_file/read_file.py</path>
      </file>
      <file>
        <path>prompt_toolkit_demo/src/main.py</path>
      </file>
    </args>
    </read_file>
    """
    print(run(xml_example, current_working_directory))
