
from datetime import datetime
from typing import Any, Dict, List, TYPE_CHECKING, Tuple

from ..environment.user_message_environment_detail import get_environment_details
from ..environment.environment_proxy import EnvironmentProxy

from ..utils.tpl_util import replace_template_vars
from ..utils.time_util import get_current_timestamp

import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List

from ..tools.execute_command.run import run as run_execute_command
from ..tools.insert_content.run import run as run_insert_content
from ..tools.list_files.run import run as run_list_files
from ..tools.read_file.run import run as run_read_file
from ..tools.search_and_replace.run import run as run_search_and_replace
from ..tools.search_files.run import run as run_search_files
from ..tools.write_to_file.run import run as run_write_to_file


if TYPE_CHECKING:
    from ..views import ViewInterface


def _get_potential_closing_tag_prefixes(tag_name: str) -> List[str]:
    """
    获取可能的结束标签前缀列表

    Args:
        tag_name: 标签名，如 "result"

    Returns:
        所有可能的结束标签前缀列表
    """
    closing_tag = f"</{tag_name}>"
    prefixes = []
    for i in range(1, len(closing_tag)):
        prefixes.append(closing_tag[:i])
    return prefixes


def _should_display_content(buffer: str, content_start: int, content_end: int, chunk: str) -> bool:
    """
    判断是否应该显示内容

    Args:
        buffer: 当前缓冲区
        content_start: 内容开始位置
        content_end: 内容结束位置
        chunk: 当前块

    Returns:
        是否应该显示内容
    """
    # 检查chunk是否以任何结束标签前缀结尾
    result_prefixes = _get_potential_closing_tag_prefixes("result")

    # 检查buffer是否以结束标签前缀结尾
    for prefix in result_prefixes:
        if buffer.endswith(prefix):
            return False

    # 检查buffer末尾是否以结束标签前缀结尾
    buffer_suffix = buffer[len(buffer) - len(chunk)
                               :] if len(buffer) >= len(chunk) else buffer
    for prefix in result_prefixes:
        if buffer_suffix.endswith(prefix) and not buffer.endswith(f"</{prefix[2:]}" if prefix.startswith("</") else f"</{prefix}"):
            # 只有在buffer确实不包含完整结束标签时才限制输出
            if not buffer.endswith(f"</result>"):
                return False

    return True


class LLMProxy:
    def __init__(self, view_interface: 'ViewInterface', llm_provider: 'LLMProvider'):
        """
        Initialize the tool task handler.

        Args:
            view_interface: The view interface for displaying information
            llm_provider: The LLM provider for interacting with AI models
        """
        self.view = view_interface
        self.llm = llm_provider
        self.tools = {}  # Dictionary to hold available tools

    def process_tools_input(self, tool_results: List[Dict], conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Process tool execution results and combine them with environment information.

        Args:
            tool_results: List of tool execution results
            conversation_history: The conversation history

        Returns:
            Dictionary with processing results
        """
        # Extract tool execution results
        tool_execution_results = []
        for tool in tool_results:
            if "__execution_result" in tool:
                tool_execution_results.append({
                    "name": tool.get("__name", "unknown"),
                    "result": tool["__execution_result"]
                })

        # Get environment details
        env_proxy = EnvironmentProxy()
        environment_details = get_environment_details(env_proxy)

        # Create tool results message
        tool_results_content = "<tool_execution_results>\n"
        for result in tool_execution_results:
            tool_results_content += f"<tool name='{result['name']}'>\n{result['result']}\n</tool>\n"
        tool_results_content += "</tool_execution_results>"

        # Combine tool results with environment information
        combined_content = f"{tool_results_content}\n{environment_details}"

        # Add to conversation history
        result = {
            'conversation_history': conversation_history.copy()
        }

        result['conversation_history'].append({
            "role": "user",
            "content": combined_content,
            "timestamp": get_current_timestamp()
        })

        return result

    def process_user_input(self, user_input: str, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Process user input and determine if tools are needed.

        Args:
            user_input: The user's input message
            conversation_history: The conversation history

        Returns:
            Dictionary with processing results
        """
        # For now, we'll just add the user input to the conversation history
        # In a more complex implementation, this would analyze the input
        # to determine if tools are needed

        result = {
            'requires_tool': False,
            'tool_name': None,
            'tool_args': None,
            'user_message': user_input,
            'conversation_history': conversation_history.copy()
        }

        # Build user task entry
        env_proxy = EnvironmentProxy()
        details = get_environment_details(env_proxy)
        user_message_tpl = """<task>{{user_task}}</task>\n{{env_details}}
        """
        user_input = replace_template_vars(
            user_message_tpl, {"{{user_task}}": user_input, "{{env_details}}": details})

        # Add user message to conversation history
        result['conversation_history'].append({
            "role": "user",
            "content": user_input,
            "timestamp": get_current_timestamp()
        })

        return result

    def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task, potentially using tools.

        Args:
            task_data: Data about the task to execute

        Returns:
            Dictionary with execution results
        """
        # For now, we'll just get a response from the LLM
        # In a more complex implementation, this would check if tools are needed
        # and execute them before or after getting an LLM response

        response_stream = self.llm.get_response_stream(
            task_data['conversation_history'])

        result = {
            'response_stream': response_stream,
            'conversation_history': task_data['conversation_history']
        }

        return result

    def process_response(self, response_stream, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Process the AI response stream and handle tool calls in real-time.

        This version is robust to arbitrary chunk boundaries: it accumulates incoming
        chunks into a buffer and processes the buffer to safely extract:
          - plain text that can be displayed
          - complete tool XML blocks for parsing/execution
        Partial tags (e.g. "<to", "<execu") are never output until they are confirmed
        to be non-tool text or completed into a full tag + matching closing tag.
        """
        tools_situations = []
        full_response = ""
        self.view.display_ai_header()

        # buffer holds data not yet safely displayed/consumed
        buffer = ""
        tool_tags = [
            'execute_command', 'insert_content', 'list_files', 'read_file',
            'search_and_replace', 'search_files', 'write_to_file', 'attempt_completion'
        ]
        max_tool_tag_len = max(len(t) for t in tool_tags)

        # helper: process current buffer and extract displayable texts and tool blocks
        def _drain_buffer(buf: str):
            """
            Process buffer and yield tuples:
              ("text", text_to_display)
              ("tool", full_tool_xml)
            Returns (remaining_buffer, list_of_outputs)
            """
            outputs = []
            pos = 0
            while True:
                # find earliest full start-tag for any tool
                earliest = None
                earliest_tag = None
                for tag in tool_tags:
                    m = re.search(rf"<{tag}\b", buf[pos:])
                    if m:
                        found_at = pos + m.start()
                        if earliest is None or found_at < earliest:
                            earliest = found_at
                            earliest_tag = tag

                if earliest is None:
                    # No full start tag found.
                    # We can safely display most of buffer, but must keep possible partial prefix
                    # that could be the beginning of a tag, e.g. "<", "<to", "<exec".
                    # Strategy:
                    #   - find last '<' in buf
                    #   - if substring after last '<' is a prefix of any tool tag, withhold it.
                    #   - otherwise, display all.
                    last_lt = buf.rfind('<')
                    if last_lt == -1:
                        # no '<' at all: safe to display all
                        outputs.append(("text", buf))
                        buf = ""
                    else:
                        suffix = buf[last_lt+1:]  # after '<'
                        # if suffix might be prefix of any tool tag, withhold from display
                        may_be_tool_prefix = False
                        for tag in tool_tags:
                            if tag.startswith(suffix):
                                may_be_tool_prefix = True
                                break
                        if may_be_tool_prefix:
                            # display until last_lt, keep the rest
                            if last_lt > 0:
                                outputs.append(("text", buf[:last_lt]))
                                buf = buf[last_lt:]
                            # else last_lt == 0 -> keep whole buffer
                        else:
                            # '<' exists but definitely not start of our tool tags: safe to display all
                            outputs.append(("text", buf))
                            buf = ""
                    break  # drained as much as possible for now

                # earliest is start position of a tool start-tag
                start_pos = earliest
                tag = earliest_tag
                # display everything before start_pos as plain text (if any)
                if start_pos > 0:
                    outputs.append(("text", buf[:start_pos]))
                # Now we need to find matching end tag considering nesting for the same tag
                open_tag = f"<{tag}"
                close_tag = f"</{tag}>"

                # We'll scan from start_pos forward counting occurrences of open_tag (only full open like "<tag" with word boundary)
                scan_pos = start_pos
                depth = 0
                found_complete = False
                while True:
                    # find next open or close tag occurrence
                    next_open = re.search(rf"<{tag}\b", buf[scan_pos:])
                    next_close = buf.find(close_tag, scan_pos)
                    # normalize positions relative to buf
                    next_open_pos = (scan_pos + next_open.start()
                                     ) if next_open else None
                    next_close_pos = next_close if next_close != -1 else None

                    # If there's an open before close, increase depth and continue
                    if next_open_pos is not None and (next_close_pos is None or next_open_pos < next_close_pos):
                        depth += 1
                        scan_pos = next_open_pos + len(open_tag)
                        # continue scanning
                    elif next_close_pos is not None:
                        # found a close tag
                        depth -= 1
                        scan_pos = next_close_pos + len(close_tag)
                        if depth == 0:
                            # complete block found from start_pos to scan_pos
                            end_pos = scan_pos
                            full_tool = buf[start_pos:end_pos]
                            outputs.append(("tool", full_tool))
                            # cut buffer after end_pos
                            buf = buf[end_pos:]
                            # restart outer while loop from beginning of new buffer
                            break
                        # else keep scanning
                    else:
                        # no close tag found yet — incomplete block; keep from start_pos onward in buffer
                        # keep whole tail and wait for more chunks
                        buf = buf[start_pos:]
                        found_complete = False
                        break

                # if we found a complete tool block, continue processing the new (shorter) buf
                if 'end_pos' in locals():
                    # cleanup for next iteration
                    del end_pos
                    continue
                else:
                    # incomplete block situation: stop draining
                    break

            return buf, outputs

        # Process stream
        for chunk in response_stream:
            buffer += chunk
            # drain buffer as much as possible
            buffer, outputs = _drain_buffer(buffer)

            # 检查是否有<attempt_completion>标签内容正在构建
            # 使用游标方式判断chunk是否在<attempt_completion><result>标签内容中
            if "<attempt_completion>" in buffer and "</result>" not in buffer:
                # 使用游标跟踪标签位置
                cursor = 0
                while cursor < len(buffer):
                    # 查找<attempt_completion>标签起始位置
                    attempt_start = buffer.find("<attempt_completion>", cursor)
                    if attempt_start == -1:
                        break

                    # 查找</attempt_completion>标签结束位置
                    attempt_end = buffer.find(
                        "</attempt_completion>", attempt_start)
                    if attempt_end == -1:
                        attempt_end = len(buffer)

                    # 查找<result>标签起始位置
                    result_start_tag = buffer.find("<result>", attempt_start)
                    if result_start_tag != -1 and result_start_tag < attempt_end:
                        # 计算result内容起始位置
                        result_content_start = result_start_tag + \
                            len("<result>")

                        # 查找</result>标签结束位置
                        result_end_tag = buffer.find(
                            "</result>", result_content_start)
                        if result_end_tag != -1 and result_end_tag < attempt_end:
                            # 确定result内容结束位置
                            result_content_end = result_end_tag
                        else:
                            # 如果没有找到结束标签，则内容一直到attempt_completion结束或缓冲区末尾
                            result_content_end = attempt_end

                        # 检查chunk是否在result内容范围内
                        chunk_start_pos = len(buffer) - len(chunk)

                        # 判断chunk是否在result内容区间内
                        if (chunk_start_pos >= result_content_start and
                                chunk_start_pos < result_content_end):
                            # 检查是否应该显示内容（避免显示标签片段）
                            if _should_display_content(buffer, result_content_start, result_content_end, chunk):
                                self.view.display_attempt_completion(chunk)
                        elif (result_content_start >= chunk_start_pos and
                              result_content_start < len(buffer)):
                            # 处理边界情况，chunk包含了result开始的一部分
                            overlap_start = max(
                                result_content_start, chunk_start_pos)
                            if overlap_start < len(buffer):
                                overlapping_part = buffer[overlap_start:len(
                                    buffer)]
                                if overlapping_part and chunk.endswith(overlapping_part):
                                    # 检查是否应该显示内容（避免显示标签片段）
                                    if _should_display_content(buffer, result_content_start, result_content_end, overlapping_part):
                                        self.view.display_attempt_completion(
                                            overlapping_part)

                    # 移动游标到下一个位置
                    cursor = attempt_end + len("</attempt_completion>") if buffer.find(
                        "</attempt_completion>", attempt_end) != -1 else len(buffer)

            # display yielded outputs in order
            for typ, val in outputs:
                if typ == "text":
                    if val:
                        self.view.display_ai_message_chunk(val)
                        full_response += val
                elif typ == "tool":
                    # try to parse & execute tool block
                    try:
                        full_response += val
                        execution_result = self._parse_and_execute_tool(val)

                        execution_params = val
                        # If execution_result is a dict with __callback, queue for approval
                        if isinstance(execution_result, dict) and "__callback" in execution_result:
                            self.view.pending_tools.append(execution_result)
                            tools_situations.append({
                                "execution_params": execution_params,
                                "execution_result": execution_result,
                            })
                        else:
                            # string result: show directly
                            tools_situations.append({
                                "execution_params": execution_params,
                                "execution_result": execution_result,
                            })
                            self.view.display_ai_message_chunk(
                                f"【工具执行结果】{execution_result}")
                    except Exception as e:
                        # parsing/execution failed — display the tool block as plain text (fail-open)
                        self.view.display_ai_message_chunk(val)
                        full_response += val

        # After stream ends, whatever remains in buffer is either safe text or partial things that never completed.
        # We'll attempt to safely display them following same rules.
        if buffer:
            # If buffer still contains a leftover that looks like a partial tool tag, we should avoid exposing raw tag fragments.
            # We'll reuse the same logic: if buffer begins with a possible tool tag prefix, try to see if it's actual xml parseable.
            trimmed = buffer
            # try parse as XML - if parses as known tool, treat as tool block (best-effort)
            try:
                parsed = ET.fromstring(trimmed)
                # if parsed tag is one of tool_tags and structure is fine, call parse/execution
                if parsed.tag in tool_tags:
                    execution_result = self._parse_and_execute_tool(trimmed)
                    if isinstance(execution_result, dict) and "__callback" in execution_result:
                        self.view.pending_tools.append(execution_result)
                        tools_situations.append({
                            "execution_params": trimmed,
                            "execution_result": execution_result,
                        })
                    else:
                        tools_situations.append({
                            "execution_params": trimmed,
                            "execution_result": execution_result,
                        })
                        self.view.display_ai_message_chunk(
                            f"【工具执行结果】{execution_result}")
                    full_response += trimmed
                else:
                    # not a recognized tool tag, display as text
                    self.view.display_ai_message_chunk(trimmed)
                    full_response += trimmed
            except ET.ParseError:
                # Could not parse: display but hide suspicious partial tag tails.
                # For maximum safety, if buffer contains a '<' that could be prefix of tool tag, strip it or escape it.
                safe_to_display = trimmed
                # find any '<' followed by a prefix of a tool tag—escape them

                def _escape_possible_tool_prefix(m):
                    inner = m.group(0)  # e.g. "<to"
                    return inner.replace("<", "&lt;")
                # Use regex to find '<' followed by letters and check if letters prefix any tool_tags
                safe_to_display = re.sub(
                    r"<([a-zA-Z]{1," + str(max_tool_tag_len) + r"})",
                    lambda m: ("&lt;" + m.group(1)) if any(t.startswith(m.group(1))
                                                           for t in tool_tags) else m.group(0),
                    safe_to_display
                )
                self.view.display_ai_message_chunk(safe_to_display)
                full_response += safe_to_display

        self.view.display_newline()

        # Add AI response to conversation history
        conversation_history.append({
            "role": "assistant",
            "content": full_response,
            "timestamp": get_current_timestamp()
        })

        result = {
            'response': full_response,
            'conversation_history': conversation_history,
            'tools_situations': tools_situations
        }

        return result

    def _parse_and_execute_tool(self, tool_xml: str) -> str:
        """
        解析并执行工具调用。

        Args:
            tool_xml: 工具调用的XML字符串

        Returns:
            执行结果字符串
        """
        try:
            root = ET.fromstring(tool_xml)
            tool_name = root.tag

            # 根据工具类型调用相应的处理函数
            if tool_name == 'execute_command':
                return self._execute_command_tool(root, tool_name, tool_xml)
            elif tool_name == 'insert_content':
                return self._execute_insert_content_tool(root, tool_name, tool_xml)
            elif tool_name == 'list_files':
                return self._execute_list_files_tool(root, tool_name, tool_xml)
            elif tool_name == 'read_file':
                return self._execute_read_file_tool(root, tool_name, tool_xml)
            elif tool_name == 'search_and_replace':
                return self._execute_search_replace_tool(root, tool_name, tool_xml)
            elif tool_name == 'search_files':
                return self._execute_search_files_tool(root, tool_name, tool_xml)
            elif tool_name == 'write_to_file':
                return self._execute_write_file_tool(root, tool_name, tool_xml)
            elif tool_name == 'attempt_completion':
                return self._execute_attempt_completion_tool(root, tool_name, tool_xml)
            else:
                return f"未知工具: {tool_name}"

        except ET.ParseError as e:
            return f"XML解析错误: {str(e)}"
        except Exception as e:
            return f"工具执行失败: {str(e)}"

    # 以下工具执行方法与之前相同，保持不变
    def _execute_command_tool(self, root: ET.Element, tool_name: str, tool_xml: str) -> Dict[str, Any]:
        """模拟执行命令工具"""
        command_elem = root.find('.//command')
        if command_elem is not None:
            command = command_elem.text or ""

            def __run_execute_command():
                return run_execute_command(tool_xml)

            return {
                "desc": f"执行命令: {command} [模拟执行完成]",
                "__name": tool_name,
                "__callback": __run_execute_command,
            }
        return "命令参数缺失"

    def _execute_insert_content_tool(self, root: ET.Element, tool_name: str, tool_xml: str) -> str:
        """模拟插入内容工具"""
        path_elem = root.find('.//path')
        line_elem = root.find('.//line')
        content_elem = root.find('.//content')

        if all(elem is not None for elem in [path_elem, line_elem, content_elem]):
            path = path_elem.text or ""
            line = line_elem.text or ""
            content = content_elem.text or ""

            def __run_insert_content():
                return run_insert_content(tool_xml)

            return {
                "desc": f"在文件 {path} 第 {line} 行插入内容 [模拟执行完成]",
                "__name": tool_name,
                "__callback": __run_insert_content,
            }
        return "插入内容参数缺失"

    def _execute_list_files_tool(self, root: ET.Element, tool_name: str, tool_xml: str) -> str:
        """模拟列出文件工具"""
        path_elem = root.find('.//path')
        recursive_elem = root.find('.//recursive')

        path = path_elem.text if path_elem is not None else "."
        recursive = recursive_elem.text if recursive_elem is not None else "false"

        def __run_execute_command():
            return run_list_files(tool_xml)

        return {
            "desc": f"列出目录 {path} 的文件 (递归: {recursive}) [模拟执行完成]",
            "__name": tool_name,
            "__callback": __run_execute_command,
        }

    def _execute_read_file_tool(self, root: ET.Element, tool_name: str, tool_xml: str) -> str:
        """模拟读取文件工具"""
        path_elem = root.find('.//path')
        if path_elem is not None:
            path = path_elem.text or ""

            def __run_read_file():
                return run_read_file(tool_xml)

            return {
                "desc": f"读取文件 {path} 的内容 [模拟执行完成]",
                "__name": tool_name,
                "__callback": __run_read_file,
            }
        return "文件路径参数缺失"

    def _execute_search_replace_tool(self, root: ET.Element, tool_name: str, tool_xml: str) -> str:
        """模拟搜索替换工具"""
        path_elem = root.find('.//path')
        search_elem = root.find('.//search')
        replace_elem = root.find('.//replace')

        if all(elem is not None for elem in [path_elem, search_elem, replace_elem]):
            path = path_elem.text or ""
            search = search_elem.text or ""
            replace = replace_elem.text or ""

            def __run_search_and_replace():
                return run_search_and_replace(tool_xml)

            return {
                "desc": f"在文件 {path} 中搜索 '{search}' 替换为 '{replace}' [模拟执行完成]",
                "__name": tool_name,
                "__callback": __run_search_and_replace,
            }
        return "搜索替换参数缺失"

    def _execute_search_files_tool(self, root: ET.Element, tool_name: str, tool_xml: str) -> str:
        """模拟搜索文件工具"""
        path_elem = root.find('.//path')
        regex_elem = root.find('.//regex')
        file_pattern_elem = root.find('.//file_pattern')

        path = path_elem.text if path_elem is not None else "."
        regex = regex_elem.text if regex_elem is not None else "."
        file_pattern = file_pattern_elem.text if file_pattern_elem is not None else "*"

        def __run_search_files():
            return run_search_files(tool_xml)

        return {
            "desc": f"在目录 {path} 中搜索文件模式 {file_pattern}，正则表达式 {regex} [模拟执行完成]",
            "__name": tool_name,
            "__callback": __run_search_files,
        }

    def _execute_write_file_tool(self, root: ET.Element, tool_name: str, tool_xml: str) -> str:
        """模拟写入文件工具"""
        path_elem = root.find('.//path')
        content_elem = root.find('.//content')
        line_count_elem = root.find('.//line_count')

        if path_elem is not None and content_elem is not None:
            path = path_elem.text or ""
            content = content_elem.text or ""
            line_count = line_count_elem.text if line_count_elem is not None else "未知"

            def __run_write_to_file():
                return run_write_to_file(tool_xml)

            return {
                "desc": f"写入文件 {path}，内容 {line_count} 行 [模拟执行完成]",
                "__name": tool_name,
                "__callback": __run_write_to_file,
            }
        return "写入文件参数缺失"

    def _execute_attempt_completion_tool(self, root: ET.Element, tool_name: str, tool_xml: str) -> str:
        ac_elem = root.find('.//attempt_completion')
        result_elem = root.find('.//result')

        if result_elem is not None and result_elem is not None:
            result = result_elem.text or ""

            def __run_attempt_completion_tool():
                return result

            return {
                "desc": f"尝试结束任务",
                "__name": tool_name,
                "__callback": __run_attempt_completion_tool,
            }
        return "写入文件参数缺失"

    def process_tagged_stream(self, chunk: str, tag_name: str) -> Tuple[str, str]:
        """
        Process a stream chunk and separate content inside and outside the specified tag.

        This function handles cases where chunks are randomly split and tags may be incomplete.

        Args:
            chunk: The incoming stream chunk
            tag_name: The tag name to look for (e.g., "think")

        Returns:
            A tuple of (outside_content, inside_content) where:
            - outside_content: Content outside the tag
            - inside_content: Content inside the tag (empty if not currently inside tag)
        """
        start_tag = f"<{tag_name}>"
        end_tag = f"</{tag_name}>"

        # 初始化缓冲区（如果不存在）
        if not hasattr(self, '_tag_buffer'):
            self._tag_buffer = {}

        if tag_name not in self._tag_buffer:
            self._tag_buffer[tag_name] = {
                'state': 'outside',  # outside, inside, start_tag_partial, end_tag_partial
                'buffer': '',
                'partial_start': '',
                'partial_end': ''
            }

        buffer_info = self._tag_buffer[tag_name]
        state = buffer_info['state']
        buffer_content = buffer_info['buffer']
        partial_start = buffer_info['partial_start']
        partial_end = buffer_info['partial_end']

        outside_content = ""
        inside_content = ""

        # 处理当前chunk
        current_text = chunk
        i = 0

        while i < len(current_text):
            if state == 'outside':
                # 在标签外部，寻找开始标签
                start_pos = current_text.find(start_tag, i)

                if start_pos != -1:
                    # 找到完整的开始标签
                    outside_content += current_text[i:start_pos]
                    state = 'inside'
                    i = start_pos + len(start_tag)
                    buffer_content = ""
                else:
                    # 检查是否有部分开始标签
                    found_partial = False
                    for j in range(len(start_tag), 0, -1):
                        partial = start_tag[:j]
                        if current_text.endswith(partial, i, len(current_text)):
                            # 找到部分开始标签
                            outside_content += current_text[i:len(
                                current_text)-j]
                            partial_start = partial
                            state = 'start_tag_partial'
                            i = len(current_text)
                            found_partial = True
                            break

                    if not found_partial:
                        # 没有找到开始标签或部分开始标签
                        outside_content += current_text[i:]
                        i = len(current_text)

            elif state == 'start_tag_partial':
                # 之前有部分开始标签，现在尝试补全
                remaining_needed = start_tag[len(partial_start):]

                if current_text.startswith(remaining_needed, i):
                    # 成功补全开始标签
                    state = 'inside'
                    buffer_content = ""
                    i += len(remaining_needed)
                    partial_start = ""
                else:
                    # 检查当前文本是否能形成更长的部分标签
                    combined = partial_start + current_text[i:]
                    found_extension = False

                    for j in range(len(start_tag), len(partial_start), -1):
                        if combined.startswith(start_tag[:j]):
                            # 形成了更长的部分标签
                            partial_start = start_tag[:j]
                            i = len(current_text)
                            found_extension = True
                            break

                    if not found_extension:
                        # 无法补全，回到外部状态
                        outside_content += partial_start + current_text[i:]
                        state = 'outside'
                        partial_start = ""
                        i = len(current_text)

            elif state == 'inside':
                # 在标签内部，寻找结束标签
                end_pos = current_text.find(end_tag, i)

                if end_pos != -1:
                    # 找到完整的结束标签
                    inside_content += buffer_content + current_text[i:end_pos]
                    state = 'outside'
                    buffer_content = ""
                    i = end_pos + len(end_tag)
                else:
                    # 检查是否有部分结束标签
                    found_partial = False
                    for j in range(len(end_tag), 0, -1):
                        partial = end_tag[:j]
                        if current_text.endswith(partial, i, len(current_text)):
                            # 找到部分结束标签
                            buffer_content += current_text[i:len(
                                current_text)-j]
                            partial_end = partial
                            state = 'end_tag_partial'
                            i = len(current_text)
                            found_partial = True
                            break

                    if not found_partial:
                        # 没有找到结束标签或部分结束标签
                        buffer_content += current_text[i:]
                        i = len(current_text)

            elif state == 'end_tag_partial':
                # 之前有部分结束标签，现在尝试补全
                remaining_needed = end_tag[len(partial_end):]

                if current_text.startswith(remaining_needed, i):
                    # 成功补全结束标签
                    inside_content += buffer_content
                    state = 'outside'
                    buffer_content = ""
                    partial_end = ""
                    i += len(remaining_needed)
                else:
                    # 检查当前文本是否能形成更长的部分结束标签
                    combined = partial_end + current_text[i:]
                    found_extension = False

                    for j in range(len(end_tag), len(partial_end), -1):
                        if combined.startswith(end_tag[:j]):
                            # 形成了更长的部分结束标签
                            partial_end = end_tag[:j]
                            buffer_content += current_text[i:]
                            i = len(current_text)
                            found_extension = True
                            break

                    if not found_extension:
                        # 无法补全，回到内部状态
                        buffer_content += partial_end + current_text[i:]
                        state = 'inside'
                        partial_end = ""
                        i = len(current_text)

        # 更新缓冲区状态
        buffer_info['state'] = state
        buffer_info['buffer'] = buffer_content
        buffer_info['partial_start'] = partial_start
        buffer_info['partial_end'] = partial_end

        return outside_content, inside_content


def process_tagged_stream_v2(chunk: str, tag_name: str, tag_buffer: dict) -> Tuple[str, str]:
    """
    Incrementally process a stream chunk and separate content inside and outside the specified tag.
    Handles partial tags and maintains internal state across chunks.
    """
    start_tag = f"<{tag_name}>"
    end_tag = f"</{tag_name}>"
    if tag_name not in tag_buffer:
        tag_buffer[tag_name] = {
            "partial": "",   # 跨chunk残留部分
            "inside": False  # 当前是否处于标签内部
        }
    state = tag_buffer[tag_name]
    # 拼接残留
    data = state["partial"] + chunk
    state["partial"] = ""
    outside_content = ""
    inside_content = ""
    i = 0
    while i < len(data):
        if not state["inside"]:
            # 找 start_tag
            start_idx = data.find(start_tag, i)
            if start_idx == -1:
                # 检查是否结尾是 start_tag 的前缀
                prefix_len = 0
                for k in range(1, len(start_tag)):
                    if data.endswith(start_tag[:k]):
                        prefix_len = k
                if prefix_len > 0:
                    # 把完整的前缀留作 partial
                    state["partial"] = data[-prefix_len:]
                    outside_content += data[i:len(data)-prefix_len]
                else:
                    outside_content += data[i:]
                break
            else:
                # 输出 start_tag 前的部分
                outside_content += data[i:start_idx]
                i = start_idx + len(start_tag)
                state["inside"] = True
        else:
            # inside 模式
            end_idx = data.find(end_tag, i)
            if end_idx == -1:
                # 检查结尾是否是 end_tag 的前缀
                prefix_len = 0
                for k in range(1, len(end_tag)):
                    if data.endswith(end_tag[:k]):
                        prefix_len = k
                if prefix_len > 0:
                    state["partial"] = data[-prefix_len:]
                    inside_content += data[i:len(data)-prefix_len]
                else:
                    inside_content += data[i:]
                break
            else:
                inside_content += data[i:end_idx]
                i = end_idx + len(end_tag)
                state["inside"] = False
    # 关键修正：确保 partial 真的是一个标签前缀，而不是误包含标签内容
    if state["partial"]:
        # 如果 partial 中没有 '<'，说明没必要保留
        if '<' not in state["partial"]:
            state["partial"] = ''
        # 如果 partial 同时包含 '>'，说明已经完整，不应该保留
        elif '>' in state["partial"]:
            state["partial"] = ''
    return outside_content, inside_content


if __name__ == "__main__":
    # 创建一个 LLMProxy 实例来测试 test_process_tagged_stream 方法
    # 因为 test_process_tagged_stream 不依赖于其他组件，所以可以传入 None

    """
    Test function for process_tagged_stream with various chunk scenarios.
    """
    # 合并测试用例和期望输出为一个数据结构
    test_cases = [
        # Test case 1: 随机组合chunks
        {
            "chunks": ["hello ", "<think", ">thinking content</thi", "nk> goodbye"],
            "expected": {
                "outside": "hello  goodbye",
                "inside": "thinking content"
            }
        },
        # Test case 2: 多个标签和普通文本混合
        {
            "chunks": ["<think>thought 1</think>", "some text", "<think>thought 2</think>"],
            "expected": {
                "outside": "some text",
                "inside": "thought 1thought 2"
            }
        },
        # Test case 3: 部分标签
        {
            "chunks": ["partial<thinking", ">", "more content", "</think", "ing>"],
            "expected": {
                "outside": "partial<thinking>more content</thinking>",
                "inside": ""
            }
        },
        # Test case 4: 嵌套标签
        {
            "chunks": ["<think>deep<think>nested</think>thinking</think>"],
            "expected": {
                "outside": "thinking</think>",
                "inside": "deep<think>nested"
            }
        },
        # Test case 5: 双重嵌套标签
        {
            "chunks": ["<think><think>double nested</think></think>"],
            "expected": {
                "outside": "</think>",
                "inside": "<think>double nested"
            }
        },
        # Test case 6: 无标签
        {
            "chunks": ["no tags here", "just regular text"],
            "expected": {
                "outside": "no tags herejust regular text",
                "inside": ""
            }
        },
        # Test case 7: 跨多个chunk的标签内容
        {
            "chunks": ["<think>start", " middle ", "end</think>"],
            "expected": {
                "outside": "",
                "inside": "start middle end"
            }
        },
        # Test case 8: 不完整的标签
        {
            "chunks": ["<think>incomplete"],
            "expected": {
                "outside": "",
                "inside": "incomplete"
            }
        },
        # Test case 9: 尾部闭合标签和新开始标签
        {
            "chunks": ["</think>trailing close", "<think>new start</think>"],
            "expected": {
                "outside": "</think>trailing close",
                "inside": "new start"
            }
        },
        # Test case 10: 不匹配的标签
        {
            "chunks": ["<think>mismatched</thinking>"],
            "expected": {
                "outside": "",
                "inside": "mismatched</thinking>"
            }
        },
        # Test case 11: 包含特殊字符的标签内容
        {
            "chunks": ["<think>content with <special> chars</special></think>"],
            "expected": {
                "outside": "",
                "inside": "content with <special> chars</special>"
            }
        },
        # Test case 12: 空chunks
        {
            "chunks": ["", "<think>", "", "content", "", "</think>", ""],
            "expected": {
                "outside": "",
                "inside": "content"
            }
        },
        # Test case 13: 连续标签
        {
            "chunks": ["<think>content</think><think>more content</think>"],
            "expected": {
                "outside": "",
                "inside": "contentmore content"
            }
        },
        # Test case 14: 多行内容
        {
            "chunks": ["<think>multi", "line\ncontent", "with\nbreaks</think>"],
            "expected": {
                "outside": "",
                "inside": "multiline\ncontentwith\nbreaks"
            }
        }
    ]
    print("Testing process_tagged_stream function:")
    print("=" * 50)
    for i, test_case in enumerate(test_cases):
        chunks = test_case["chunks"]
        expected = test_case["expected"]
        print(f"\nTest case {i+1}: {chunks}")
        outside_parts = []
        inside_parts = []
        llm_proxy = LLMProxy(None, None)
        tag_buffer = {}
        for chunk in chunks:
            # outside, inside = llm_proxy.process_tagged_stream_v2(
            outside, inside = process_tagged_stream_v2(
                chunk, "think", tag_buffer)
            if outside:
                outside_parts.append(outside)
            if inside:
                inside_parts.append(inside)
        final_outside = ''.join(outside_parts)
        final_inside = ''.join(inside_parts)
        print(f"  Outside: '{final_outside}'")
        print(f"  Inside:  '{final_inside}'")
        print(f"  Expected Outside: '{expected['outside']}'")
        print(f"  Expected Inside:  '{expected['inside']}'")
        assert final_outside == expected[
            'outside'], f"Outside mismatch in test case {i+1}"
        assert final_inside == expected[
            'inside'], f"Inside mismatch in test case {i+1}"
        print(f"  ✓ Test case {i+1} passed")
    print("\nAll tests passed! ✓")
