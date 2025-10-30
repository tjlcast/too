
from datetime import datetime
from typing import Any, Dict, List, TYPE_CHECKING

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
            'search_and_replace', 'search_files', 'write_to_file'
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

            # display yielded outputs in order
            for typ, val in outputs:
                if typ == "text":
                    if val:
                        self.view.display_ai_message_chunk(val)
                        full_response += val
                elif typ == "tool":
                    # try to parse & execute tool block
                    try:
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
                        full_response += val
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
