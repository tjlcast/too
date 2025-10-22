import os
import xml.etree.ElementTree as ET
from typing import Dict, Any
import json


"""
@function
"""
def write_to_file(xml_string: str, basePath: str = None) -> Dict[str, Any]:
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
    args = parse_write_file_xml(xml_string)
    return _write_to_file(args, basePath)


def _write_to_file(args: Dict[str, Any], basePath: str) -> Dict[str, Any]:
    """
    Write content to one or more files.

    Args:
        args: Dictionary containing file paths and content to write

    Returns:
        Dictionary with results of file writing operations
    """
    try:
        # Extract files from args
        files = args.get('args', {}).get('file', [])
        if not files:
            return {"error": "No files specified"}

        # Handle case where only one file is passed (not in a list)
        if isinstance(files, dict):
            files = [files]

        results = []
        for file_info in files:
            path = file_info.get('path')
            content = file_info.get('content', '')
            line_count = file_info.get('line_count', 0)
            
            if not path:
                continue

            # Resolve path relative to workspace
            full_path = os.path.join(basePath, path)
            
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                results.append({
                    "path": path,
                    "status": "success",
                    "line_count": line_count
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


def parse_write_file_xml(xml_string: str) -> Dict[str, Any]:
    """
    Parse XML string into the args structure for write_to_file tool.

    Args:
        xml_string: XML string representing a write_to_file tool call

    Returns:
        Dictionary with the parsed args structure
    """
    try:
        # Check if this is the simple format (no args/file wrappers)
        root = ET.fromstring(xml_string)
        
        # If root tag is 'write_to_file', parse in the simple format
        if root.tag == 'write_to_file':
            path_element = root.find('path')
            content_element = root.find('content')
            line_count_element = root.find('line_count')
            
            file_info = {"path": "", "content": "", "line_count": 0}
            
            if path_element is not None and path_element.text:
                file_info["path"] = path_element.text.strip()
                
            if content_element is not None:
                # Handle CDATA or plain text content
                file_info["content"] = content_element.text or ""
                
            if line_count_element is not None and line_count_element.text:
                try:
                    file_info["line_count"] = int(line_count_element.text.strip())
                except ValueError:
                    file_info["line_count"] = 0

            return {
                "args": {
                    "file": [file_info]
                }
            }
        else:
            # Handle the args/file format
            write_to_file_element = root if root.tag == 'write_to_file' else root.find('write_to_file')
            
            if write_to_file_element is None:
                return {"error": "Invalid XML format"}

            # Parse args
            args_element = write_to_file_element.find('args')
            if args_element is None:
                return {"error": "Missing <args> element"}

            # Parse files
            file_elements = args_element.findall('file')
            files = []

            for file_element in file_elements:
                path_element = file_element.find('path')
                content_element = file_element.find('content')
                line_count_element = file_element.find('line_count')
                
                file_info = {"path": "", "content": "", "line_count": 0}
                
                if path_element is not None and path_element.text:
                    file_info["path"] = path_element.text.strip()
                    
                if content_element is not None:
                    # Handle CDATA or plain text content
                    file_info["content"] = content_element.text or ""
                    
                if line_count_element is not None and line_count_element.text:
                    try:
                        file_info["line_count"] = int(line_count_element.text.strip())
                    except ValueError:
                        file_info["line_count"] = 0

                files.append(file_info)

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
            "file": [{
                "path": "test.txt",
                "content": "Hello, world!",
                "line_count": 1
            }]
        }
    }
    
    # Convert to XML format for testing
    print("Testing write_to_file function...")
    # result = write_to_file(test_args, str(current_working_directory))
    # print(json.dumps(result, indent=2))