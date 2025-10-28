import os

from typing import Dict, List, Any
import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class FileInfo:
    """Information about a file to be read."""
    path: str


@dataclass
class ReadFileArgs:
    """Arguments for the read file tool."""
    file: List[FileInfo]


def read_file(args: ReadFileArgs, basePath: str = None) -> Dict[str, Any]:
    """
    Read the contents of one or more files.

    Args:
        xml_string: XML string representing a read_file tool call
        basePath: Base path to resolve relative file paths

    Returns:
        Dictionary with results of file reading operations
    """
    if basePath is None:
        basePath = os.getcwd()
    return _read_file(args, basePath)


def _read_file(args: ReadFileArgs, basePath: str) -> Dict[str, Any]:
    """
    Read the contents of one or more files.

    Args:
        args: Structured arguments containing file paths to read
        basePath: Base path to resolve relative file paths

    Returns:
        Dictionary with results of file reading operations
    """
    try:
        # Extract files from args
        files = args.file
        if not files:
            return {"error": "No files specified"}

        # Limit to 5 files as per specification
        if len(files) > 5:
            files = files[:5]

        results = []
        for file_info in files:
            path = file_info.path
            if not path:
                continue

            # Resolve path relative to workspace
            # In a real implementation, workspace_dir would be configured properly
            full_path = os.path.join(basePath, path)

            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Add line numbers to content
                    lines = content.split('\n')
                    # 计算总行数以确定行号的宽度
                    total_lines = len(lines)
                    width = len(str(total_lines))
                    # 格式化行号，右对齐
                    numbered_lines = [
                        f"{i+1:>{width}} | {line}" for i, line in enumerate(lines)]
                    formatted_content = '\n'.join(numbered_lines)

                    results.append({
                        "path": path,
                        "content": formatted_content,
                        "status": "success"
                    })
            except FileNotFoundError:
                results.append({
                    "path": path,
                    "content": None,
                    "status": "error",
                    "error": f"File not found: {full_path}"
                })
            except Exception as e:
                results.append({
                    "path": path,
                    "content": None,
                    "status": "error",
                    "error": str(e)
                })

        return {"results": results}

    except Exception as e:
        return {"error": f"Failed to process read_file request: {str(e)}"}


# For testing purposes
if __name__ == "__main__":
    print("Testing read_file tool...")
    from pathlib import Path
    current_working_directory = Path.cwd()

    # Test the function
    print("Testing 1 start.")
    test_args = ReadFileArgs(
        file=[
            FileInfo(path="test.txt"),
            FileInfo(path="test.json")
        ]
    )
    result = _read_file(test_args, current_working_directory)
    print(json.dumps(result, indent=2))

    print("Testing 2 start.")
    # Test XML parsing
    xml_example = """
    <read_file>
    <args>
      <file>
        <path>prompt_toolkit_demo/src/examples/ai_chat_modular/tools/read_file/read_file.py</path>
      </file>
      <file>
        <path>src/main.py</path>
      </file>
    </args>
    </read_file>
    """

    from .run import parse_xml_args
    parsed_args = parse_xml_args(xml_example)
    result = _read_file(parsed_args, current_working_directory)
    print(json.dumps(result, indent=2))

    print("Testing 3 start.")
    xml_example = """
    <read_file>
    <args>
      <file>
        <path>src/example/ai_agent/tools/read_file.py</path>
      </file>
      <file>
        <path>src/main.py</path>
      </file>
    </args>
    </read_file>
    """
    print(read_file(parse_xml_args(xml_example)))
