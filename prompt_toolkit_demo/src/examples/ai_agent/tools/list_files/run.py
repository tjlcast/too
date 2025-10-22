import json
from typing import Dict, Any

from prompt_toolkit_demo.src.examples.ai_agent.tools.list_files.list_files import list_files


def run(xml_string: str, basePath: str = None) -> str:
    result = list_files(xml_string, basePath)
    
    # 如果有错误，返回错误信息
    if "error" in result:
        return f"Error: {result['error']}"
    
    # 获取路径信息
    path = result.get("path", "")
    
    # 构建返回的字符串格式
    output_lines = [f"[list_files for '{path}'] Result:"]
    
    # 添加文件名列表
    items = result.get("items", [])
    for item in items:
        if item.get("type") == "file":
            output_lines.append(item.get("name", ""))
    
    return "\n".join(output_lines)


# For testing purposes
if __name__ == "__main__":
    from pathlib import Path
    current_working_directory = Path.cwd()

    xml_example = """
    <list_files>
    <args>
      <path>.</path>
      <recursive>false</recursive>
    </args>
    </list_files>
    """
    result = run(xml_example, current_working_directory)
    # print(json.dumps(result, indent=4))
    print(result)

    xml_example = """
    <list_files>
    <args>
      <path>prompt_toolkit_demo/src/examples/ai_agent/tools</path>
      <recursive>true</recursive>
    </args>
    </list_files>
    """
    result = run(xml_example, current_working_directory)
    # print(json.dumps(result, indent=4))
    print(result)