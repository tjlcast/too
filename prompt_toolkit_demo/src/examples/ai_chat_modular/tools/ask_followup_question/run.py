import json
from typing import Dict, Any, List
from dataclasses import asdict

from .ask_followup_question import AskFollowupQuestionArgs, Suggestion, ask_followup_question
import xml.etree.ElementTree as ET


def run(xml_string: str, basePath: str = None) -> AskFollowupQuestionArgs:
    """
    Execute the ask_followup_question tool with XML input.

    Args:
        xml_string: XML string representing a ask_followup_question tool call
        basePath: Base path for file operations

    Returns:
        AskFollowupQuestionArgs result of the execution
    """
    args = parse_ask_followup_question_xml(xml_string)
    return execute(args, basePath)


def execute(args: Dict[str, Any], basePath: str = None) -> AskFollowupQuestionArgs:
    """
    Execute the ask_followup_question function with parsed arguments.

    Args:
        args: Dictionary containing the parsed arguments
        basePath: Base path for file operations

    Returns:
        AskFollowupQuestionArgs result or error in dict format
    """
    # 如果是错误情况，直接返回包含错误信息的对象
    if "error" in args:
        return AskFollowupQuestionArgs(
            question="",
            follow_up=[],
            error=args['error']
        )

    try:
        # 处理参数并执行主要逻辑
        result = ask_followup_question(args, basePath)

        # 如果有错误，返回包含错误信息的对象
        if isinstance(result, dict) and "error" in result:
            return AskFollowupQuestionArgs(
                question="",
                follow_up=[],
                error=result['error']
            )

        # 返回结果对象
        return result

    except Exception as e:
        # 在异常情况下，返回包含错误信息的对象
        return AskFollowupQuestionArgs(
            question="",
            follow_up=[],
            error=f"Error executing ask_followup_question: {str(e)}"
        )


def parse_ask_followup_question_xml(xml_string: str) -> Dict[str, Any]:
    """
    Parse XML string into the args structure for ask_followup_question tool.

    Args:
        xml_string: XML string representing a ask_followup_question tool call

    Returns:
        Dictionary with the parsed args structure or error information
    """
    try:
        # Wrap the XML in a root element if it doesn't have one
        xml_string = xml_string.strip()
        if not xml_string.startswith('<ask_followup_question>'):
            xml_string = f"<root>{xml_string}</root>"
            root = ET.fromstring(xml_string)
            ask_followup_question_element = root.find('ask_followup_question')
        else:
            ask_followup_question_element = ET.fromstring(xml_string)

        if ask_followup_question_element is None:
            return {"error": "Invalid XML format"}

        # 查找 question 元素
        question_element = ask_followup_question_element.find('question')
        if question_element is None:
            return {"error": "Missing <question> element"}

        question = question_element.text.strip() if question_element.text else ""

        # 查找 follow_up 元素
        follow_up_element = ask_followup_question_element.find('follow_up')
        if follow_up_element is None:
            return {"error": "Missing <follow_up> element"}

        # 解析建议答案
        suggestions = []
        for suggest_element in follow_up_element.findall('suggest'):
            suggestion_text = suggest_element.text.strip() if suggest_element.text else ""
            mode_attr = suggest_element.get('mode')

            if mode_attr:
                suggestions.append({
                    "text": suggestion_text,
                    "mode": mode_attr
                })
            else:
                suggestions.append(suggestion_text)

        # 构建参数对象
        return {
            "args": {
                "question": question,
                "follow_up": suggestions
            }
        }

    except ET.ParseError as e:
        return {"error": f"XML parsing error: {str(e)}"}
    except TypeError as e:
        return {"error": f"Invalid arguments: {str(e)}"}
    except Exception as e:
        return {"error": f"Error parsing XML: {str(e)}"}


# For testing purposes
if __name__ == "__main__":
    from pathlib import Path
    current_working_directory = Path.cwd()

    # 测试基本的 ask_followup_question 功能
    xml_example = """
    <ask_followup_question>
    <question>What is the path to the frontend-config.json file?</question>
    <follow_up>
    <suggest>./src/frontend-config.json</suggest>
    <suggest>./config/frontend-config.json</suggest>
    <suggest>./frontend-config.json</suggest>
    </follow_up>
    </ask_followup_question>
    """
    result = run(xml_example, current_working_directory)
    print("Basic test result:")
    print(result)
    print()

    # 测试带有 mode 属性的 ask_followup_question 功能
    xml_example_with_mode = """
    <ask_followup_question>
    <question>How would you like to proceed with this task?</question>
    <follow_up>
    <suggest mode="code">Start implementing the solution</suggest>
    <suggest mode="architect">Plan the architecture first</suggest>
    <suggest>Continue with more details</suggest>
    </follow_up>
    </ask_followup_question>
    """
    result = run(xml_example_with_mode, current_working_directory)
    print("Test result with mode attributes:")
    print(result)
    print()

    # 测试错误情况 - 缺少 question 元素
    xml_example_error = """
    <ask_followup_question>
    <follow_up>
    <suggest>Option 1</suggest>
    <suggest>Option 2</suggest>
    </follow_up>
    </ask_followup_question>
    """
    result = run(xml_example_error, current_working_directory)
    print("Error test result (missing question):")
    print(result)
    print()

    # 测试错误情况 - 缺少 follow_up 元素
    xml_example_error2 = """
    <ask_followup_question>
    <question>What is your favorite color?</question>
    </ask_followup_question>
    """
    result = run(xml_example_error2, current_working_directory)
    print("Error test result (missing follow_up):")
    print(result)
