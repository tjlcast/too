from typing import Dict, Any

from prompt_toolkit_demo.src.examples.ai_agent.tools.read_file.read_file import read_file


def run(xml_string: str, basePath: str = None) -> str:
    result = read_file(xml_string, basePath)
    
    # 如果有错误，返回错误信息
    if "error" in result:
        return f"Error: {result['error']}"
    
    # 获取结果列表
    results = result.get("results", [])
    
    # 构建返回的字符串格式
    output_lines = [f"[read_file for {len(results)} files] Result:"]
    output_lines.append("The user approved this operation and provided the following context:")
    output_lines.append("<feedback>")
    output_lines.append("VS Code/Untitled-2:1-5")
    output_lines.append("</feedback>")
    output_lines.append("<files>")
    
    # 添加每个文件的内容
    for file_result in results:
        if file_result.get("status") == "success":
            path = file_result.get("path", "")
            content = file_result.get("content", "")
            
            # 计算行数
            lines = content.split('\n') if content else []
            line_count = len(lines)
            line_range = f"1-{line_count}" if line_count > 0 else "1-0"
            
            output_lines.append(f"<file><path>{path}</path>")
            output_lines.append(f"<content lines=\"{line_range}\">")
            output_lines.append(content)
            output_lines.append("</content>")
            output_lines.append("</file>")
        else:
            # 处理错误情况
            path = file_result.get("path", "")
            error = file_result.get("error", "Unknown error")
            output_lines.append(f"<file><path>{path}</path>")
            output_lines.append(f"<error>{error}</error>")
            output_lines.append("</file>")
    
    output_lines.append("</files>")
    
    return "\n".join(output_lines)


# For testing purposes
if __name__ == "__main__":
    from pathlib import Path
    current_working_directory = Path.cwd()

    xml_example = """
    <read_file>
    <args>
      <file>
        <path>prompt_toolkit_demo/src/examples/ai_agent/tools/read_file/read_file.py</path>
      </file>
      <file>
        <path>prompt_toolkit_demo/src/main.py</path>
      </file>
    </args>
    </read_file>
    """
    print(run(xml_example, current_working_directory))