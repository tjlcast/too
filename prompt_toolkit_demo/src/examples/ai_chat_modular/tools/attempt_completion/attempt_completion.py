import json
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class AttemptCompletionArgs:
    """Arguments for the attempt completion tool."""
    result: str


def attempt_completion(args: Dict[str, Any], basePath: str = None) -> AttemptCompletionArgs:
    """
    Process the attempt_completion tool call to present final results.

    Args:
        args: Arguments containing the result
        basePath: Base path (unused for this tool)

    Returns:
        Dictionary with the result
    """
    if "error" in args:
        return args

    # Extract result from args
    result = args.get("args", {}).get("result", "")
    
    if not result:
        return {"error": "No result specified"}

    # Create and return AttemptCompletionArgs object
    attempt_args = AttemptCompletionArgs(result=result)
    return attempt_args


# For testing purposes
if __name__ == "__main__":
    # Test the function
    test_args = {
        "args": {
            "result": "Task completed successfully"
        }
    }
    result = attempt_completion(test_args)
    print(result)