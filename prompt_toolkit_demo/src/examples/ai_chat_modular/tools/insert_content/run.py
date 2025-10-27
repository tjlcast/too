from typing import Dict, Any


import xml.etree.ElementTree as ET

from .insert_content import InsertContentArgs, Insertion, insert_content


def run(xml_string: str, basePath: str = None) -> str:
    exec_args = parse_insert_content_xml(xml_string)
    return execute(exec_args, basePath)


def execute(exec_args: InsertContentArgs, basePath: str = None) -> str:
    result = insert_content(exec_args, basePath)

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


def parse_insert_content_xml(xml_string: str) -> InsertContentArgs:
    """
    Parse XML string into the args structure for insert_content tool.

    Args:
        xml_string: XML string representing a insert_content tool call

    Returns:
        InsertContentArgs with the parsed args structure
    """
    try:
        # Wrap the XML in a root element if it doesn't have one
        if not xml_string.strip().startswith('<insert_content>'):
            xml_string = f"<root>{xml_string}</root>"
            root = ET.fromstring(xml_string)
            insert_content_element = root.find('insert_content')
        else:
            insert_content_element = ET.fromstring(xml_string)

        if insert_content_element is None:
            raise ValueError("Invalid XML format")

        # Parse args
        args_element = insert_content_element.find('args')
        if args_element is None:
            raise ValueError("Missing <args> element")

        # Parse insertions
        insertion_elements = args_element.findall('insertion')
        insertions = []

        for insertion_element in insertion_elements:
            path_element = insertion_element.find('path')
            line_element = insertion_element.find('line')
            content_element = insertion_element.find('content')

            path = ""
            line = ""
            content = ""

            if path_element is not None and path_element.text:
                path = path_element.text.strip()

            if line_element is not None and line_element.text:
                line = line_element.text.strip()

            if content_element is not None and content_element.text:
                content = content_element.text.strip()

            insertions.append(Insertion(path=path, line=line, content=content))

        return InsertContentArgs(insertion=insertions)

    except ET.ParseError as e:
        raise ValueError(f"XML parsing error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing XML: {str(e)}")


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
