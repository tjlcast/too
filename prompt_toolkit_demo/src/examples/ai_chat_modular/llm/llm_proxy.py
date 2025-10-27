
from datetime import datetime
from typing import Any, Dict, List

from ..environment.user_message_environment_detail import get_environment_details
from ..environment.environment_proxy import EnvironmentProxy

from ..utils.tpl_util import replace_template_vars
from ..utils.time_util import get_current_timestamp

import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List


class LLMProxy:
    def __init__(self, view_interface, llm_provider):
        """
        Initialize the tool task handler.

        Args:
            view_interface: The view interface for displaying information
            llm_provider: The LLM provider for interacting with AI models
        """
        self.view = view_interface
        self.llm = llm_provider
        self.tools = {}  # Dictionary to hold available tools

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

        Args:
            response_stream: Stream of response chunks from the LLM
            conversation_history: The conversation history

        Returns:
            Dictionary with processing results
        """
        tools_situations = []
        full_response = ""
        self.view.display_ai_header()

        # 工具调用相关的状态变量
        current_tool_buffer = ""  # 当前正在构建的工具调用缓冲区
        in_tool_call = False  # 是否正在处理工具调用
        current_tool_tag = ""  # 当前工具标签名
        tool_depth = 0  # XML标签深度计数器

        # 收集流式响应的token并实时处理工具调用
        for chunk in response_stream:
            # 如果不在工具调用中，正常显示chunk
            if not in_tool_call:
                self.view.display_ai_message_chunk(chunk)

            full_response += chunk

            # 实时处理工具调用检测
            processed_chunk, tool_detected = self._process_chunk_for_tools(
                chunk, current_tool_buffer, in_tool_call, current_tool_tag, tool_depth
            )

            # 更新工具调用状态
            current_tool_buffer = processed_chunk.get('buffer', '')
            in_tool_call = processed_chunk.get('in_tool_call', False)
            current_tool_tag = processed_chunk.get('current_tool_tag', '')
            tool_depth = processed_chunk.get('tool_depth', 0)

            # 如果检测到完整的工具调用并执行完成
            if tool_detected and processed_chunk.get('execution_result'):
                execution_result = processed_chunk['execution_result']
                execution_params = processed_chunk.get('execution_params', '')
                tools_situations.append({
                    "execution_params": execution_params,
                    "execution_result": execution_result,
                })
                self.view.display_ai_message_chunk(
                    f"【工具执行结果】{execution_result}")

        self.view.display_newline()

        # 处理可能残留的不完整工具调用
        if in_tool_call and current_tool_buffer:
            # 不完整的工具调用，按普通文本处理
            self.view.display_ai_message_chunk(current_tool_buffer)
            full_response = full_response.replace(
                current_tool_buffer, '') + current_tool_buffer

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

    def _process_chunk_for_tools(self, chunk: str, current_buffer: str, in_tool_call: bool,
                                 current_tool_tag: str, tool_depth: int) -> tuple:
        """
        实时处理chunk，检测和解析工具调用。

        Args:
            chunk: 当前chunk内容
            current_buffer: 当前工具调用缓冲区
            in_tool_call: 是否正在处理工具调用
            current_tool_tag: 当前工具标签名
            tool_depth: XML标签深度

        Returns:
            tuple: (状态字典, 是否检测到完整工具调用)
        """
        buffer = current_buffer + chunk
        tool_detected = False
        execution_result = None
        execution_params = None

        # 定义支持的工具标签
        tool_tags = [
            'execute_command', 'insert_content', 'list_files', 'read_file',
            'search_and_replace', 'search_files', 'write_to_file'
        ]

        if not in_tool_call:
            # 检测是否开始工具调用
            for tool_tag in tool_tags:
                start_tag = f"<{tool_tag}>"
                if start_tag in buffer:
                    in_tool_call = True
                    current_tool_tag = tool_tag
                    # 找到开始标签的位置
                    start_pos = buffer.find(start_tag)
                    # 将开始标签之前的内容作为普通文本显示
                    if start_pos > 0:
                        normal_text = buffer[:start_pos]
                        self.view.display_ai_message_chunk(normal_text)
                        buffer = buffer[start_pos:]
                    break

        if in_tool_call:
            # 更新标签深度
            open_tag = f"<{current_tool_tag}>"
            close_tag = f"</{current_tool_tag}>"

            # 计算深度（只计算新 chunk 中的标签数量，而不是整个 buffer）
            tool_depth += chunk.count(open_tag)
            tool_depth -= chunk.count(close_tag)

            # 检查是否找到完整的工具调用（深度为0表示标签闭合）
            if tool_depth == 0 and close_tag in buffer:
                # 提取完整的工具调用
                end_pos = buffer.find(close_tag) + len(close_tag)
                full_tool_call = buffer[:end_pos]

                try:
                    # 尝试解析和执行工具调用
                    execution_result = self._parse_and_execute_tool(
                        full_tool_call)
                    execution_params = full_tool_call
                    tool_detected = True

                    # 从缓冲区移除已处理的工具调用
                    buffer = buffer[end_pos:]
                    in_tool_call = False
                    current_tool_tag = ""
                    tool_depth = 0  # 重置深度计数器

                except Exception as e:
                    # 解析失败，将内容作为普通文本处理
                    self.view.display_ai_message_chunk(full_tool_call)
                    buffer = buffer[end_pos:]
                    in_tool_call = False
                    current_tool_tag = ""
                    tool_depth = 0  # 重置深度计数器

        return {
            'buffer': buffer,
            'in_tool_call': in_tool_call,
            'current_tool_tag': current_tool_tag,
            'tool_depth': tool_depth,
            'execution_result': execution_result,
            'execution_params': execution_params
        }, tool_detected

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
                return self._execute_command_tool(root)
            elif tool_name == 'insert_content':
                return self._execute_insert_content_tool(root)
            elif tool_name == 'list_files':
                return self._execute_list_files_tool(root)
            elif tool_name == 'read_file':
                return self._execute_read_file_tool(root)
            elif tool_name == 'search_and_replace':
                return self._execute_search_replace_tool(root)
            elif tool_name == 'search_files':
                return self._execute_search_files_tool(root)
            elif tool_name == 'write_to_file':
                return self._execute_write_file_tool(root)
            else:
                return f"未知工具: {tool_name}"

        except ET.ParseError as e:
            return f"XML解析错误: {str(e)}"
        except Exception as e:
            return f"工具执行失败: {str(e)}"

    # 以下工具执行方法与之前相同，保持不变
    def _execute_command_tool(self, root: ET.Element) -> str:
        """模拟执行命令工具"""
        command_elem = root.find('.//command')
        if command_elem is not None:
            command = command_elem.text or ""
            return f"执行命令: {command} [模拟执行完成]"
        return "命令参数缺失"

    def _execute_insert_content_tool(self, root: ET.Element) -> str:
        """模拟插入内容工具"""
        path_elem = root.find('.//path')
        line_elem = root.find('.//line')
        content_elem = root.find('.//content')

        if all(elem is not None for elem in [path_elem, line_elem, content_elem]):
            path = path_elem.text or ""
            line = line_elem.text or ""
            content = content_elem.text or ""
            return f"在文件 {path} 第 {line} 行插入内容 [模拟执行完成]"
        return "插入内容参数缺失"

    def _execute_list_files_tool(self, root: ET.Element) -> str:
        """模拟列出文件工具"""
        path_elem = root.find('.//path')
        recursive_elem = root.find('.//recursive')

        path = path_elem.text if path_elem is not None else "."
        recursive = recursive_elem.text if recursive_elem is not None else "false"

        return f"列出目录 {path} 的文件 (递归: {recursive}) [模拟执行完成]"

    def _execute_read_file_tool(self, root: ET.Element) -> str:
        """模拟读取文件工具"""
        path_elem = root.find('.//path')
        if path_elem is not None:
            path = path_elem.text or ""
            return f"读取文件 {path} 的内容 [模拟执行完成]"
        return "文件路径参数缺失"

    def _execute_search_replace_tool(self, root: ET.Element) -> str:
        """模拟搜索替换工具"""
        path_elem = root.find('.//path')
        search_elem = root.find('.//search')
        replace_elem = root.find('.//replace')

        if all(elem is not None for elem in [path_elem, search_elem, replace_elem]):
            path = path_elem.text or ""
            search = search_elem.text or ""
            replace = replace_elem.text or ""
            return f"在文件 {path} 中搜索 '{search}' 替换为 '{replace}' [模拟执行完成]"
        return "搜索替换参数缺失"

    def _execute_search_files_tool(self, root: ET.Element) -> str:
        """模拟搜索文件工具"""
        path_elem = root.find('.//path')
        regex_elem = root.find('.//regex')
        file_pattern_elem = root.find('.//file_pattern')

        path = path_elem.text if path_elem is not None else "."
        regex = regex_elem.text if regex_elem is not None else "."
        file_pattern = file_pattern_elem.text if file_pattern_elem is not None else "*"

        return f"在目录 {path} 中搜索文件模式 {file_pattern}，正则表达式 {regex} [模拟执行完成]"

    def _execute_write_file_tool(self, root: ET.Element) -> str:
        """模拟写入文件工具"""
        path_elem = root.find('.//path')
        content_elem = root.find('.//content')
        line_count_elem = root.find('.//line_count')

        if path_elem is not None and content_elem is not None:
            path = path_elem.text or ""
            content = content_elem.text or ""
            line_count = line_count_elem.text if line_count_elem is not None else "未知"
            return f"写入文件 {path}，内容 {line_count} 行 [模拟执行完成]"
        return "写入文件参数缺失"
