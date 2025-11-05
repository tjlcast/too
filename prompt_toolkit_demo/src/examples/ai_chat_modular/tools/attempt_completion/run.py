import json
from typing import Dict, Any
from dataclasses import asdict

from .attempt_completion import AttemptCompletionArgs, attempt_completion
import xml.etree.ElementTree as ET


def run(xml_string: str, basePath: str = None) -> str:
    """
    Execute the attempt_completion tool with XML input.
    
    Args:
        xml_string: XML string representing a attempt_completion tool call
        basePath: Base path for file operations
        
    Returns:
        String result of the execution
    """
    args = parse_attempt_completion_xml(xml_string)
    return execute(args, basePath)


def execute(args: Dict[str, Any], basePath: str = None) -> str:
    """
    Execute the attempt_completion function with parsed arguments.
    
    Args:
        args: Dictionary containing the parsed arguments
        basePath: Base path for file operations
        
    Returns:
        String result or error message
    """
    # 如果是错误情况，直接返回
    if "error" in args:
        return f"Error: {args['error']}"
        
    try:
        # 将字典转换为数据类实例
        if isinstance(args, dict) and "args" in args:
            args_obj = AttemptCompletionArgs(**args["args"])
            # 转换回字典以保持接口兼容
            args_dict = asdict(args_obj)
        else:
            args_dict = args
            
        result = attempt_completion({"args": args_dict}, basePath)

        # 如果有错误，返回错误信息
        if "error" in result.result:
            return f"Error: {result['error']}"

        # 返回结果
        return result.result
        
    except Exception as e:
        return f"Error executing attempt_completion: {str(e)}"


def parse_attempt_completion_xml(xml_string: str) -> Dict[str, Any]:
    """
    Parse XML string into the args structure for attempt_completion tool using AttemptCompletionArgs.

    Args:
        xml_string: XML string representing a attempt_completion tool call

    Returns:
        Dictionary with the parsed args structure or error information
    """
    try:
        # Wrap the XML in a root element if it doesn't have one
        xml_string = xml_string.strip()
        if not xml_string.startswith('<attempt_completion>'):
            xml_string = f"<root>{xml_string}</root>"
            root = ET.fromstring(xml_string)
            attempt_completion_element = root.find('attempt_completion')
        else:
            attempt_completion_element = ET.fromstring(xml_string)

        if attempt_completion_element is None:
            return {"error": "Invalid XML format"}

        # Try to find result directly under attempt_completion or in args/result
        result_element = attempt_completion_element.find('result')
        if result_element is None:
            args_element = attempt_completion_element.find('args')
            if args_element is not None:
                result_element = args_element.find('result')

        if result_element is None or not result_element.text:
            return {"error": "Missing <result> element or empty result content"}

        result = result_element.text.strip()

        # 使用数据类进行结构验证和转换
        args_obj = AttemptCompletionArgs(result=result)
        
        return {
            "args": asdict(args_obj)
        }

    except ET.ParseError as e:
        return {"error": f"XML parsing error: {str(e)}"}
    except TypeError as e:
        return {"error": f"Invalid arguments for AttemptCompletionArgs: {str(e)}"}
    except Exception as e:
        return {"error": f"Error parsing XML: {str(e)}"}


# For testing purposes
if __name__ == "__main__":
    from pathlib import Path
    current_working_directory = Path.cwd()

    xml_example = """
    <attempt_completion>
    <args>
      <result>
Task completed successfully
</result>
    </args>
    </attempt_completion>
    """
    result = run(xml_example, current_working_directory)
    print(result)

    xml_example = """
    <attempt_completion>
    <result>
Task completed successfully
</result>
    </attempt_completion>
    """
    result = run(xml_example, current_working_directory)
    print(result)