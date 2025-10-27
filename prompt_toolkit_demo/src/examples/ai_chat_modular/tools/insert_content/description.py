desc = """
## insert_content
Description: Use this tool specifically for adding new lines of content into a file without modifying existing content. Specify the line number to insert before, or use line 0 to append to the end. Ideal for adding imports, functions, configuration blocks, log entries, or any multi-line text block.

Parameters:
- args: Contains one or more insertion elements, where each insertion contains:
  - path: (required) File path relative to workspace directory c:/Users/phx10/code/cg-manager
  - line: (required) Line number where content will be inserted (1-based)
          Use 0 to append at end of file
          Use any positive number to insert before that line
  - content: (required) The content to insert at the specified line

Usage:
<insert_content>
<args>
  <insertion>
    <path>path/to/file</path>
    <line>line_number</line>
    <content>content to insert</content>
  </insertion>
</args>
</insert_content>

Examples:

1. Inserting imports at start of file:
<insert_content>
<args>
  <insertion>
    <path>src/utils.ts</path>
    <line>1</line>
    <content>
// Add imports at start of file
import { sum } from './math';
</content>
  </insertion>
</args>
</insert_content>

2. Appending to the end of file:
<insert_content>
<args>
  <insertion>
    <path>src/utils.ts</path>
    <line>0</line>
    <content>
// This is the end of the file
</content>
  </insertion>
</args>
</insert_content>

3. Multiple insertions (within the 5-insertion limit):
<insert_content>
<args>
  <insertion>
    <path>src/app.ts</path>
    <line>1</line>
    <content>import { helper } from './helper';</content>
  </insertion>
  <insertion>
    <path>src/app.ts</path>
    <line>10</line>
    <content>console.log('Application started');</content>
  </insertion>
</args>
</insert_content>

**IMPORTANT NOTES:**
- Line numbers are 1-based (first line is line 1)
- Use line 0 to append content at the end of the file
- You can insert a maximum of 5 insertions in a single request
- Content will be inserted before the specified line number
- Existing content in the file will not be modified, only new content will be added
"""