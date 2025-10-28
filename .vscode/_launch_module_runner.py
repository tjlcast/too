# .vscode/_launch_module_runner.py
import runpy
import os
import sys

workspace = os.path.abspath(os.getenv("WORKSPACE_FOLDER", "."))
last_module_file = os.path.join(workspace, ".vscode", ".last_module_name")

if not os.path.exists(last_module_file):
    print("Error: .last_module_name not found. Please run Compute Python Module Name task first.")
    sys.exit(1)

with open(last_module_file, "r", encoding="utf-8") as f:
    module_name = f.read().strip()

print(f"Launching module: {module_name}")
sys.stdout.flush()

runpy.run_module(module_name, run_name="__main__")
