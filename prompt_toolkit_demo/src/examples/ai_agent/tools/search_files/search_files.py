import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Any
import json
import re
from pathlib import Path


"""
@function
"""
def search_files(xml_string: str, basePath: str = None) -> Dict[str, Any]:
    """
    Search for regex patterns across files in a specified directory.

    Args:
        xml_string: XML string representing a search_files tool call
        basePath: Base path to resolve relative directory paths

    Returns:
        Dictionary with results of file search operations
    """
    if basePath is None:
        basePath = os.getcwd()
    args = parse_search_files_xml(xml_string)
    return _search_files(args, basePath)


def _search_files(args: Dict[str, Any], basePath: str) -> Dict[str, Any]:
    """
    Search for regex patterns across files in a specified directory.

    Args:
        args: Dictionary containing search parameters

    Returns:
        Dictionary with results of file search operations
    """
    try:
        # Extract parameters from args
        search_params = args.get('args', {})
        path = search_params.get('path')
        regex_pattern = search_params.get('regex')
        file_pattern = search_params.get('file_pattern', '*')

        if not path:
            return {"error": "Path is required"}
        
        if not regex_pattern:
            return {"error": "Regex pattern is required"}

        # Resolve path relative to workspace
        full_path = os.path.join(basePath, path)
        
        # Check if path exists and is a directory
        if not os.path.exists(full_path):
            return {"error": f"Path does not exist: {full_path}"}
        
        if not os.path.isdir(full_path):
            return {"error": f"Path is not a directory: {full_path}"}

        # Compile regex pattern
        try:
            pattern = re.compile(regex_pattern)
        except re.error as e:
            return {"error": f"Invalid regex pattern: {str(e)}"}

        # Find all matching files
        results = []
        try:
            matched_files = list(Path(full_path).rglob(file_pattern))
            
            # Process each file
            for file_path in matched_files:
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Find all matches in the file
                        matches = []
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if pattern.search(line):
                                # Collect context lines (previous, current, and next line)
                                context_parts = []
                                
                                # Add previous line if it exists
                                if i > 1:
                                    context_parts.append(f"{str(i-1).ljust(5)} | {lines[i-2]}")
                                
                                # Add current matching line
                                context_parts.append(f"{str(i).ljust(5)} | {line}")
                                
                                # Add next line if it exists
                                if i < len(lines):
                                    context_parts.append(f"{str(i+1).ljust(5)} | {lines[i]}")
                                
                                # Join all context lines into a single entry
                                matches.append("\n".join(context_parts))
                        
                        if matches:
                            # Get relative path from search root
                            relative_path = os.path.relpath(str(file_path), basePath)
                            results.append({
                                "path": relative_path,
                                "matches": matches,
                                "status": "success"
                            })
                    
                    except (UnicodeDecodeError, PermissionError, FileNotFoundError):
                        # Skip files that can't be read as text or accessed
                        continue
                        
        except Exception as e:
            return {"error": f"Error during file search: {str(e)}"}

        return {"results": results}

    except Exception as e:
        return {"error": f"Failed to process search_files request: {str(e)}"}


def parse_search_files_xml(xml_string: str) -> Dict[str, Any]:
    """
    Parse XML string into the args structure for search_files tool.

    Args:
        xml_string: XML string representing a search_files tool call

    Returns:
        Dictionary with the parsed args structure
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
            return {"error": "Invalid XML format"}

        # Parse args
        args_element = search_files_element.find('args')
        if args_element is None:
            return {"error": "Missing <args> element"}

        # Parse individual elements
        path_element = args_element.find('path')
        path = path_element.text.strip() if path_element is not None and path_element.text else None
        
        regex_element = args_element.find('regex')
        regex = regex_element.text.strip() if regex_element is not None and regex_element.text else None
        
        file_pattern_element = args_element.find('file_pattern')
        file_pattern = file_pattern_element.text.strip() if file_pattern_element is not None and file_pattern_element.text else "*"

        return {
            "args": {
                "path": path,
                "regex": regex,
                "file_pattern": file_pattern
            }
        }

    except ET.ParseError as e:
        return {"error": f"XML parsing error: {str(e)}"}
    except Exception as e:
        return {"error": f"Error parsing XML: {str(e)}"}