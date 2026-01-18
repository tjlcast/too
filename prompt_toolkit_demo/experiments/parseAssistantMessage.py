from typing import Dict, List, Optional, Union, Any, Literal
from dataclasses import dataclass
from enum import Enum

# Type definitions
ToolName = str
ToolParamName = str

class ContentType(Enum):
    TEXT = "text"
    TOOL_USE = "tool_use"

@dataclass
class TextContent:
    type: str = ContentType.TEXT.value
    content: str = ""
    partial: bool = True

@dataclass
class ToolUse:
    type: str = ContentType.TOOL_USE.value
    name: ToolName = ""
    params: Dict[ToolParamName, str] = None
    partial: bool = True
    
    def __post_init__(self):
        if self.params is None:
            self.params = {}

AssistantMessageContent = Union[TextContent, ToolUse]

def parse_assistant_message(
    assistant_message: str,
    tool_names: List[ToolName],
    tool_param_names: List[ToolParamName]
) -> List[AssistantMessageContent]:
    """
    解析助手消息字符串，将其转换为结构化内容块列表。
    
    此函数与提供的 TypeScript 代码保持相同的逻辑：
    1. 使用累加器方法逐个字符处理
    2. 支持混合的文本和工具调用块
    3. 正确处理部分（未完成）内容
    4. 特殊处理 write_to_file 工具的 content 参数
    
    Args:
        assistant_message: 助手输出的原始字符串
        tool_names: 有效的工具名称列表
        tool_param_names: 有效的工具参数名称列表
        
    Returns:
        包含 TextContent 和 ToolUse 对象的列表
    """
    content_blocks: List[AssistantMessageContent] = []
    current_text_content: Optional[TextContent] = None
    current_text_content_start_index = 0
    current_tool_use: Optional[ToolUse] = None
    current_tool_use_start_index = 0
    current_param_name: Optional[ToolParamName] = None
    current_param_value_start_index = 0
    accumulator = ""

    # 预计算可能的标签以提高性能
    possible_tool_use_opening_tags = [f"<{name}>" for name in tool_names]
    possible_param_opening_tags = [f"<{name}>" for name in tool_param_names]
    
    content_param_name: ToolParamName = "content"
    
    i = 0
    length = len(assistant_message)
    
    while i < length:
        char = assistant_message[i]
        accumulator += char
        
        # 1. 如果当前正在解析参数值
        if current_tool_use and current_param_name:
            current_param_value = accumulator[current_param_value_start_index:]
            param_closing_tag = f"</{current_param_name}>"
            
            if current_param_value.endswith(param_closing_tag):
                # 参数值结束
                param_value = current_param_value[:-len(param_closing_tag)]
                
                # 特殊处理 content 参数：保留换行，但去除首尾换行符
                if current_param_name == content_param_name:
                    current_tool_use.params[current_param_name] = (
                        param_value[1:] if param_value.startswith('\n') else param_value
                    )
                    if current_tool_use.params[current_param_name].endswith('\n'):
                        current_tool_use.params[current_param_name] = current_tool_use.params[current_param_name][:-1]
                else:
                    current_tool_use.params[current_param_name] = param_value.strip()
                
                current_param_name = None
                i += 1
                continue
            else:
                # 继续累积参数值
                i += 1
                continue
        
        # 2. 如果当前正在解析工具（没有当前参数）
        if current_tool_use and not current_param_name:
            current_tool_value = accumulator[current_tool_use_start_index:]
            tool_use_closing_tag = f"</{current_tool_use.name}>"
            
            if current_tool_value.endswith(tool_use_closing_tag):
                # 工具调用结束
                current_tool_use.partial = False
                content_blocks.append(current_tool_use)
                current_tool_use = None
                i += 1
                continue
            else:
                # 检查是否开始新的参数
                started_new_param = False
                for param_opening_tag in possible_param_opening_tags:
                    if accumulator.endswith(param_opening_tag):
                        # 开始新的参数
                        current_param_name = param_opening_tag[1:-1]  # 移除 < 和 >
                        current_param_value_start_index = len(accumulator)
                        started_new_param = True
                        break
                
                if started_new_param:
                    i += 1
                    continue
                
                # 特殊处理 write_to_file 工具的 content 参数
                # 处理 content 参数中可能包含关闭标签的情况
                if (current_tool_use.name == "write_to_file" and 
                    accumulator.endswith(f"</{content_param_name}>")):
                    
                    tool_content = accumulator[current_tool_use_start_index:]
                    content_start_tag = f"<{content_param_name}>"
                    content_end_tag = f"</{content_param_name}>"
                    
                    content_start_index = tool_content.find(content_start_tag) + len(content_start_tag)
                    content_end_index = tool_content.rfind(content_end_tag)
                    
                    if (content_start_index != -1 and content_end_index != -1 and 
                        content_end_index > content_start_index):
                        
                        content_value = tool_content[content_start_index:content_end_index]
                        # 去除首尾换行符
                        if content_value.startswith('\n'):
                            content_value = content_value[1:]
                        if content_value.endswith('\n'):
                            content_value = content_value[:-1]
                        
                        current_tool_use.params[content_param_name] = content_value
                
                # 继续累积工具内容
                i += 1
                continue
        
        # 3. 如果没有当前工具调用
        if not current_tool_use:
            # 检查是否开始新的工具调用
            did_start_tool_use = False
            
            for tool_use_opening_tag in possible_tool_use_opening_tags:
                if accumulator.endswith(tool_use_opening_tag):
                    # 开始新的工具调用
                    current_tool_use = ToolUse(
                        name=tool_use_opening_tag[1:-1],  # 移除 < 和 >
                        params={},
                        partial=True
                    )
                    current_tool_use_start_index = len(accumulator)
                    
                    # 这也标志着当前文本内容的结束
                    if current_text_content:
                        current_text_content.partial = False
                        
                        # 从文本末尾移除部分累积的工具标签
                        current_text_content.content = (
                            current_text_content.content[:-len(tool_use_opening_tag[:-1])].strip()
                        )
                        
                        content_blocks.append(current_text_content)
                        current_text_content = None
                    
                    did_start_tool_use = True
                    break
            
            if not did_start_tool_use:
                # 没有工具调用，所以必须是文本（开始或工具之间）
                if current_text_content is None:
                    current_text_content_start_index = i
                
                current_text_content = TextContent(
                    content=accumulator[current_text_content_start_index:].strip(),
                    partial=True
                )
            
            i += 1
            continue
    
    # 处理流结束时未完成的内容
    if current_tool_use:
        # 流未完成工具调用，将其添加为部分内容
        if current_param_name:
            # 工具调用有未完成的参数
            param_value = accumulator[current_param_value_start_index:]
            
            # 特殊处理 content 参数
            if current_param_name == content_param_name:
                current_tool_use.params[current_param_name] = (
                    param_value[1:] if param_value.startswith('\n') else param_value
                )
                if current_tool_use.params[current_param_name].endswith('\n'):
                    current_tool_use.params[current_param_name] = current_tool_use.params[current_param_name][:-1]
            else:
                current_tool_use.params[current_param_name] = param_value.strip()
        
        content_blocks.append(current_tool_use)
    
    if current_text_content:
        # 流未完成文本内容，将其添加为部分内容
        current_text_content.content = accumulator[current_text_content_start_index:].strip()
        content_blocks.append(current_text_content)
    
    return content_blocks


def parse_assistant_message_simplified(
    assistant_message: str,
    tool_names: List[str] = None,
    tool_param_names: List[str] = None
) -> List[AssistantMessageContent]:
    """
    简化版本，带有默认的工具和参数名称。
    
    Args:
        assistant_message: 助手输出的原始字符串
        tool_names: 有效的工具名称列表（默认为常见工具）
        tool_param_names: 有效的工具参数名称列表（默认为常见参数）
        
    Returns:
        包含 TextContent 和 ToolUse 对象的列表
    """
    if tool_names is None:
        tool_names = ["write_to_file", "new_rule", "read_file", "search_code"]
    
    if tool_param_names is None:
        tool_param_names = ["content", "path", "rule_name", "search_query", "file_path"]
    
    return parse_assistant_message(assistant_message, tool_names, tool_param_names)


# 测试函数
def test_parse_assistant_message():
    """测试解析函数"""
    
    # 测试1: 纯文本
    print("Test 1: Pure text")
    result = parse_assistant_message_simplified("Hello, world!")
    print(f"Result: {result}")
    print()
    
    # 测试2: 工具调用
    print("Test 2: Tool use")
    message = """Some text before.
<write_to_file>
<path>/tmp/test.txt</path>
<content>Hello from the file!</content>
</write_to_file>
Some text after."""
    
    result = parse_assistant_message_simplified(message)
    for block in result:
        print(f"Block: {block}")
    print()
    
    # 测试3: 部分内容
    print("Test 3: Partial content")
    message = "Some text <write_to_file><path>/tmp/test.txt"
    result = parse_assistant_message_simplified(message)
    for block in result:
        print(f"Block: {block}")
    print()
    
    # 测试4: write_to_file 特殊处理
    print("Test 4: write_to_file special handling")
    message = """<write_to_file>
<path>/tmp/test.txt</path>
<content>Line 1
Line 2
Line 3</content>
</write_to_file>"""
    
    result = parse_assistant_message_simplified(message)
    for block in result:
        print(f"Block: {block}")
        if hasattr(block, 'params'):
            print(f"  Params: {block.params}")

if __name__ == "__main__":
    test_parse_assistant_message()