desc = """
## execute_command
Description: Request to execute a CLI command on the system. Use this when you need to perform system operations or run specific commands to accomplish any step in the user's task. You must tailor your command to the user's system and provide a clear explanation of what the command does. For command chaining, use the appropriate chaining syntax for the user's shell. Prefer to execute complex CLI commands over creating executable scripts, as they are more flexible and easier to run. Prefer relative commands and paths that avoid location sensitivity for terminal consistency, e.g: `touch ./testdata/example.file`, `dir ./examples/model1/data/yaml`, or `go test ./cmd/front --config ./cmd/front/config.yml`. If directed by the user, you may open a terminal in a different directory by using the `cwd` parameter.

Parameters:
- args: Contains the command to execute and optional working directory
  - command: (required) The CLI command to execute. This should be valid for the current operating system. Ensure the command is properly formatted and does not contain any harmful instructions.
  - cwd: (optional) The working directory to execute the command in (default: current directory)

Usage:
<execute_command>
<args>
  <command>Your command here</command>
  <cwd>Working directory path (optional)</cwd>
</args>
</execute_command>

Examples:

1. Executing a simple command:
<execute_command>
<args>
  <command>ls -la</command>
</args>
</execute_command>

2. Executing a command in a specific directory:
<execute_command>
<args>
  <command>npm run dev</command>
  <cwd>/home/user/projects</cwd>
</args>
</execute_command>

3. Executing a command with pipes:
<execute_command>
<args>
  <command>ps aux | grep python</command>
</args>
</execute_command>
"""