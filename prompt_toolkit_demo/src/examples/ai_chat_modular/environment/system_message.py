from .prompt_tpl.system_prompt import ss as system_prompt_tpl
from .system_info import get_system_info_section
from .environment_proxy import EnvironmentProxy
from ..utils.time_util import get_current_timestamp
from ..utils.tpl_util import replace_template_vars


def get_message_message():
    """
    生成系统提示信息，替换模板中的变量
    
    Returns:
        str: 替换变量后的系统提示信息
    """
    # 获取环境信息
    env_proxy = EnvironmentProxy()
    current_dir = env_proxy.get_current_dir()
    current_time = get_current_timestamp()
    current_working_directory = env_proxy.get_current_working_directory()
    
    # 获取系统信息部分
    system_info_section = get_system_info_section(current_dir)
    
    # 替换模板中的变量
    vars_map = {
        "{{current_time}}": current_time,
        "{{current_working_directory}}": current_working_directory,
        "{{system_info_section}}": system_info_section,
        "{{current_dir}}": current_dir
    }
    
    system_prompt = replace_template_vars(system_prompt_tpl, vars_map)
    
    return system_prompt

"""
Run command: python -m src.examples.ai_chat_modular.environment.system_message
"""
if __name__ == "__main__":
    # 测试函数功能
    print("Testing system message generation...")
    message = get_message_message()
    print("Generated system message:")
    print("=" * 50)
    print(message)
    print("=" * 50)
    print(f"Total length: {len(message)} characters")