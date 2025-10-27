import os

from typing import Dict, List, Any
import json
from dataclasses import dataclass


# 定义黑名单
BLACKLIST = {'.git', '__pycache__', '.DS_Store',
             'node_modules', '.vscode', '.idea'}


@dataclass
class ListFilesArgs:
    """Arguments for the list files tool."""
    path: str
    recursive: bool = False


def list_files(args: ListFilesArgs, basePath: str = None) -> Dict[str, Any]:
    """
    List files and directories within the specified directory.

    Args:
        xml_string: XML string representing a list_files tool call
        basePath: Base path to resolve relative file paths

    Returns:
        Dictionary with results of directory listing operations
    """
    if basePath is None:
        basePath = os.getcwd()

    # Convert dict args to ListFilesArgs dataclass
    if "error" in args:
        return args

    list_files_args = ListFilesArgs(
        path=args.get("args", {}).get("path", ""),
        recursive=args.get("args", {}).get("recursive", False)
    )

    return _list_files(list_files_args, basePath)


def _list_files(args: ListFilesArgs, basePath: str) -> Dict[str, Any]:
    """
    List files and directories within the specified directory.

    Args:
        args: Structured arguments containing path and recursive flag
        basePath: Base path to resolve relative file paths

    Returns:
        Dictionary with results of directory listing operations
    """
    try:
        # Extract path and recursive flag from args
        path = args.path
        recursive = args.recursive

        if not path:
            return {"error": "No path specified"}

        # Resolve path relative to workspace
        full_path = os.path.join(basePath, path)

        # Check if path exists and is a directory
        if not os.path.exists(full_path):
            return {"error": f"Path does not exist: {full_path}"}

        if not os.path.isdir(full_path):
            return {"error": f"Path is not a directory: {full_path}"}

        # List files and directories
        items = []
        if recursive:
            for root, dirs, files in os.walk(full_path):
                # 过滤目录
                dirs[:] = [d for d in dirs if d not in BLACKLIST]

                rel_root = os.path.relpath(root, full_path)
                if rel_root == ".":
                    rel_root = ""

                for dir_name in dirs:
                    if dir_name in BLACKLIST:
                        continue
                    dir_path = os.path.join(
                        rel_root, dir_name) if rel_root else dir_name
                    items.append({
                        "name": dir_name,
                        "path": dir_path,
                        "type": "directory"
                    })

                for file_name in files:
                    if file_name in BLACKLIST:
                        continue
                    file_path = os.path.join(
                        rel_root, file_name) if rel_root else file_name
                    items.append({
                        "name": file_name,
                        "path": file_path,
                        "type": "file"
                    })
        else:
            for item in os.listdir(full_path):
                if item in BLACKLIST:
                    continue
                item_path = os.path.join(full_path, item)
                items.append({
                    "name": item,
                    "path": item,
                    "type": "directory" if os.path.isdir(item_path) else "file"
                })

        return {
            "path": path,
            "recursive": recursive,
            "items": sorted(items, key=lambda x: (x['path'], x['type'], x['name']))
        }

    except Exception as e:
        return {"error": f"Failed to process list_files request: {str(e)}"}


# For testing purposes
if __name__ == "__main__":
    from pathlib import Path
    current_working_directory = Path.cwd()

    # Test the function
    test_args = {
        "args": {
            "path": ".",
            "recursive": False
        }
    }
    result = _list_files(test_args, current_working_directory)
    print(json.dumps(result, indent=2))

    # Test XML parsing
    xml_example = """
    <list_files>
    <args>
      <path>.</path>
      <recursive>false</recursive>
    </args>
    </list_files>
    """

    parsed_args = parse_list_files_xml(xml_example)
    print("\nParsed XML:")
    print(json.dumps(parsed_args, indent=2))
    result = _list_files(parsed_args, current_working_directory)
    print(json.dumps(result, indent=2))

    xml_example = """
    <list_files>
    <args>
      <path>.</path>
      <recursive>true</recursive>
    </args>
    </list_files>
    """
    print(list_files(xml_example))
