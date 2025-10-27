import json
from typing import Dict, Any

from .list_files import ListFilesArgs, list_files
import xml.etree.ElementTree as ET


def run(xml_string: str, basePath: str = None) -> str:
    args = parse_list_files_xml(xml_string)
    return execute(args, basePath)


def execute(args: ListFilesArgs, basePath: str = None) -> str:
    result = list_files(args, basePath)

    # 如果有错误，返回错误信息
    if "error" in result:
        return f"Error: {result['error']}"

    # 获取路径信息
    path = result.get("path", "")

    # 构建返回的字符串格式
    output_lines = [f"[list_files for '{path}'] Result:"]

    # 添加文件名列表
    items = result.get("items", [])
    for item in items:
        # if item.get("type") == "file":
        #     output_lines.append(item.get("name", ""))
        output_lines.append(item.get("path", ""))

    return "\n".join(output_lines)


def parse_list_files_xml(xml_string: str) -> ListFilesArgs:
    """
    Parse XML string into the args structure for list_files tool.

    Args:
        xml_string: XML string representing a list_files tool call

    Returns:
        Dictionary with the parsed args structure
    """
    try:
        # Wrap the XML in a root element if it doesn't have one
        if not xml_string.strip().startswith('<list_files>'):
            xml_string = f"<root>{xml_string}</root>"
            root = ET.fromstring(xml_string)
            list_files_element = root.find('list_files')
        else:
            list_files_element = ET.fromstring(xml_string)

        if list_files_element is None:
            return {"error": "Invalid XML format"}

        # Parse args
        args_element = list_files_element.find('args')
        if args_element is None:
            return {"error": "Missing <args> element"}

        # Parse path
        path_element = args_element.find('path')
        path = path_element.text.strip(
        ) if path_element is not None and path_element.text else None

        # Parse recursive flag
        recursive_element = args_element.find('recursive')
        recursive = False
        if recursive_element is not None and recursive_element.text:
            recursive_text = recursive_element.text.strip().lower()
            recursive = recursive_text in ['true', '1', 'yes', 'on']

        return {
            "args": {
                "path": path,
                "recursive": recursive
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
    <list_files>
    <args>
      <path>.</path>
      <recursive>false</recursive>
    </args>
    </list_files>
    """
    result = run(xml_example, current_working_directory)
    # print(json.dumps(result, indent=4))
    print(result)

    xml_example = """
    <list_files>
    <args>
      <path>prompt_toolkit_demo/src/examples/ai_agent/tools</path>
      <recursive>true</recursive>
    </args>
    </list_files>
    """
    result = run(xml_example, current_working_directory)
    # print(json.dumps(result, indent=4))
    print(result)
