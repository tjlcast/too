from .environment_proxy import EnvironmentProxy


tpl = """
<environment_details>
# VSCode Visible Files


# VSCode Open Tabs


# Current Time
Current time in ISO 8601 UTC format: {{current_time}}
User time zone: {{user_timezone}}

# Current Cost
$0.00

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
<model>gpt-4o</model>


{{environment_details_files}}
</environment_details>
"""


def get_environment_details(envir_proxy: EnvironmentProxy, with_workspace: bool = True) -> str:
    environment_details_files = ''
    if with_workspace:
        environment_details_files = envir_proxy.get_current_working_directory()

    # Get current time
    from datetime import datetime, timezone
    current_time = datetime.now(timezone.utc).isoformat()

    # Get local timezone
    local_time = datetime.now().astimezone()
    local_tz = local_time.tzinfo
    tz_name = str(local_tz)
    tz_offset = local_tz.utcoffset(local_time)
    offset_hours = int(tz_offset.total_seconds() / 3600)
    offset_minutes = int((tz_offset.total_seconds() % 3600) / 60)
    if offset_minutes == 0:
        offset_str = f"UTC{offset_hours:+d}"
    else:
        offset_str = f"UTC{offset_hours:+d}:{offset_minutes:02d}"
    # 构建完整的时区信息
    user_timezone_info = f"{tz_name}, {offset_str}"

    system_prompt = tpl
    vars_map = {
        "{{environment_details_files}}": environment_details_files,
        "{{current_time}}": current_time,
        "{{user_timezone}}": user_timezone_info,
    }

    # 使用简单字符串替换而不是正则表达式替换所有可能的变量占位符
    for var_placeholder, replacement_value in vars_map.items():
        system_prompt = system_prompt.replace(
            var_placeholder, replacement_value)

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
