import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Any
import json

from .search_files import search_files


def run(xml_string: str, basePath: str = None) -> Dict[str, Any]:
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
    return search_files(xml_string, basePath)


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
    <regex>.*</regex>
    <file_pattern>*.py</file_pattern>
    </args>
    </search_files>
    """
    print(run(xml_example, current_working_directory))