desc = """
## list_files
Description: Request to list files and directories within the specified directory. If recursive is true, it will list all files and directories recursively. If recursive is false or not provided, it will only list the top-level contents. Do not use this tool to confirm the existence of files you may have created, as the user will let you know if the files were created successfully or not.
Parameters:
- path: (required) The path of the directory to list contents for (relative to workspace directory c:\\Users\\phx10\\code\\cg-manager)
- recursive: (optional) Whether to list files recursively. Use true for recursive listing, false or omit for top-level only.
Usage:
<list_files>
<path>Directory path here</path>
<recursive>true or false (optional)</recursive>
</list_files>

Example: Requesting to list all files in the current directory
<list_files>
<path>.</path>
<recursive>false</recursive>
</list_files>

Output Format:
The tool returns a JSON object with the following structure:
{
  "path": "the path that was listed",
  "recursive": boolean indicating whether listing was recursive,
  "items": [
    {
      "name": "filename or directory name",
      "path": "relative path from the specified directory", 
      "type": "file or directory"
    },
    ...
  ]
}
"""
