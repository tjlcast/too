import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Any
import json

from .search_files import SearchArgs, search_files


def run(xml_string: str, basePath: str = None) -> str:
    """
    ## search_files
    Description: Request to perform a regex search across files in a specified directory, providing context-rich results. This tool searches for patterns or specific content across multiple files, displaying each match with encapsulating context.

    **IMPORTANT: You can search in a maximum of 100 files in a single request.** If you need to search in more files, narrow down your search using the file_pattern parameter.


    Parameters:
    - args: Contains search parameters:
      - path: (required) The path of the directory to search in (relative to workspace directory c:\\Users\\phx10\\code\\prompt_toolkit)
      - regex: (required) The regular expression pattern to search for. Uses Python regex syntax.
      - file_pattern: (optional) Glob pattern to filter files (e.g., '*.py' for Python files). If not provided, it will search all files (*).

    Usage:
    <search_files>
    <args>
      <path>Directory path here</path>
      <regex>Your regex pattern here</regex>
      <file_pattern>file pattern here (optional)</file_pattern>
    </args>
    </search_files>

    Examples:

    1. Searching for all .py files in the current directory:
    <search_files>
    <args>
      <path>.</path>
      <regex>.*</regex>
      <file_pattern>*.py</file_pattern>
    </args>
    </search_files>

    2. Searching for function definitions in the src directory:
    <search_files>
    <args>
      <path>src</path>
      <regex>def \\w+\\(</regex>
    </args>
    </search_files>

    3. Searching for TODO comments in JavaScript files:
    <search_files>
    <args>
      <path>.</path>
      <regex>TODO</regex>
      <file_pattern>*.js</file_pattern>
    </args>
    </search_files>
    """
    args = parse_xml_args(xml_string)
    return execute(args, basePath)


def execute(args: SearchArgs, basePath: str = None) -> str:
    result = search_files(args, basePath)

    # 如果有错误，直接返回错误信息
    if "error" in result:
        return json.dumps(result, indent=2, ensure_ascii=False)

    # 格式化输出结果
    results = result.get("results", [])
    if not results:
        return "Found 0 results."

    # 按文件路径分组结果
    file_groups = {}
    total_matches = 0

    for res in results:
        path = res.get("path", "")
        matches = res.get("matches", [])
        total_matches += len(matches)

        if path not in file_groups:
            file_groups[path] = []
        file_groups[path].extend(matches)

    output_lines = [f"Found {total_matches} results.\n"]

    # 为每个文件输出所有匹配项
    for path, matches in file_groups.items():
        output_lines.append(f"# {path}")
        for match in matches:
            # 添加匹配行，确保正确缩进
            for line in match.split('\n'):
                output_lines.append(f" {line}")
            output_lines.append("----")
        output_lines.append('\n')

    return '\n'.join(output_lines)


def parse_xml_args(xml_string: str) -> SearchArgs:
    """
    Parse XML string into the args structure for search_files tool.

    Args:
        xml_string: XML string representing a search_files tool call

    Returns:
        SearchArgs with the parsed parameters
    """
    try:
        # Wrap the XML in a root element if it doesn't have one
        if not xml_string.strip().startswith('<search_files>'):
            xml_string = f"<root>{xml_string}</root>"
            root = ET.fromstring(xml_string)
            search_files_element = root.find('search_files')
        else:
            search_files_element = ET.fromstring(xml_string)

        if search_files_element is None:
            raise ValueError("Invalid XML format")

        # Parse args
        args_element = search_files_element.find('args')
        if args_element is None:
            raise ValueError("Missing <args> element")

        # Parse individual elements
        path_element = args_element.find('path')
        path = path_element.text.strip(
        ) if path_element is not None and path_element.text else None

        regex_element = args_element.find('regex')
        regex = regex_element.text.strip(
        ) if regex_element is not None and regex_element.text else None

        file_pattern_element = args_element.find('file_pattern')
        file_pattern = file_pattern_element.text.strip(
        ) if file_pattern_element is not None and file_pattern_element.text else "*"

        return SearchArgs(
            path=path,
            regex=regex,
            file_pattern=file_pattern
        )

    except ET.ParseError as e:
        raise ValueError(f"XML parsing error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing XML: {str(e)}")


# For testing purposes
if __name__ == "__main__":
    from pathlib import Path
    current_working_directory = Path.cwd()

    # xml_example = """
    # <search_files>
    # <args>
    #   <path>prompt_toolkit_demo/src</path>
    #   <regex>def \\w+\\(</regex>
    #   <file_pattern>*.py</file_pattern>
    # </args>
    # </search_files>
    # """
    # print(run(xml_example, current_working_directory))

    xml_example = """
    <search_files>
    <args>
    <path>prompt_toolkit_demo/src</path>
    <regex>for</regex>
    <file_pattern>*.py</file_pattern>
    </args>
    </search_files>
    """
    result = run(xml_example, current_working_directory)
    print(result)
