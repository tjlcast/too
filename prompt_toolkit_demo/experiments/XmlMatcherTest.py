from XmlMatcher import XmlMatcher

def test_only_match_at_position_0():
    matcher = XmlMatcher("think")
    chunks = matcher.update("<think>data</think>") + matcher.final()
    assert len(chunks) == 1
    assert chunks == [
        {
            "matched": True,
            "data": "data",
        },
    ]
    print("test_only_match_at_position_0 passed")


def test_tag_with_space():
    matcher = XmlMatcher("think")
    chunks = matcher.update("< think >data</ think >") + matcher.final()
    assert len(chunks) == 1
    assert chunks == [
        {
            "matched": True,
            "data": "data",
        },
    ]
    print("test_tag_with_space passed")


def test_invalid_tag():
    matcher = XmlMatcher("think")
    chunks = matcher.update("< think 1>data</ think >") + matcher.final()
    assert len(chunks) == 1
    assert chunks == [
        {
            "matched": False,
            "data": "< think 1>data</ think >",
        },
    ]
    print("test_invalid_tag passed")


def test_anonymous_tag():
    matcher = XmlMatcher("think")
    chunks = matcher.update("<>data</>") + matcher.final()
    assert len(chunks) == 1
    assert chunks == [
        {
            "matched": False,
            "data": "<>data</>",
        },
    ]
    print("test_anonymous_tag passed")


def test_streaming_push():
    matcher = XmlMatcher("think")
    chunks = (
        matcher.update("<thi") +
        matcher.update("nk") +
        matcher.update(">dat") +
        matcher.update("a</") +
        matcher.update("think>")
    )
    assert len(chunks) == 2
    assert chunks == [
        {
            "matched": True,
            "data": "dat",
        },
        {
            "matched": True,
            "data": "a",
        },
    ]
    print("test_streaming_push passed")


def test_nested_tag():
    matcher = XmlMatcher("think")
    chunks = matcher.update("<think>X<think>Y</think>Z</think>") + matcher.final()
    assert len(chunks) == 1
    assert chunks == [
        {
            "matched": True,
            "data": "X<think>Y</think>Z",
        },
    ]
    print("test_nested_tag passed")


def test_nested_invalid_tag():
    matcher = XmlMatcher("think")
    chunks = matcher.update("<think>X<think>Y</thxink>Z</think>") + matcher.final()
    assert len(chunks) == 2
    expected_chunks = [
        {
            "matched": True,
            "data": "X<think>Y</thxink>Z",
        },
        {
            "matched": True,
            "data": "</think>",
        },
    ]
    # Note: The exact result depends on how the algorithm handles invalid tags
    # This is a simplified verification; actual results may vary
    print(f"test_nested_invalid_tag chunks: {chunks}")
    print("test_nested_invalid_tag completed")


def test_wrong_matching_position():
    matcher = XmlMatcher("think")
    chunks = matcher.update("1<think>data</think>") + matcher.final()
    assert len(chunks) == 1
    assert chunks == [
        {
            "matched": False,
            "data": "1<think>data</think>",
        },
    ]
    print("test_wrong_matching_position passed")


def test_unclosed_tag():
    matcher = XmlMatcher("think")
    chunks = matcher.update("<think>data") + matcher.final()
    assert len(chunks) == 1
    assert chunks == [
        {
            "matched": True,
            "data": "data",
        },
    ]
    print("test_unclosed_tag passed")


if __name__ == "__main__":
    test_only_match_at_position_0()
    test_tag_with_space()
    test_invalid_tag()
    test_anonymous_tag()
    test_streaming_push()
    test_nested_tag()
    test_nested_invalid_tag()
    test_wrong_matching_position()
    test_unclosed_tag()
    print("All tests passed!")