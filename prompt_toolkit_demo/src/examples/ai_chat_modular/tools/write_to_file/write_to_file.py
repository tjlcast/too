import os
from typing import Dict, Any, List
import json
import difflib
from dataclasses import dataclass


@dataclass
class FileInfo:
    """Information about a file to be written."""
    path: str
    content: str = ""
    line_count: int = 0


@dataclass
class WriteToFileArgs:
    """Arguments for the write to file tool."""
    file: List[FileInfo]


def write_to_file(args: WriteToFileArgs, basePath: str = None) -> Dict[str, Any]:
    """
    Write content to one or more files.

    Args:
        xml_string: XML string representing a write_to_file tool call
        basePath: Base path to resolve relative file paths

    Returns:
        Dictionary with results of file writing operations
    """
    if basePath is None:
        basePath = os.getcwd()
    return _write_to_file(args, basePath)


def _write_to_file(args: WriteToFileArgs, basePath: str) -> Dict[str, Any]:
    """
    Write content to one or more files.

    Args:
        args: WriteToFileArgs containing file paths and content to write

    Returns:
        Dictionary with results of file writing operations
    """
    try:
        # Extract files from args
        files = args.file
        if not files:
            return {"error": "No files specified"}

        # Handle case where only one file is passed (not in a list)
        if isinstance(files, dict):
            files = [files]

        results = []
        for file_info in files:
            content_diff = ""
            operation = "created"
            path = file_info.get('path')
            content = file_info.get('content', '')
            line_count = file_info.get('line_count', 0)

            if not path:
                continue

            # Resolve path relative to workspace
            full_path = os.path.join(basePath, path)

            # Read old content if file exists
            old_content = ""
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        old_content = f.read()
                        operation = "modified"
                except Exception:
                    # If we can't read the old file, treat as if it's empty
                    old_content = ""

            # Generate diff
            old_lines = old_content.splitlines(keepends=True)
            new_lines = content.splitlines(keepends=True)
            diff = difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=f'a/{path}',
                tofile=f'b/{path}',
                lineterm=''
            )
            content_diff = ''.join(diff)

            # Create directories if they don't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                results.append({
                    "path": path,
                    "status": "success",
                    "line_count": line_count,
                    "user_edits": content_diff,
                    "operation": operation,
                })
            except Exception as e:
                results.append({
                    "path": path,
                    "status": "error",
                    "error": str(e)
                })

        return {"results": results}

    except Exception as e:
        return {"error": f"Failed to process write_to_file request: {str(e)}"}


# For testing purposes
if __name__ == "__main__":
    from pathlib import Path
    current_working_directory = Path.cwd()

    # Test the function
    test_args = WriteToFileArgs(
        file=[FileInfo(
            path="test.txt",
            content="Hello, world!",
            line_count=1
        )]
    )

    # Convert to XML format for testing
    print("Testing write_to_file function...")
    # result = write_to_file(test_args, str(current_working_directory))
    # print(json.dumps(result, indent=2))
