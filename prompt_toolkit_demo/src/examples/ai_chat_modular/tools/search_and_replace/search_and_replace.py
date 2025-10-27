import os
import xml.etree.ElementTree as ET
import re
import difflib
from typing import Dict, Any


def search_and_replace(xml_string: str, basePath: str = None) -> Dict[str, Any]:
    """
    Search and replace content in a file.

    Args:
        xml_string: XML string representing a search_and_replace tool call
        basePath: Base path to resolve relative file paths

    Returns:
        Dictionary with results of search and replace operations
    """
    if basePath is None:
        basePath = os.getcwd()
    
    args = parse_search_and_replace_xml(xml_string)
    if "error" in args:
        return args
    
    return _search_and_replace(args, basePath)


def _search_and_replace(args: Dict[str, Any], basePath: str) -> Dict[str, Any]:
    """
    Search and replace content in a file.

    Args:
        args: Dictionary containing file path, search term, replacement text and options
        basePath: Base path to resolve relative file paths

    Returns:
        Dictionary with results of search and replace operations
    """
    try:
        # Extract parameters from args
        path = args.get('path', '')
        search_term = args.get('search', '')
        replace_term = args.get('replace', '')
        start_line = args.get('start_line')
        end_line = args.get('end_line')
        use_regex = args.get('use_regex', False)
        ignore_case = args.get('ignore_case', False)

        if not path:
            return {"error": "No file path specified"}

        if not search_term:
            return {"error": "No search term specified"}

        # Resolve path relative to workspace
        full_path = os.path.join(basePath, path)
        
        # Check if file exists
        if not os.path.exists(full_path):
            return {"error": f"File not found: {path}"}

        # Read file content
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Failed to read file {path}: {str(e)}"}

        # Split content into lines for line-based operations
        lines = content.splitlines(keepends=True)
        
        # Determine line range to operate on
        start_idx = 0 if start_line is None else max(0, int(start_line) - 1)
        end_idx = len(lines) if end_line is None else min(len(lines), int(end_line))
        
        # Work with the subset of lines
        target_lines = lines[start_idx:end_idx]
        target_content = ''.join(target_lines)
        
        # Perform search and replace
        if use_regex:
            flags = re.IGNORECASE if ignore_case else 0
            try:
                pattern = re.compile(search_term, flags)
                new_content = pattern.sub(replace_term, target_content)
            except re.error as e:
                return {"error": f"Invalid regex pattern: {str(e)}"}
        else:
            # Plain text search and replace
            if ignore_case:
                # For case insensitive replacement, we need a custom approach
                def replace_ignore_case(text, old, new):
                    pattern = re.compile(re.escape(old), re.IGNORECASE)
                    return pattern.sub(new, text)
                new_content = replace_ignore_case(target_content, search_term, replace_term)
            else:
                new_content = target_content.replace(search_term, replace_term)
        
        # Reconstruct the full content with modifications
        if new_content != target_content:
            # There were changes, reconstruct the full file
            new_lines = new_content.splitlines(keepends=True)
            # Ensure we have the right number of line endings
            if target_content.endswith('\n') and not new_content.endswith('\n') and len(target_lines) > 0:
                if target_lines[-1].endswith('\n') and len(new_lines) > 0:
                    new_lines[-1] += '\n'
            
            # Create the final content
            final_lines = lines[:start_idx] + new_lines + lines[end_idx:]
            final_content = ''.join(final_lines)
        else:
            # No changes made
            final_content = content

        # Generate diff
        old_lines = content.splitlines(keepends=True)
        new_lines = final_content.splitlines(keepends=True)
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f'a/{path}',
            tofile=f'b/{path}',
            lineterm=''
        )
        content_diff = ''.join(diff)

        # Write the file if there are changes
        operation = "no changes"
        if content != final_content:
            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(final_content)
                operation = "updated"
            except Exception as e:
                return {"error": f"Failed to write file {path}: {str(e)}"}

        return {
            "results": [{
                "path": path,
                "status": "success",
                "user_edits": content_diff,
                "operation": operation,
            }]
        }

    except Exception as e:
        return {"error": f"Failed to process search_and_replace request: {str(e)}"}


def parse_search_and_replace_xml(xml_string: str) -> Dict[str, Any]:
    """
    Parse XML string into parameters for search_and_replace tool.

    Args:
        xml_string: XML string representing a search_and_replace tool call

    Returns:
        Dictionary with the parsed parameters
    """
    try:
        root = ET.fromstring(xml_string)

        # Check if this is the correct format
        if root.tag != 'search_and_replace':
            return {"error": "Invalid XML format: root tag must be 'search_and_replace'"}

        # Extract required parameters
        path_element = root.find('path')
        search_element = root.find('search')
        replace_element = root.find('replace')

        if path_element is None or path_element.text is None:
            return {"error": "Missing required 'path' parameter"}
        
        if search_element is None or search_element.text is None:
            return {"error": "Missing required 'search' parameter"}
        
        if replace_element is None:
            replace_text = ""
        else:
            replace_text = replace_element.text or ""

        result = {
            "path": path_element.text.strip(),
            "search": search_element.text.strip(),
            "replace": replace_text
        }

        # Extract optional parameters
        start_line_element = root.find('start_line')
        if start_line_element is not None and start_line_element.text:
            try:
                result["start_line"] = int(start_line_element.text.strip())
            except ValueError:
                pass  # Ignore invalid start_line

        end_line_element = root.find('end_line')
        if end_line_element is not None and end_line_element.text:
            try:
                result["end_line"] = int(end_line_element.text.strip())
            except ValueError:
                pass  # Ignore invalid end_line

        use_regex_element = root.find('use_regex')
        if use_regex_element is not None and use_regex_element.text:
            result["use_regex"] = use_regex_element.text.strip().lower() == "true"

        ignore_case_element = root.find('ignore_case')
        if ignore_case_element is not None and ignore_case_element.text:
            result["ignore_case"] = ignore_case_element.text.strip().lower() == "true"

        return result

    except ET.ParseError as e:
        return {"error": f"XML parsing error: {str(e)}"}
    except Exception as e:
        return {"error": f"Error parsing XML: {str(e)}"}