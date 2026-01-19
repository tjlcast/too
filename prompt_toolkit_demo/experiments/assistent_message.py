from typing import Any, Dict, Union
from dataclasses import dataclass
from enum import Enum


# Define types that would come from the TypeScript imports
# In practice, you would import these from your actual types module
ToolName = str
ToolParamName = str

# These would normally be imported, but we'll define them here for completeness
# toolNames = ["write_to_file", "new_rule", ...]  # from "@roo-code/types"
# toolParamNames = ["content", "path", "rule_name", ...]  # from "../../shared/tools"


class ContentBlockType(Enum):
    TEXT = "text"
    TOOL_USE = "tool_use"


class TextContent:
    def __init__(self, content: str = "", partial: bool = True):
        self.type = ContentBlockType.TEXT.value
        self.content = content
        self.partial = partial

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "content": self.content,
            "partial": self.partial
        }


class ToolUse:
    def __init__(self, name: ToolName, partial: bool = True, params: Dict[ToolParamName, str] = {}):
        self.type = ContentBlockType.TOOL_USE.value
        self.name = name
        self.params: Dict[ToolParamName, str] = {}
        self.partial = partial

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "name": self.name,
            "params": self.params,
            "partial": self.partial
        }


AssistantMessageContent = Union[TextContent, ToolUse]
