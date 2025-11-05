import os

from typing import Dict, List, Any
import json
import difflib
from dataclasses import dataclass
from typing import Optional


@dataclass
class InsertContentArgs:
    """Represents the arguments for insert_content function."""
    path: str
    line: str
    content: str


def insert_content(args: InsertContentArgs, basePath: str = None) -> Dict[str, Any]:
    """
    Insert content into a file at a specific line number.

    Args:
        xml_string: XML string representing a insert_content tool call
        basePath: Base path to resolve relative file paths

    Returns:
        Dictionary with results of content insertion operations
    """
    if basePath is None:
        basePath = os.getcwd()
    return _insert_content(args, basePath)


def _insert_content(args: InsertContentArgs, basePath: str) -> Dict[str, Any]:
    """
    Insert content into a file at a specific line number.

    Args:
        args: InsertContentArgs containing file paths and content to insert
        basePath: Base path to resolve relative file paths

    Returns:
        Dictionary with results of content insertion operations
    """
    try:
        # Extract insertions from args
        path = args.path
        if not path:
            return {"error": "No path specified"}

        results = []
        path = args.path
        line = args.line
        content = args.content

        if not path:
            results.append({
                "path": path,
                "status": "error",
                "error": "Missing path"
            })
            return results

        if line is None:
            results.append({
                "path": path,
                "status": "error",
                "error": "Missing line number"
            })
            return results

        if content is None:
            results.append({
                "path": path,
                "status": "error",
                "error": "Missing content"
            })
            return results

        # Resolve path relative to workspace
        full_path = os.path.join(basePath, path)

        try:
            # Read old content if file exists
            old_content = ""
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        old_content = f.read()
                except Exception:
                    # If we can't read the old file, treat as if it's empty
                    old_content = ""

            # Read the file
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Convert line number to 0-based index
            line_index = int(line) - 1

            # Handle appending to end of file, should start at new line  (line 0)
            if int(line) == 0:
                lines.append('\n' + content + '\n')
                inserted_lines = ['\n' + content + '\n']
            # Handle inserting at specific line
            elif 0 <= line_index <= len(lines):
                # Split content into lines and add to file
                content_lines = content.split('\n')
                inserted_lines = []
                for i, content_line in enumerate(reversed(content_lines)):
                    lines.insert(line_index, content_line + '\n')
                    inserted_lines.append(content_line + '\n')
                inserted_lines.reverse()  # Reverse back to original order
            else:
                results.append({
                    "path": path,
                    "status": "error",
                    "error": f"Invalid line number: {line}. Valid range is 0-{len(lines)}"
                })
                return results

            # Write the file back
            with open(full_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            # Generate diff
            new_content = "".join(lines)
            old_lines = old_content.splitlines(keepends=True)
            new_lines = new_content.splitlines(keepends=True)
            diff = difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=f'a/{path}',
                tofile=f'b/{path}',
                lineterm=''
            )
            content_diff = ''.join(diff)

            # Determine operation type
            operation = "modified"
            if not old_content:
                operation = "created"

            results.append({
                "path": path,
                "line": line,
                "content": content,
                "status": "success",
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
        return {"error": f"Failed to process insert_content request: {str(e)}"}


# For testing purposes
if __name__ == "__main__":
    from pathlib import Path
    current_working_directory = Path.cwd()

    # Test the function
    test_args = InsertContentArgs(
        path="test.txt",
        line="0",
        content="This is a test line"
    )
    result = _insert_content(test_args, str(current_working_directory))
    print(json.dumps(result, indent=2))

    # Test XML parsing
    xml_example = """
    <insert_content>
        <path>src/example/ai_agent/tools/test.py</path>
        <line>1</line>
        <content>print('Hello World')</content>
    </insert_content>
    """
    from .run import parse_insert_content_xml
    parsed_args = parse_insert_content_xml(xml_example)
    print("\nParsed XML:")
    result = _insert_content(parsed_args, str(current_working_directory))
    print(json.dumps(result, indent=2))
    assert json.dumps(result).index("No such file or directory") > 0
