import os

import re
import difflib
from typing import Dict, Any, Optional


class SearchAndReplaceArgs:
    """Structure for search_and_replace function arguments."""

    def __init__(self, path: str, search: str, replace: str,
                 start_line: Optional[int] = None, end_line: Optional[int] = None,
                 use_regex: bool = False, ignore_case: bool = False):
        self.path = path
        self.search = search
        self.replace = replace
        self.start_line = start_line
        self.end_line = end_line
        self.use_regex = use_regex
        self.ignore_case = ignore_case


def search_and_replace(search_and_replace_args: SearchAndReplaceArgs, basePath: str = None) -> Dict[str, Any]:
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

    return _search_and_replace(search_and_replace_args, basePath)


def _search_and_replace(args: SearchAndReplaceArgs, basePath: str) -> Dict[str, Any]:
    """
    Search and replace content in a file.

    Args:
        args: SearchAndReplaceArgs containing file path, search term, replacement text and options
        basePath: Base path to resolve relative file paths

    Returns:
        Dictionary with results of search and replace operations
    """
    try:
        # Extract parameters from args
        path = args.path
        search_term = args.search
        replace_term = args.replace
        start_line = args.start_line
        end_line = args.end_line
        use_regex = args.use_regex
        ignore_case = args.ignore_case

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
        end_idx = len(lines) if end_line is None else min(
            len(lines), int(end_line))

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
                new_content = replace_ignore_case(
                    target_content, search_term, replace_term)
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
                operation = "modified"
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
