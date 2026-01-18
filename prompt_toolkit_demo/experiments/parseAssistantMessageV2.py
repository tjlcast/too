from typing import Dict, List, Optional, Union, Literal, Any
from enum import Enum
import re

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
    def __init__(self, name: ToolName, partial: bool = True):
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


def parse_assistant_message_v2(
    assistant_message: str, 
    tool_names: List[ToolName], 
    tool_param_names: List[ToolParamName]
) -> List[AssistantMessageContent]:
    """
    Parses an assistant message string potentially containing mixed text and tool
    usage blocks marked with XML-like tags into an array of structured content
    objects.
    
    This Python version follows the same logic as the TypeScript V2 implementation.
    
    Args:
        assistant_message: The raw string output from the assistant.
        tool_names: List of valid tool names.
        tool_param_names: List of valid tool parameter names.
        
    Returns:
        A list of AssistantMessageContent objects, which can be TextContent or ToolUse.
        Blocks that were not fully closed by the end of the input string will have
        their partial flag set to True.
    """
    content_blocks: List[AssistantMessageContent] = []
    
    current_text_content_start = 0  # Index where the current text block started.
    current_text_content: Optional[TextContent] = None
    current_tool_use_start = 0  # Index *after* the opening tag of the current tool use.
    current_tool_use: Optional[ToolUse] = None
    current_param_value_start = 0  # Index *after* the opening tag of the current param.
    current_param_name: Optional[ToolParamName] = None
    
    # Precompute tags for faster lookups.
    tool_use_open_tags = {f"<{name}>": name for name in tool_names}
    tool_param_open_tags = {f"<{name}>": name for name in tool_param_names}
    
    length = len(assistant_message)
    i = 0
    
    while i < length:
        current_char_index = i
        
        # Parsing a tool parameter
        if current_tool_use and current_param_name:
            close_tag = f"</{current_param_name}>"
            close_tag_len = len(close_tag)
            
            # Check if the string *ending* at index i matches the closing tag
            if (current_char_index >= close_tag_len - 1 and
                assistant_message[current_char_index - close_tag_len + 1:current_char_index + 1] == close_tag):
                
                # Found the closing tag for the parameter.
                value = assistant_message[
                    current_param_value_start:  # Start after the opening tag.
                    current_char_index - close_tag_len + 1  # End before the closing tag.
                ]
                
                # Don't trim content parameters to preserve newlines, but strip first and last newline only
                if current_param_name == "content":
                    current_tool_use.params[current_param_name] = (
                        value[1:] if value.startswith('\n') else value
                    )
                    if current_tool_use.params[current_param_name].endswith('\n'):
                        current_tool_use.params[current_param_name] = current_tool_use.params[current_param_name][:-1]
                else:
                    current_tool_use.params[current_param_name] = value.strip()
                
                current_param_name = None  # Go back to parsing tool content.
                # Don't continue loop here, need to check for tool close or other params at index i.
            else:
                i += 1
                continue  # Still inside param value, move to next char.
        
        # Parsing a tool use (but not a specific parameter).
        if current_tool_use and not current_param_name:
            # Ensure we are not inside a parameter already.
            # Check if starting a new parameter.
            started_new_param = False
            
            for tag, param_name in tool_param_open_tags.items():
                tag_len = len(tag)
                if (current_char_index >= tag_len - 1 and
                    assistant_message[current_char_index - tag_len + 1:current_char_index + 1] == tag):
                    
                    current_param_name = param_name
                    current_param_value_start = current_char_index + 1  # Value starts after the tag.
                    started_new_param = True
                    break
            
            if started_new_param:
                i += 1
                continue  # Handled start of param, move to next char.
            
            # Check if closing the current tool use.
            tool_close_tag = f"</{current_tool_use.name}>"
            tool_close_tag_len = len(tool_close_tag)
            
            if (current_char_index >= tool_close_tag_len - 1 and
                assistant_message[current_char_index - tool_close_tag_len + 1:current_char_index + 1] == tool_close_tag):
                
                # End of the tool use found.
                # Special handling for content params *before* finalizing the tool.
                tool_content_slice = assistant_message[
                    current_tool_use_start:  # From after the tool opening tag.
                    current_char_index - tool_close_tag_len + 1  # To before the tool closing tag.
                ]
                
                # Check if content parameter needs special handling (write_to_file/new_rule).
                # This check is important if the closing </content> tag was missed by the 
                # parameter parsing logic (e.g., if content is empty or parsing logic 
                # prioritizes tool close).
                content_param_name = "content"
                if (current_tool_use.name == "write_to_file" and  # or current_tool_use.name == "new_rule"
                    f"<{content_param_name}>" in tool_content_slice):  # Check if tag exists.
                    
                    content_start_tag = f"<{content_param_name}>"
                    content_end_tag = f"</{content_param_name}>"
                    content_start = tool_content_slice.find(content_start_tag)
                    
                    # Use `rfind` for robustness against nested tags.
                    content_end = tool_content_slice.rfind(content_end_tag)
                    
                    if content_start != -1 and content_end != -1 and content_end > content_start:
                        # Don't trim content to preserve newlines, but strip first and last newline only
                        content_value = tool_content_slice[
                            content_start + len(content_start_tag):content_end
                        ]
                        if content_value.startswith('\n'):
                            content_value = content_value[1:]
                        if content_value.endswith('\n'):
                            content_value = content_value[:-1]
                        current_tool_use.params[content_param_name] = content_value
                
                current_tool_use.partial = False  # Mark as complete.
                content_blocks.append(current_tool_use)
                current_tool_use = None  # Reset state.
                current_text_content_start = current_char_index + 1  # Potential text starts after this tag.
                i += 1
                continue  # Move to next char.
            
            # If not starting a param and not closing the tool, continue
            # accumulating tool content implicitly.
            i += 1
            continue
        
        # Parsing text / looking for tool start.
        if not current_tool_use:
            # Check if starting a new tool use.
            started_new_tool = False
            
            for tag, tool_name in tool_use_open_tags.items():
                tag_len = len(tag)
                if (current_char_index >= tag_len - 1 and
                    assistant_message[current_char_index - tag_len + 1:current_char_index + 1] == tag):
                    
                    # End current text block if one was active.
                    if current_text_content:
                        current_text_content.content = assistant_message[
                            current_text_content_start:  # From where text started.
                            current_char_index - tag_len + 1  # To before the tool tag starts.
                        ].strip()
                        
                        current_text_content.partial = False  # Ended because tool started.
                        
                        if len(current_text_content.content) > 0:
                            content_blocks.append(current_text_content)
                        
                        current_text_content = None
                    else:
                        # Check for any text between the last block and this tag.
                        potential_text = assistant_message[
                            current_text_content_start:  # From where text *might* have started.
                            current_char_index - tag_len + 1  # To before the tool tag starts.
                        ].strip()
                        
                        if potential_text:
                            content_blocks.append(TextContent(potential_text, False))
                    
                    # Start the new tool use.
                    current_tool_use = ToolUse(tool_name, True)
                    current_tool_use_start = current_char_index + 1  # Tool content starts after the opening tag.
                    started_new_tool = True
                    break
            
            if started_new_tool:
                i += 1
                continue  # Handled start of tool, move to next char.
            
            # If not starting a tool, it must be text content.
            if not current_text_content:
                # Start a new text block if we aren't already in one.
                current_text_content_start = current_char_index  # Text starts at the current character.
                current_text_content = TextContent("", True)
            
            # Continue accumulating text implicitly; content is extracted later.
            i += 1
            continue
        
        i += 1
    
    # Finalize any open parameter within an open tool use.
    if current_tool_use and current_param_name:
        value = assistant_message[current_param_value_start:]  # From param start to end of string.
        # Don't trim content parameters to preserve newlines, but strip first and last newline only
        if current_param_name == "content":
            if value.startswith('\n'):
                value = value[1:]
            if value.endswith('\n'):
                value = value[:-1]
            current_tool_use.params[current_param_name] = value
        else:
            current_tool_use.params[current_param_name] = value.strip()
        # Tool use remains partial.
    
    # Finalize any open tool use (which might contain the finalized partial param).
    if current_tool_use:
        # Tool use is partial because the loop finished before its closing tag.
        content_blocks.append(current_tool_use)
    
    # Finalize any trailing text content.
    # Only possible if a tool use wasn't open at the very end.
    elif current_text_content:
        current_text_content.content = assistant_message[current_text_content_start:].strip()
        # Text is partial because the loop finished.
        if current_text_content.content:
            content_blocks.append(current_text_content)
    
    return content_blocks


# Simplified version with predefined tool and parameter names
def parse_assistant_message(
    assistant_message: str,
    tool_names: List[str] = None,
    tool_param_names: List[str] = None
) -> List[AssistantMessageContent]:
    """
    Simplified version with default tool and parameter names.
    
    Args:
        assistant_message: The raw string output from the assistant.
        tool_names: List of valid tool names (defaults to common ones).
        tool_param_names: List of valid tool parameter names (defaults to common ones).
        
    Returns:
        A list of AssistantMessageContent objects.
    """
    if tool_names is None:
        tool_names = ["write_to_file", "new_rule", "read_file", "search_code"]
    
    if tool_param_names is None:
        tool_param_names = ["content", "path", "rule_name", "search_query", "file_path"]
    
    return parse_assistant_message_v2(assistant_message, tool_names, tool_param_names)