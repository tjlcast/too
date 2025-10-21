import json
from typing import Dict, Any

from prompt_toolkit_demo.src.examples.ai_agent.tools.list_files.list_files import list_files


def run(xml_string: str, basePath: str = None) -> Dict[str, Any]:
    return list_files(xml_string, basePath)


# For testing purposes
if __name__ == "__main__":
    from pathlib import Path
    current_working_directory = Path.cwd()

    xml_example = """
    <list_files>
    <args>
      <path>.</path>
      <recursive>false</recursive>
    </args>
    </list_files>
    """
    result = run(xml_example, current_working_directory)
    print(json.dumps(result, indent=4))

    xml_example = """
    <list_files>
    <args>
      <path>prompt_toolkit_demo/src/examples/ai_agent/tools</path>
      <recursive>true</recursive>
    </args>
    </list_files>
    """
    result = run(xml_example, current_working_directory)
    print(json.dumps(result, indent=4))
