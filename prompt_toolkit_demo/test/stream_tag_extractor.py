"""
流式数据标签提取工具

该工具用于从流式数据块中提取指定标签的内容，特别处理标签在chunk边界被截断的情况。
"""

from typing import Dict, Tuple


class StreamTagExtractor:
    """
    流式标签提取器
    
    处理流式数据块中的标签提取，能够处理标签在chunk边界被截断的情况。
    """
    
    def __init__(self):
        """初始化提取器"""
        # 存储每个标签的状态
        self._tag_states: Dict[str, Dict] = {}
    
    def extract_tag_content(self, chunk: str, tag_name: str) -> Tuple[str, str]:
        """
        从数据块中提取指定标签的内容
        
        Args:
            chunk: 流式数据块
            tag_name: 要提取的标签名称
            
        Returns:
            Tuple[str, str]: (标签外内容, 标签内内容)
            - 标签外内容: 不在标签内的文本内容
            - 标签内内容: 在标签内的文本内容，如果当前不在标签内则为空字符串
        """
        # 获取或初始化该标签的状态
        if tag_name not in self._tag_states:
            self._tag_states[tag_name] = {
                'inside_tag': False,  # 是否在标签内部
                'buffer': '',         # 缓冲区，用于存储不完整的标签片段
            }
        
        tag_state = self._tag_states[tag_name]
        
        # 完整的开始和结束标签
        start_tag = f"<{tag_name}>"
        end_tag = f"</{tag_name}>"
        
        # 将缓冲区内容与当前块合并
        combined_content = tag_state['buffer'] + chunk
        tag_state['buffer'] = ''  # 清空缓冲区
        
        outside_content = ""
        inside_content = ""
        
        i = 0
        while i < len(combined_content):
            if not tag_state['inside_tag']:
                # 查找开始标签
                start_pos = combined_content.find(start_tag, i)
                if start_pos != -1:
                    # 添加开始标签之前的内容到outside_content
                    outside_content += combined_content[i:start_pos]
                    # 跳过开始标签
                    i = start_pos + len(start_tag)
                    tag_state['inside_tag'] = True
                else:
                    # 没有找到开始标签，检查是否有部分开始标签
                    partial_start = self._get_partial_start(combined_content[i:], start_tag)
                    if partial_start:
                        # 保存部分开始标签到缓冲区
                        tag_state['buffer'] = partial_start
                        outside_content += combined_content[i:len(combined_content) - len(partial_start)]
                    else:
                        # 没有部分开始标签，全部内容都在标签外
                        outside_content += combined_content[i:]
                    break
            else:
                # 查找结束标签
                end_pos = combined_content.find(end_tag, i)
                if end_pos != -1:
                    # 添加结束标签之前的内容到inside_content
                    inside_content += combined_content[i:end_pos]
                    # 跳过结束标签
                    i = end_pos + len(end_tag)
                    tag_state['inside_tag'] = False
                else:
                    # 没有找到结束标签，检查是否有部分结束标签
                    partial_end = self._get_partial_end(combined_content[i:], end_tag)
                    if partial_end:
                        # 保存部分结束标签到缓冲区
                        tag_state['buffer'] = partial_end
                        inside_content += combined_content[i:len(combined_content) - len(partial_end)]
                    else:
                        # 没有部分结束标签，剩余内容都在标签内
                        inside_content += combined_content[i:]
                    break
        
        return outside_content, inside_content
    
    def _get_partial_start(self, text: str, start_tag: str) -> str:
        """
        检查文本末尾是否有开始标签的部分匹配
        
        Args:
            text: 要检查的文本
            start_tag: 完整的开始标签
            
        Returns:
            str: 部分匹配的标签片段，如果没有则返回空字符串
        """
        # 从最长可能的部分开始检查
        for i in range(min(len(text), len(start_tag) - 1), 0, -1):
            if text.endswith(start_tag[:i]):
                return start_tag[:i]
        return ""
    
    def _get_partial_end(self, text: str, end_tag: str) -> str:
        """
        检查文本末尾是否有结束标签的部分匹配
        
        Args:
            text: 要检查的文本
            end_tag: 完整的结束标签
            
        Returns:
            str: 部分匹配的标签片段，如果没有则返回空字符串
        """
        # 从最长可能的部分开始检查
        for i in range(min(len(text), len(end_tag) - 1), 0, -1):
            if text.endswith(end_tag[:i]):
                return end_tag[:i]
        return ""
    
    def reset_state(self, tag_name: str = None):
        """
        重置标签状态
        
        Args:
            tag_name: 要重置的标签名称，如果为None则重置所有标签状态
        """
        if tag_name:
            if tag_name in self._tag_states:
                del self._tag_states[tag_name]
        else:
            self._tag_states.clear()


def extract_tag_content(chunk: str, tag_name: str, tag_states: dict = None) -> Tuple[str, str, dict]:
    """
    从数据块中提取指定标签的内容（函数接口版本）
    
    Args:
        chunk: 流式数据块
        tag_name: 要提取的标签名称
        tag_states: 标签状态字典，用于跨chunk维护状态
        
    Returns:
        Tuple[str, str, dict]: (标签外内容, 标签内内容, 更新后的标签状态)
    """
    if tag_states is None:
        tag_states = {}
    
    # 获取或初始化该标签的状态
    if tag_name not in tag_states:
        tag_states[tag_name] = {
            'inside_tag': False,
            'buffer': '',
        }
    
    tag_state = tag_states[tag_name]
    
    # 完整的开始和结束标签
    start_tag = f"<{tag_name}>"
    end_tag = f"</{tag_name}>"
    
    # 将缓冲区内容与当前块合并
    combined_content = tag_state['buffer'] + chunk
    tag_state['buffer'] = ''  # 清空缓冲区
    
    outside_content = ""
    inside_content = ""
    
    i = 0
    while i < len(combined_content):
        if not tag_state['inside_tag']:
            # 查找开始标签
            start_pos = combined_content.find(start_tag, i)
            if start_pos != -1:
                # 添加开始标签之前的内容到outside_content
                outside_content += combined_content[i:start_pos]
                # 跳过开始标签
                i = start_pos + len(start_tag)
                tag_state['inside_tag'] = True
            else:
                # 没有找到开始标签，检查是否有部分开始标签
                partial_start = ""
                for j in range(min(len(combined_content[i:]), len(start_tag) - 1), 0, -1):
                    if combined_content[i:].endswith(start_tag[:j]):
                        partial_start = start_tag[:j]
                        break
                
                if partial_start:
                    # 保存部分开始标签到缓冲区
                    tag_state['buffer'] = partial_start
                    outside_content += combined_content[i:len(combined_content) - len(partial_start)]
                else:
                    # 没有部分开始标签，全部内容都在标签外
                    outside_content += combined_content[i:]
                break
        else:
            # 查找结束标签
            end_pos = combined_content.find(end_tag, i)
            if end_pos != -1:
                # 添加结束标签之前的内容到inside_content
                inside_content += combined_content[i:end_pos]
                # 跳过结束标签
                i = end_pos + len(end_tag)
                tag_state['inside_tag'] = False
            else:
                # 没有找到结束标签，检查是否有部分结束标签
                partial_end = ""
                for j in range(min(len(combined_content[i:]), len(end_tag) - 1), 0, -1):
                    if combined_content[i:].endswith(end_tag[:j]):
                        partial_end = end_tag[:j]
                        break
                
                if partial_end:
                    # 保存部分结束标签到缓冲区
                    tag_state['buffer'] = partial_end
                    inside_content += combined_content[i:len(combined_content) - len(partial_end)]
                else:
                    # 没有部分结束标签，剩余内容都在标签内
                    inside_content += combined_content[i:]
                break
    
    return outside_content, inside_content, tag_states


# 测试代码
if __name__ == "__main__":
    # 测试用例1: 标签被分割在不同chunk中
    extractor = StreamTagExtractor()
    
    print("测试用例1: 标签被分割在不同chunk中")
    print("-" * 40)
    
    chunks = ["hello ", "<think", ">thinking content</thi", "nk> goodbye"]
    for i, chunk in enumerate(chunks):
        outside, inside = extractor.extract_tag_content(chunk, "think")
        print(f"Chunk {i+1}: '{chunk}'")
        print(f"  标签外内容: '{outside}'")
        print(f"  标签内内容: '{inside}'")
        print()
    
    # 重置状态
    extractor.reset_state()
    
    print("测试用例2: 多个完整标签")
    print("-" * 40)
    
    chunks = ["text <think>thought 1</think> some text <think>thought 2</think> more text"]
    for i, chunk in enumerate(chunks):
        outside, inside = extractor.extract_tag_content(chunk, "think")
        print(f"Chunk {i+1}: '{chunk}'")
        print(f"  标签外内容: '{outside}'")
        print(f"  标签内内容: '{inside}'")
        print()