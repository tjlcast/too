import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Any
import json


"""
@function
"""
def read_file(xml_string: str, basePath: str = None) -> Dict[str, Any]:
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
    args = parse_read_file_xml(xml_string)
    return _read_file(args, basePath)


def _read_file(args: Dict[str, Any], basePath: str) -> Dict[str, Any]:
    """
    Read the contents of one or more files.

    Args:
        args: Dictionary containing file paths to read

    Returns:
        Dictionary with results of file reading operations
    """
    try:
        # Extract files from args
        files = args.get('args', {}).get('file', [])
        if not files:
            return {"error": "No files specified"}

        # Handle case where only one file is passed (not in a list)
        if isinstance(files, dict):
            files = [files]

        # Limit to 5 files as per specification
        if len(files) > 5:
            files = files[:5]

        results = []
        for file_info in files:
            path = file_info.get('path')
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
                    numbered_lines = [
                        f"{i+1} | {line}" for i, line in enumerate(lines)]
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


def parse_read_file_xml(xml_string: str) -> Dict[str, Any]:
    """
    Parse XML string into the args structure for read_file tool.

    Args:
        xml_string: XML string representing a read_file tool call

    Returns:
        Dictionary with the parsed args structure
    """
    try:
        # Wrap the XML in a root element if it doesn't have one
        if not xml_string.strip().startswith('<read_file>'):
            xml_string = f"<root>{xml_string}</root>"
            root = ET.fromstring(xml_string)
            read_file_element = root.find('read_file')
        else:
            read_file_element = ET.fromstring(xml_string)

        if read_file_element is None:
            return {"error": "Invalid XML format"}

        # Parse args
        args_element = read_file_element.find('args')
        if args_element is None:
            return {"error": "Missing <args> element"}

        # Parse files
        file_elements = args_element.findall('file')
        files = []

        for file_element in file_elements:
            path_element = file_element.find('path')
            if path_element is not None and path_element.text:
                files.append({"path": path_element.text.strip()})

        return {
            "args": {
                "file": files
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
            "file": [
                {"path": "test.txt"},
                {"path": "another_test.txt"}
            ]
        }
    }
    result = _read_file(test_args, current_working_directory)
    print(json.dumps(result, indent=2))

    # Test XML parsing
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

    parsed_args = parse_read_file_xml(xml_example)
    print("\nParsed XML:")
    print(json.dumps(parsed_args, indent=2))
    result = _read_file(parsed_args, current_working_directory)
    print(json.dumps(result, indent=2))
    
    
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
    print(read_file(xml_example))
