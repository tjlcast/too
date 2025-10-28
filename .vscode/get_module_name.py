# .vscode/get_module_name.py
import os
import sys

def main():
    if len(sys.argv) < 3:
        print("Usage: python get_module_name.py <file_path> <workspace>")
        sys.exit(1)

    file_path = os.path.abspath(sys.argv[1])
    workspace = os.path.abspath(sys.argv[2])

    if not os.path.exists(file_path):
        print("Error: file not found")
        sys.exit(1)
    if not file_path.startswith(workspace):
        print("Error: file not inside workspace")
        sys.exit(1)

    rel = os.path.relpath(file_path, workspace)
    if rel.endswith(".py"):
        rel = rel[:-3]

    module_name = rel.replace(os.sep, ".")
    out_path = os.path.join(workspace, ".vscode", ".last_module_name")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(module_name)

    print(f"[module] {module_name}")

if __name__ == "__main__":
    main()
