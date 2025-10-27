import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Any
import json
import re
from pathlib import Path
from dataclasses import dataclass


@dataclass
class SearchArgs:
    path: str
    regex: str
    file_pattern: str = "*"


def search_files(args: SearchArgs, basePath: str = None) -> Dict[str, Any]:
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
    return _search_files(args, basePath)


def _search_files(args: SearchArgs, basePath: str) -> Dict[str, Any]:
    """
    Search for regex patterns across files in a specified directory.

    Args:
        args: SearchArgs containing search parameters

    Returns:
        Dictionary with results of file search operations
    """
    try:
        # Extract parameters from args
        path = args.path
        regex_pattern = args.regex
        file_pattern = args.file_pattern

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
                                    context_parts.append(
                                        f"{str(i-1).ljust(5)} | {lines[i-2]}")

                                # Add current matching line
                                context_parts.append(
                                    f"{str(i).ljust(5)} | {line}")

                                # Add next line if it exists
                                if i < len(lines):
                                    context_parts.append(
                                        f"{str(i+1).ljust(5)} | {lines[i]}")

                                # Join all context lines into a single entry
                                matches.append("\n".join(context_parts))

                        if matches:
                            # Get relative path from search root
                            relative_path = os.path.relpath(
                                str(file_path), basePath)
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
