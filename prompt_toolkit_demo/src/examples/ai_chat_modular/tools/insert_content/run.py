from typing import Dict, Any
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser
from .insert_content import InsertContentArgs, insert_content


def run(xml_string: str, basePath: str = None) -> str:
    exec_args = parse_insert_content_xml(xml_string)
    return execute(exec_args, basePath)


def execute(exec_args: InsertContentArgs, basePath: str = None) -> str:
    result = insert_content(exec_args, basePath)

    # 如果有错误，返回错误信息
    if "error" in result:
        return f"Error: {result['error']}"

    # 获取结果列表
    results = result.get("results", [])
    result = results[0]
    path = result.get("path", "")
    operation = result.get("operation", "")
    user_edits = result.get("user_edits", "")

    # 构建返回的字符串格式
    output_lines = [f"[insert_content for '{path}'] Result:"]
    output_lines.append("<file_write_result>")
    output_lines.append(f"<path>{path}</path>")
    output_lines.append(f"<operation>{operation}</operation>")

    output_lines.append(f"<user_edits>{user_edits}")
    output_lines.append("</file_write_result>")

    # 添加notice部分
    output_lines.append("<notice>")
    output_lines.append(
        "<i>You do not need to re-read the file, as you have seen all changes</i>")
    output_lines.append(
        "<i>Proceed with the task using these changes as the new baseline.</i>")
    output_lines.append(
        "<i>If the user's edits have addressed part of the task or changed the requirements, adjust your approach accordingly.</i>")
    output_lines.append("</notice>")
    output_lines.append("</file_write_result>")

    return "\n".join(output_lines)


def parse_insert_content_xml(xml_string: str) -> InsertContentArgs:
    """
    Parse XML string into the args structure for insert_content tool.

    Args:
        xml_string: XML string representing a insert_content tool call

    Returns:
        InsertContentArgs with the parsed args structure
    """
    try:
        # 用特殊方法处理包含XML标签的文本内容
        # 首先将content标签内容临时替换为占位符
        import re
        
        # 提取content内容，使用非贪婪模式
        content_match = re.search(r'<content>(.*?)</content>', xml_string, re.DOTALL)
        content_text = ""
        if content_match:
            content_text = content_match.group(1)
            
        # 将原始XML中的content内容替换为占位符，使用非贪婪模式
        placeholder_xml = re.sub(r'<content>.*?</content>', '<content>__CONTENT_PLACEHOLDER__</content>', xml_string, flags=re.DOTALL)
        
        # 解析替换后的XML
        root = ET.fromstring(placeholder_xml)
        insert_content_element = root if root.tag == 'insert_content' else root.find('insert_content')
        
        if insert_content_element is None:
            raise ValueError("Invalid XML format")

        path_element = insert_content_element.find('path')
        line_element = insert_content_element.find('line')
        content_element = insert_content_element.find('content')
        
        path = ""
        line = ""
        content = ""
        if path_element is not None and path_element.text:
            path = path_element.text.strip()
        if line_element is not None and line_element.text:
            line = line_element.text.strip()
        if content_element is not None and content_element.text:
            # 使用之前提取的完整content内容
            content = content_text

        return InsertContentArgs(path=path, line=line, content=content)

    except ET.ParseError as e:
        raise ValueError(f"XML parsing error: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing XML: {str(e)}")


# For testing purposes
if __name__ == "__main__":
    from pathlib import Path
    current_working_directory = Path.cwd()

    xml_example = """
    <insert_content>
    <path>test.json</path>
    <line>1</line>
    <content>This is a test line</content>
    </insert_content>
    """
    # print(run(xml_example, current_working_directory))
    
    xml_example = """
<insert_content>
<path>test.json</path>
<line>0</line>
<content>

## search_and_replace 工具使用说明

`search_and_replace` 工具用于在文件中查找并替换特定的文本字符串或正则表达式模式。这是一个强大的工具，可以快速批量修改文件内容。

### 基本语法

```xml
<search_and_replace>
<path>文件路径</path>
<search>要查找的文本</search>
<replace>替换为的文本</replace>
</search_and_replace>
```

### 可选参数

- `use_regex`: 设置为 "true" 时，将 `search` 参数视为正则表达式模式
- `ignore_case`: 设置为 "true" 时，忽略大小写匹配
- `start_line`: 限制替换的起始行号
- `end_line`: 限制替换的结束行号

### 使用示例

#### 示例1：简单文本替换
将文件中的所有 "旧文本" 替换为 "新文本"：

```xml
<search_and_replace>
<path>example.txt</path>
<search>旧文本</search>
<replace>新文本</replace>
</search_and_replace>
```

#### 示例2：使用正则表达式
使用正则表达式替换所有数字：

```xml
<search_and_replace>
<path>example.txt</path>
<search>\d+</search>
<replace>NUM</replace>
<use_regex>true</use_regex>
</search_and_replace>
```

#### 示例3：忽略大小写
忽略大小写替换所有 "hello" 变体：

```xml
<search_and_replace>
<path>example.txt</path>
<search>hello</search>
<replace>Hi</replace>
<ignore_case>true</ignore_case>
</search_and_replace>
```

#### 示例4：限制行范围
只在第10-20行之间进行替换：

```xml
<search_and_replace>
<path>example.txt</path>
<search>oldText</search>
<replace>newText</replace>
<start_line>10</start_line>
<end_line>20</end_line>
</search_and_replace>
```

### 注意事项

1. 使用正则表达式时，确保模式正确
2. 替换前建议备份重要文件
3. 可以同时使用多个可选参数
4. 工具会显示替换前后的差异预览

### 实际演示

下面将演示一个实际的 `search_and_replace` 操作：
</content>
</insert_content>
    """
    print(run(xml_example, current_working_directory))