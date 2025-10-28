from typing import Dict, Any
import os

import xml.etree.ElementTree as ET
from .search_and_replace import SearchAndReplaceArgs, search_and_replace


def run(xml_string: str, basePath: str = None) -> str:

    args = parse_search_and_replace_xml(xml_string)
    if "error" in args:
        return args

    # Convert dict args to SearchAndReplaceArgs object
    structured_args = SearchAndReplaceArgs(
        path=args.get('path', ''),
        search=args.get('search', ''),
        replace=args.get('replace', ''),
        start_line=args.get('start_line'),
        end_line=args.get('end_line'),
        use_regex=args.get('use_regex', False),
        ignore_case=args.get('ignore_case', False)
    )

    return execute(structured_args, basePath)


def execute(args: SearchAndReplaceArgs, basePath: str) -> str:

    search_and_replace_results = search_and_replace(args, basePath)

    # 构建返回的字符串格式，按照示例格式
    if search_and_replace_results:
        file_result = search_and_replace_results.get("results")[0]  # 只处理第一个文件
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


def parse_search_and_replace_xml(xml_string: str) -> Dict[str, Any]:
    """
    Parse XML string into parameters for search_and_replace tool.

    Args:
        xml_string: XML string representing a search_and_replace tool call

    Returns:
        Dictionary with the parsed parameters
    """
    try:
        root = ET.fromstring(xml_string)

        # Check if this is the correct format
        if root.tag != 'search_and_replace':
            return {"error": "Invalid XML format: root tag must be 'search_and_replace'"}

        # Extract required parameters
        path_element = root.find('path')
        search_element = root.find('search')
        replace_element = root.find('replace')

        if path_element is None or path_element.text is None:
            return {"error": "Missing required 'path' parameter"}

        if search_element is None or search_element.text is None:
            return {"error": "Missing required 'search' parameter"}

        if replace_element is None:
            replace_text = ""
        else:
            replace_text = replace_element.text or ""

        result = {
            "path": path_element.text.strip(),
            "search": search_element.text.strip(),
            "replace": replace_text
        }

        # Extract optional parameters
        start_line_element = root.find('start_line')
        if start_line_element is not None and start_line_element.text:
            try:
                result["start_line"] = int(start_line_element.text.strip())
            except ValueError:
                pass  # Ignore invalid start_line

        end_line_element = root.find('end_line')
        if end_line_element is not None and end_line_element.text:
            try:
                result["end_line"] = int(end_line_element.text.strip())
            except ValueError:
                pass  # Ignore invalid end_line

        use_regex_element = root.find('use_regex')
        if use_regex_element is not None and use_regex_element.text:
            result["use_regex"] = use_regex_element.text.strip().lower() == "true"

        ignore_case_element = root.find('ignore_case')
        if ignore_case_element is not None and ignore_case_element.text:
            result["ignore_case"] = ignore_case_element.text.strip().lower() == "true"

        return result

    except ET.ParseError as e:
        return {"error": f"XML parsing error: {str(e)}"}
    except Exception as e:
        return {"error": f"Error parsing XML: {str(e)}"}


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
