from typing import Dict, Any

from prompt_toolkit_demo.src.examples.ai_agent.tools.read_file.read_file import read_file


def run(xml_string: str, basePath: str = None) -> Dict[str, Any]:
    return read_file(xml_string, basePath)


# For testing purposes
if __name__ == "__main__":
    from pathlib import Path
    current_working_directory = Path.cwd()

    xml_example = """
    <read_file>
    <args>
      <file>
        <path>prompt_toolkit_demo/src/example/ai_agent/tools/read_file/read_file.py</path>
      </file>
      <file>
        <path>prompt_toolkit_demo/src/main.py</path>
      </file>
    </args>
    </read_file>
    """
    print(run(xml_example, current_working_directory))
