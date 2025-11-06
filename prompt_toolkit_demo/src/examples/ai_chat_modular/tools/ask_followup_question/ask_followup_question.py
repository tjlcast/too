import json
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Suggestion:
    """Represents a suggestion for follow-up question."""
    text: str
    mode: Optional[str] = None


@dataclass
class AskFollowupQuestionArgs:
    """Arguments for the ask followup question tool."""
    question: str
    follow_up: List[Suggestion]
    error: Optional[str] = None

    def __str__(self):
        # 将对象转换为字符串表示形式，方便输出
        result = {
            "question": self.question,
            "follow_up": []
        }

        # 只有在没有错误的情况下才添加 follow_up 信息
        if not self.error:
            for suggestion in self.follow_up:
                if isinstance(suggestion, Suggestion):
                    if suggestion.mode:
                        result["follow_up"].append({
                            "text": suggestion.text,
                            "mode": suggestion.mode
                        })
                    else:
                        result["follow_up"].append(suggestion.text)
                else:
                    result["follow_up"].append(suggestion)
        else:
            # 如果有错误，添加错误信息
            result["error"] = self.error

        return json.dumps(result, indent=2, ensure_ascii=False)


def ask_followup_question(args: Dict[str, Any], basePath: str = None) -> AskFollowupQuestionArgs:
    """
    Process the ask_followup_question tool call to ask user for additional information.

    Args:
        args: Arguments containing the question and follow-up suggestions
        basePath: Base path (unused for this tool)

    Returns:
        AskFollowupQuestionArgs object with the question and suggestions
    """
    if "error" in args:
        return args

    # Extract question and follow_up from args
    question = args.get("args", {}).get("question", "")
    follow_up = args.get("args", {}).get("follow_up", [])

    if not question:
        return {"error": "No question specified"}

    if not follow_up:
        return {"error": "No follow-up suggestions provided"}

    # Create suggestions list
    suggestions = []
    for suggestion in follow_up:
        if isinstance(suggestion, dict):
            suggestions.append(Suggestion(
                text=suggestion.get("text", ""),
                mode=suggestion.get("mode")
            ))
        else:
            suggestions.append(Suggestion(text=suggestion))

    # Create and return AskFollowupQuestionArgs object
    ask_args = AskFollowupQuestionArgs(
        question=question,
        follow_up=suggestions
    )
    return ask_args
