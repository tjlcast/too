import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Any
import json
import difflib


"""
@function
"""


def insert_content(xml_string: str, basePath: str = None) -> Dict[str, Any]:
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
    args = parse_insert_content_xml(xml_string)
    return _insert_content(args, basePath)


def _insert_content(args: Dict[str, Any], basePath: str) -> Dict[str, Any]:
    """
    Insert content into a file at a specific line number.

    Args:
        args: Dictionary containing file paths and content to insert
        basePath: Base path to resolve relative file paths

    Returns:
        Dictionary with results of content insertion operations
    """
    try:
        # Extract insertions from args
        insertions = args.get('args', {}).get('insertion', [])
        if not insertions:
            return {"error": "No insertions specified"}

        # Handle case where only one insertion is passed (not in a list)
        if isinstance(insertions, dict):
            insertions = [insertions]

        # Limit to 5 insertions as per specification
        if len(insertions) > 5:
            insertions = insertions[:5]

        results = []
        for insertion in insertions:
            path = insertion.get('path')
            line = insertion.get('line')
            content = insertion.get('content')

            if not path:
                results.append({
                    "path": path,
                    "status": "error",
                    "error": "Missing path"
                })
                continue

            if line is None:
                results.append({
                    "path": path,
                    "status": "error",
                    "error": "Missing line number"
                })
                continue

            if content is None:
                results.append({
                    "path": path,
                    "status": "error",
                    "error": "Missing content"
                })
                continue

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

                # Handle appending to end of file (line 0)
                if int(line) == 0:
                    lines.append(content + '\n')
                    inserted_lines = [content + '\n']
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
                    continue

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


def parse_insert_content_xml(xml_string: str) -> Dict[str, Any]:
    """
    Parse XML string into the args structure for insert_content tool.

    Args:
        xml_string: XML string representing a insert_content tool call

    Returns:
        Dictionary with the parsed args structure
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
            return {"error": "Invalid XML format"}

        # Parse args
        args_element = insert_content_element.find('args')
        if args_element is None:
            return {"error": "Missing <args> element"}

        # Parse insertions
        insertion_elements = args_element.findall('insertion')
        insertions = []

        for insertion_element in insertion_elements:
            path_element = insertion_element.find('path')
            line_element = insertion_element.find('line')
            content_element = insertion_element.find('content')

            insertion = {}
            if path_element is not None and path_element.text:
                insertion["path"] = path_element.text.strip()

            if line_element is not None and line_element.text:
                insertion["line"] = line_element.text.strip()

            if content_element is not None and content_element.text:
                insertion["content"] = content_element.text.strip()

            insertions.append(insertion)

        return {
            "args": {
                "insertion": insertions
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

    # Test the function
    test_args = {
        "args": {
            "insertion": [
                {
                    "path": "test.txt",
                    "line": "1",
                    "content": "This is a test line"
                }
            ]
        }
    }
    result = _insert_content(test_args, current_working_directory)
    print(json.dumps(result, indent=2))

    # Test XML parsing
    xml_example = """
    <insert_content>
    <args>
      <insertion>
        <path>src/example/ai_agent/tools/test.py</path>
        <line>1</line>
        <content>print('Hello World')</content>
      </insertion>
    </args>
    </insert_content>
    """

    parsed_args = parse_insert_content_xml(xml_example)
    print("\nParsed XML:")
    print(json.dumps(parsed_args, indent=2))
    result = _insert_content(parsed_args, current_working_directory)
    print(json.dumps(result, indent=2))
