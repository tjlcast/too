from .environment_proxy import EnvironmentProxy


tpl = """
<environment_details>
# VSCode Visible Files


# VSCode Open Tabs


# Current Time
Current time in ISO 8601 UTC format: 2025-10-20T01:42:44.726Z
User time zone: Asia/Shanghai, UTC+8:00

# Current Cost
$0.00

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
<model>gpt-4o</model>


{{environment_details_files}}
"""


def get_environment_details(envir_proxy: EnvironmentProxy) -> str:
    environment_details_files = envir_proxy.get_current_working_directory()
    system_prompt = tpl
    vars_map = {
        "{{environment_details_files}}": environment_details_files,
    }

    # 使用简单字符串替换而不是正则表达式替换所有可能的变量占位符
    for var_placeholder, replacement_value in vars_map.items():
        system_prompt = system_prompt.replace(var_placeholder, replacement_value)
        
    return system_prompt

"""
Run command: python -m src.examples.ai_chat_modular.environment.environment_detail
"""
if __name__ == "__main__":
    # 测试函数功能
    print("Testing environment details generation...")
    env_proxy = EnvironmentProxy()
    details = get_environment_details(env_proxy)
    print("Generated environment details:")
    print("=" * 50)
    print(details[:1000])  # 只打印前1000个字符避免输出过长
    print("...")
    print("=" * 50)
    print(f"Total length: {len(details)} characters")