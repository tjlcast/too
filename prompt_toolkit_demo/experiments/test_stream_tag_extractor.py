#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
StreamTagExtractor测试和使用示例
"""

from stream_tag_extractor import StreamTagExtractor


def test_basic_functionality():
    """测试基本功能"""
    print("=== 基本功能测试 ===")
    extractor = StreamTagExtractor()

    # 模拟流式数据chunks
    test_chunks = [
        "Hello ",
        "<think>",
        "This is some thinking content",
        "</think>",
        " world!"
    ]

    outside_total = ""
    inside_total = ""

    for i, chunk in enumerate(test_chunks):
        outside, inside = extractor.extract_tag_content(chunk, "think")
        outside_total += outside
        inside_total += inside
        # print(f"Chunk {i+1}: '{chunk}'")
        # print(f"  Outside: '{outside}'")
        # print(f"  Inside: '{inside}'")
        # print()

    print(f"总标签外内容: '{outside_total}'")
    print(f"总标签内内容: '{inside_total}'")
    print()


def test_partial_tags():
    """测试标签被截断的情况"""
    print("=== 标签截断测试 ===")
    extractor = StreamTagExtractor()

    # 测试标签在chunk边界被截断的情况
    test_chunks = [
        "Some text <think>Thoughts ",
        "and more thoughts</think>",
        " ending text."
    ]

    outside_total = ""
    inside_total = ""

    for i, chunk in enumerate(test_chunks):
        outside, inside = extractor.extract_tag_content(chunk, "think")
        outside_total += outside
        inside_total += inside
        # print(f"Chunk {i+1}: '{chunk}'")
        # print(f"  Outside: '{outside}'")
        # print(f"  Inside: '{inside}'")
        # print()

    print(f"总标签外内容: '{outside_total}'")
    print(f"总标签内内容: '{inside_total}'")
    print()


def test_multiple_partial_tags():
    """测试多个标签被截断的情况"""
    print("=== 多个标签截断测试 ===")
    extractor = StreamTagExtractor()

    # 测试多个标签被截断的情况
    test_chunks = [
        "Start <think>Think ",
        "content</think> Middle ",
        "<think>Another thought",
        " content</think> End"
    ]

    outside_total = ""
    inside_total = ""

    for i, chunk in enumerate(test_chunks):
        outside, inside = extractor.extract_tag_content(chunk, "think")
        outside_total += outside
        inside_total += inside
        # print(f"Chunk {i+1}: '{chunk}'")
        # print(f"  Outside: '{outside}'")
        # print(f"  Inside: '{inside}'")
        # print()

    print(f"总标签外内容: '{outside_total}'")
    print(f"总标签内内容: '{inside_total}'")
    print()


def test_complex_partial_tags():
    """测试复杂的标签截断情况"""
    print("=== 复杂标签截断测试 ===")
    extractor = StreamTagExtractor()

    # 测试复杂的标签截断情况
    test_chunks = [
        "Before <thi",
        "nk>Inside content</th",
        "ink> After"
    ]

    outside_total = ""
    inside_total = ""

    for i, chunk in enumerate(test_chunks):
        outside, inside = extractor.extract_tag_content(chunk, "think")
        outside_total += outside
        inside_total += inside
        # print(f"Chunk {i+1}: '{chunk}'")
        # print(f"  Outside: '{outside}'")
        # print(f"  Inside: '{inside}'")
        # print()

    print(f"总标签外内容: '{outside_total}'")
    print(f"总标签内内容: '{inside_total}'")
    print()


def test_no_tags():
    """测试没有标签的情况"""
    print("=== 无标签测试 ===")
    extractor = StreamTagExtractor()

    # 测试没有标签的情况
    test_chunks = [
        "Just some text ",
        "without any tags ",
        "in these chunks."
    ]

    outside_total = ""
    inside_total = ""

    for i, chunk in enumerate(test_chunks):
        outside, inside = extractor.extract_tag_content(chunk, "think")
        outside_total += outside
        inside_total += inside
        # print(f"Chunk {i+1}: '{chunk}'")
        # print(f"  Outside: '{outside}'")
        # print(f"  Inside: '{inside}'")
        # print()

    print(f"总标签外内容: '{outside_total}'")
    print(f"总标签内内容: '{inside_total}'")
    print()


def test_custom1():
    """测试没有标签的情况"""
    print("=== 无标签测试 ===")
    extractor = StreamTagExtractor()

    # 测试没有标签的情况
    test_chunks = ["🤖 思考中", ".", "..", "...", "\n\n", "<think>", "用户", "尝试", "与", "我", "打招", "呼", "</think>", "\n\n", "你好", "！", "我", "是",
                   "AI", "助手", "，", "很", "高兴", "为", "您", "服务", "。", "\n\n", "请问", "有", "什么", "我", "可以", "帮", "助", "您", "的", "吗", "？", "\n\n", "[DONE]"]

    outside_total = ""
    inside_total = ""

    for i, chunk in enumerate(test_chunks):
        outside, inside = extractor.extract_tag_content(chunk, "think")
        outside_total += outside
        inside_total += inside
        # print(f"Chunk {i+1}: '{chunk}'")
        # print(f"  Outside: '{outside}'")
        # print(f"  Inside: '{inside}'")
        # print()

    # print(f"总标签外内容: '{outside_total}'")
    print(f"总标签内内容: '{inside_total}'")
    print()


def test_custom2():
    """测试没有标签的情况"""
    print("=== 无标签测试 ===")
    extractor = StreamTagExtractor()

    # 测试没有标签的情况
    test_chunks = ["🤖 思", "考中", ".", "..", "\n\n", "<think>用户", "尝试与", "我打", "招呼</think>", "\n\n",
                   "你好！我", "是AI", "助手", "，很高", "兴为您", "服务。", "\n\n", "请问有什", "么我可以", "帮助您的", "吗？", "\n\n", "[DONE]"]

    outside_total = ""
    inside_total = ""

    for i, chunk in enumerate(test_chunks):
        outside, inside = extractor.extract_tag_content(chunk, "think")
        outside_total += outside
        inside_total += inside
        # print(f"Chunk {i+1}: '{chunk}'")
        # print(f"  Outside: '{outside}'")
        # print(f"  Inside: '{inside}'")
        # print()

    # print(f"总标签外内容: '{outside_total}'")
    print(f"总标签内内容: '{inside_total}'")
    print()


def test_custom3():
    """测试没有标签的情况"""
    print("=== 无标签测试 ===")
    extractor = StreamTagExtractor()

    # 测试没有标签的情况
    test_chunks = ["🤖", "思考", "中.", ".", ".", "\n", "\n", "<think>", "用户尝", "试", "与我", "打招呼", "</think>", "\n\n", "你",
                   "好！", "我是", "AI助", "手，", "很高", "兴", "为您服", "务。", "\n", "\n", "请问有", "什么我", "可以帮", "助您的", "吗？", "\n\n", "[DONE]"]

    outside_total = ""
    inside_total = ""

    for i, chunk in enumerate(test_chunks):
        outside, inside = extractor.extract_tag_content(chunk, "think")
        outside_total += outside
        inside_total += inside
        # print(f"Chunk {i+1}: '{chunk}'")
        # print(f"  Outside: '{outside}'")
        # print(f"  Inside: '{inside}'")
        # print()

    # print(f"总标签外内容: '{outside_total}'")
    print(f"总标签内内容: '{inside_total}'")
    print()


def test_custom4():
    """测试没有标签的情况"""
    print("=== 无标签测试 ===")
    extractor = StreamTagExtractor()

    # 测试没有标签的情况
    test_chunks = ["🤖 思考中", ".", "..", "...", "\n\n", "<think", ">用户尝", "试与我", "打招呼<", "/think>", "\n\n", "你好", "！", "我", "是", "AI",
                   "助手", "，", "很", "高兴", "为", "您", "服务", "。", "\n\n", "请问", "有", "什么", "我", "可以", "帮", "助", "您", "的", "吗", "？", "\n\n", "[DONE]"]

    outside_total = ""
    inside_total = ""

    for i, chunk in enumerate(test_chunks):
        outside, inside = extractor.extract_tag_content(chunk, "think")
        outside_total += outside
        inside_total += inside
        # print(f"Chunk {i+1}: '{chunk}'")
        # print(f"  Outside: '{outside}'")
        # print(f"  Inside: '{inside}'")
        # print()

    # print(f"总标签外内容: '{outside_total}'")
    print(f"总标签内内容: '{inside_total}'")
    print()


def test_custom5():
    """测试没有标签的情况"""
    print("=== 无标签测试 ===")
    extractor = StreamTagExtractor()

    # 测试没有标签的情况
    test_chunks = ["🤖 思", "考", "中", ".", ".", ".", "\n", "\n", "<t", "hink", ">用", "户尝试", "与", "我", "打", "招呼<", "/th", "ink>", "\n\n",
                   "你", "好！", "我", "是A", "I助手", "，", "很高", "兴", "为您", "服务", "。", "\n", "\n", "请", "问有", "什么", "我可以", "帮助", "您的", "吗？", "\n\n", "[DONE]"]

    outside_total = ""
    inside_total = ""

    for i, chunk in enumerate(test_chunks):
        outside, inside = extractor.extract_tag_content(chunk, "think")
        outside_total += outside
        inside_total += inside
        # print(f"Chunk {i+1}: '{chunk}'")
        # print(f"  Outside: '{outside}'")
        # print(f"  Inside: '{inside}'")
        # print()

    # print(f"总标签外内容: '{outside_total}'")
    print(f"总标签内内容: '{inside_total}'")
    print()


def test_custom6():
    """测试没有标签的情况"""
    print("=== 无标签测试 ===")
    extractor = StreamTagExtractor()

    # 测试没有标签的情况
    test_chunks = ["🤖 思考中", "..", ".\n\n", "<", "think", ">", "用户", "尝试", "与", "我", "打", "招呼", "<", "/", "think", ">",
                   "\n\n", "你好！", "我是", "AI", "助手", "，", "很高兴", "为您", "服务。", "\n\n", "请问", "有什么", "我可以", "帮助您", "的吗？", "\n\n", "[DONE]"]

    outside_total = ""
    inside_total = ""

    for i, chunk in enumerate(test_chunks):
        outside, inside = extractor.extract_tag_content(chunk, "think")
        outside_total += outside
        inside_total += inside
        # print(f"Chunk {i+1}: '{chunk}'")
        # print(f"  Outside: '{outside}'")
        # print(f"  Inside: '{inside}'")
        # print()

    # print(f"总标签外内容: '{outside_total}'")
    print(f"总标签内内容: '{inside_total}'")
    print()


def test_custom7():
    """测试没有标签的情况"""
    print("=== 无标签测试 ===")
    extractor = StreamTagExtractor()

    # 测试没有标签的情况
    test_chunks = ["🤖 思考中", ".", "..", "...", "\n\n", "<think", ">用户尝", "试与我", "打招呼<", "/think>", "\n\n", "你好", "！", "我", "是", "AI",
                   "助手", "，", "很", "高兴", "为", "您", "服务", "。", "\n\n", "请问", "有", "什么", "我", "可以", "帮", "助", "您", "的", "吗", "？", "\n\n", "[DONE]"]

    outside_total = ""
    inside_total = ""

    for i, chunk in enumerate(test_chunks):
        outside, inside = extractor.extract_tag_content(chunk, "think")
        outside_total += outside
        inside_total += inside
        # print(f"Chunk {i+1}: '{chunk}'")
        # print(f"  Outside: '{outside}'")
        # print(f"  Inside: '{inside}'")
        # print()

    # print(f"总标签外内容: '{outside_total}'")
    print(f"总标签内内容: '{inside_total}'")
    print()


if __name__ == "__main__":
    test_basic_functionality()
    test_partial_tags()
    test_multiple_partial_tags()
    test_complex_partial_tags()
    test_no_tags()
    test_custom1()
    test_custom2()
    test_custom3()
    test_custom4()
    test_custom5()
    test_custom6()
    test_custom7()
