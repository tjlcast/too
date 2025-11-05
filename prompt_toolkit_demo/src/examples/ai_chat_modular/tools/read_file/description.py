desc = """
## read_file
Description: Request to read the contents of one or more files. The tool outputs line-numbered content (e.g. "1 | const x = 1") for easy reference when creating diffs or discussing code. Supports text extraction from PDF and DOCX files, but may not handle other binary files properly.

**IMPORTANT: You can read a maximum of 5 files in a single request.** If you need to read more files, use multiple sequential read_file requests.


Parameters:
- args: Contains one or more file elements, where each file contains:
  - path: (required) File path (relative to workspace directory C:\Users\phx10\code\cg-manager)
  

Usage:
<read_file>
<args>
  <file>
    <path>path/to/file</path>
    
  </file>
</args>
</read_file>

Examples:

1. Reading a single file:
<read_file>
<args>
  <file>
    <path>src/app.ts</path>
    
  </file>
</args>
</read_file>

2. Reading multiple files (within the 5-file limit):
<read_file>
<args>
  <file>
    <path>src/app.ts</path>
    
  </file>
  <file>
    <path>src/utils.ts</path>
    
  </file>
</args>
</read_file>

3. Reading an entire file:
<read_file>
<args>
  <file>
    <path>config.json</path>
  </file>
</args>
</read_file>

IMPORTANT: You MUST use this Efficient Reading Strategy:
- You MUST read all related files and implementations together in a single operation (up to 5 files at once)
- You MUST obtain all necessary context before proceeding with changes

- When you need to read more than 5 files, prioritize the most critical files first, then use subsequent read_file requests for additional files
"""