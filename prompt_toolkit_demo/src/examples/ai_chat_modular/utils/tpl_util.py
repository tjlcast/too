def replace_template_vars(template, vars_map):
    """
    使用简单字符串替换模板中的变量占位符

    Args:
        template (str): 模板字符串
        vars_map (dict): 变量映射字典，键为占位符，值为替换值

    Returns:
        str: 替换变量后的字符串
    """
    result = template
    # 使用简单字符串替换而不是正则表达式替换所有可能的变量占位符
    for var_placeholder, replacement_value in vars_map.items():
        result = result.replace(var_placeholder, replacement_value)

    return result


"""
Run command: python -m src.examples.ai_chat_modular.utils.tpl_util
"""
if __name__ == "__main__":
    """
    测试和展示 replace_template_vars 函数的使用方法
    """
    print("=== Template Variable Replacement Utility Demo ===\n")

    # 示例1: 基本用法
    print("示例1: 基本用法")
    template1 = "Hello, {name}! Welcome to {platform}."
    vars_map1 = {
        "{name}": "Alice",
        "{platform}": "Prompt Toolkit"
    }
    result1 = replace_template_vars(template1, vars_map1)
    print(f"模板: {template1}")
    print(f"变量映射: {vars_map1}")
    print(f"结果: {result1}\n")

    # 示例2: 多次出现的占位符
    print("示例2: 多次出现的占位符")
    template2 = "Dear {name}, thank you {name} for your interest in {product}. {product} is a great choice!"
    vars_map2 = {
        "{name}": "Bob",
        "{product}": "Python"
    }
    result2 = replace_template_vars(template2, vars_map2)
    print(f"模板: {template2}")
    print(f"变量映射: {vars_map2}")
    print(f"结果: {result2}\n")

    # 示例3: 部分匹配情况
    print("示例3: 部分匹配情况")
    template3 = "Visit https://{domain}.com/{domain}/docs for documentation."
    vars_map3 = {
        "{domain}": "example"
    }
    result3 = replace_template_vars(template3, vars_map3)
    print(f"模板: {template3}")
    print(f"变量映射: {vars_map3}")
    print(f"结果: {result3}\n")

    # 示例4: 空值和特殊字符
    print("示例4: 空值和特殊字符")
    template4 = "Status: [{status}] Error: {error_msg}"
    vars_map4 = {
        "{status}": "",
        "{error_msg}": "File not found\nCheck path: C:\\Users\\Documents"
    }
    result4 = replace_template_vars(template4, vars_map4)
    print(f"模板: {template4}")
    print(f"变量映射: {vars_map4}")
    print(f"结果: {result4}\n")

    print("=== 测试完成 ===")
