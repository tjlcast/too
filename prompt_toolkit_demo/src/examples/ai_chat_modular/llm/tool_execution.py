
from typing import Any, Dict


def try_execute_command(result: Dict[str, Any]) -> None:
    """Try to execute the command if present in the result"""
    tools_situations = result.get('tools_situations', [])
    for tool in tools_situations:
        execution_result = tool["execution_result"]
        execution_name = execution_result.get('__name')
        if execution_name:
            callback = execution_result.get('__callback')
            if callable(callback):
                print(
                    f"\n>>>>>>>>>>>>>>>>>>>>>>\n[Executing {execution_name} command...]\n")
                res = callback()
                print(f"{res}")
                print("\n<<<<<<<<<<<<<<<<<<<<<<<\n")
