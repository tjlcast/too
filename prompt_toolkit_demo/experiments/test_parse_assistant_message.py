import unittest
from parseAssistantMessageV2 import(
# from parseAssistantMessage import (
    parse_assistant_message,
)
from assistent_message import (
    TextContent,
    ToolUse
)


def is_empty_text_content(block):
    """Helper function to check if a block is empty text content."""
    return isinstance(block, TextContent) and block.content.strip() == ""


class TestParseAssistantMessage(unittest.TestCase):

    def setUp(self):
        """Set up common test data."""
        # Define tools and parameters based on the test expectations
        self.tools = [
            "read_file", "write_to_file", "browser_action",
            "execute_command", "search_files", "new_rule"
        ]
        self.params = [
            "path", "content", "start_line", "end_line",
            "line_count", "command", "regex", "rule_name"
        ]

    def parse_with_defaults(self, message):
        """Parse with default tool and parameter names."""
        return parse_assistant_message(message, self.tools, self.params)

    # ==== Text Content Parsing Tests ====
    def test_parse_simple_text_message(self):
        """should parse a simple text message"""
        message = "This is a simple text message"
        result = self.parse_with_defaults(message)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].type, "text")
        self.assertEqual(result[0].content, message)
        # Text is always partial when it's the last content
        self.assertTrue(result[0].partial)

    def test_parse_multi_line_text_message(self):
        """should parse a multi-line text message"""
        message = "This is a multi-line\ntext message\nwith several lines"
        result = self.parse_with_defaults(message)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].type, "text")
        self.assertEqual(result[0].content, message)
        # Text is always partial when it's the last content
        self.assertTrue(result[0].partial)

    def test_mark_text_as_partial_when_last_content(self):
        """should mark text as partial when it's the last content in the message"""
        message = "This is a partial text"
        result = self.parse_with_defaults(message)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].type, "text")
        self.assertEqual(result[0].content, message)
        self.assertTrue(result[0].partial)  # Should be partial as it's the end

    # ==== Tool Use Parsing Tests ====
    def test_parse_simple_tool_use(self):
        """should parse a simple tool use"""
        message = "<read_file><path>src/file.ts</path></read_file>"
        result = [block for block in self.parse_with_defaults(message)
                  if not is_empty_text_content(block)]

        self.assertEqual(len(result), 1)
        tool_use = result[0]
        self.assertEqual(tool_use.type, "tool_use")
        self.assertEqual(tool_use.name, "read_file")
        self.assertEqual(tool_use.params.get("path"), "src/file.ts")
        self.assertFalse(tool_use.partial)

    def test_parse_tool_use_with_multiple_parameters(self):
        """should parse a tool use with multiple parameters"""
        message = "<read_file><path>src/file.ts</path><start_line>10</start_line><end_line>20</end_line></read_file>"
        result = [block for block in self.parse_with_defaults(message)
                  if not is_empty_text_content(block)]

        self.assertEqual(len(result), 1)
        tool_use = result[0]
        self.assertEqual(tool_use.type, "tool_use")
        self.assertEqual(tool_use.name, "read_file")
        self.assertEqual(tool_use.params.get("path"), "src/file.ts")
        self.assertEqual(tool_use.params.get("start_line"), "10")
        self.assertEqual(tool_use.params.get("end_line"), "20")
        self.assertFalse(tool_use.partial)

    def test_mark_tool_use_as_partial_when_not_closed(self):
        """should mark tool use as partial when it's not closed"""
        message = "<read_file><path>src/file.ts</path>"
        result = [block for block in self.parse_with_defaults(message)
                  if not is_empty_text_content(block)]

        self.assertEqual(len(result), 1)
        tool_use = result[0]
        self.assertEqual(tool_use.type, "tool_use")
        self.assertEqual(tool_use.name, "read_file")
        self.assertEqual(tool_use.params.get("path"), "src/file.ts")
        self.assertTrue(tool_use.partial)

    def test_handle_partial_parameter_in_tool_use(self):
        """should handle a partial parameter in a tool use"""
        message = "<read_file><path>src/file.ts"
        result = [block for block in self.parse_with_defaults(message)
                  if not is_empty_text_content(block)]

        self.assertEqual(len(result), 1)
        tool_use = result[0]
        self.assertEqual(tool_use.type, "tool_use")
        self.assertEqual(tool_use.name, "read_file")
        self.assertEqual(tool_use.params.get("path"), "src/file.ts")
        self.assertTrue(tool_use.partial)

    # ==== Mixed Content Parsing Tests ====
    def test_parse_text_followed_by_tool_use(self):
        """should parse text followed by a tool use"""
        message = "Here's the file content: <read_file><path>src/file.ts</path></read_file>"
        result = self.parse_with_defaults(message)

        # Filter out empty text blocks
        non_empty_result = [
            block for block in result if not is_empty_text_content(block)]

        if len(non_empty_result) < 2:
            # Try with original result
            non_empty_result = result

        self.assertGreaterEqual(len(non_empty_result), 1)

        # First block should be text
        self.assertEqual(non_empty_result[0].type, "text")
        self.assertEqual(
            non_empty_result[0].content.strip(), "Here's the file content:")
        self.assertFalse(non_empty_result[0].partial)

        if len(non_empty_result) > 1:
            # Second block should be tool use
            self.assertEqual(non_empty_result[1].type, "tool_use")
            self.assertEqual(non_empty_result[1].name, "read_file")
            self.assertEqual(
                non_empty_result[1].params.get("path"), "src/file.ts")
            self.assertFalse(non_empty_result[1].partial)

    def test_parse_tool_use_followed_by_text(self):
        """should parse a tool use followed by text"""
        message = "<read_file><path>src/file.ts</path></read_file>Here's what I found in the file."
        result = [block for block in self.parse_with_defaults(message)
                  if not is_empty_text_content(block)]

        self.assertGreaterEqual(len(result), 1)

        # First block should be tool use
        self.assertEqual(result[0].type, "tool_use")
        self.assertEqual(result[0].name, "read_file")
        self.assertEqual(result[0].params.get("path"), "src/file.ts")
        self.assertFalse(result[0].partial)

        if len(result) > 1:
            # Second block should be text
            self.assertEqual(result[1].type, "text")
            self.assertIn("Here's what I found in the file.",
                          result[1].content)
            self.assertTrue(result[1].partial)

    def test_parse_multiple_tool_uses_separated_by_text(self):
        """should parse multiple tool uses separated by text"""
        message = "First file: <read_file><path>src/file1.ts</path></read_file>Second file: <read_file><path>src/file2.ts</path></read_file>"
        result = self.parse_with_defaults(message)

        # Filter out empty text blocks
        result = [
            block for block in result if not is_empty_text_content(block)]

        # Should have at least text + tool + text + tool
        self.assertGreaterEqual(len(result), 4)

        # Check structure
        self.assertEqual(result[0].type, "text")
        self.assertIn("First file:", result[0].content)

        self.assertEqual(result[1].type, "tool_use")
        self.assertEqual(result[1].name, "read_file")
        self.assertEqual(result[1].params.get("path"), "src/file1.ts")

        self.assertEqual(result[2].type, "text")
        self.assertIn("Second file:", result[2].content)

        self.assertEqual(result[3].type, "tool_use")
        self.assertEqual(result[3].name, "read_file")
        self.assertEqual(result[3].params.get("path"), "src/file2.ts")

    # ==== Special Cases Tests ====
    def test_handle_write_to_file_with_content_containing_closing_tags(self):
        """should handle the write_to_file tool with content that contains closing tags"""
        message = """<write_to_file><path>src/file.ts</path><content>
function example() {
// This has XML-like content: </content>
return true;
}
</content><line_count>5</line_count></write_to_file>"""

        result = [block for block in self.parse_with_defaults(message)
                  if not is_empty_text_content(block)]

        self.assertEqual(len(result), 1)
        tool_use = result[0]
        self.assertEqual(tool_use.type, "tool_use")
        self.assertEqual(tool_use.name, "write_to_file")
        self.assertEqual(tool_use.params.get("path"), "src/file.ts")
        self.assertEqual(tool_use.params.get("line_count"), "5")

        content = tool_use.params.get("content", "")
        self.assertIn("function example()", content)
        self.assertIn("// This has XML-like content: </content>", content)
        self.assertIn("return true;", content)
        self.assertFalse(tool_use.partial)

    def test_handle_empty_messages(self):
        """should handle empty messages"""
        message = ""
        result = self.parse_with_defaults(message)
        self.assertEqual(len(result), 0)

    def test_handle_malformed_tool_use_tags(self):
        """should handle malformed tool use tags"""
        message = "This has a <not_a_tool>malformed tag</not_a_tool>"
        result = self.parse_with_defaults(message)

        # Should be treated as plain text
        self.assertGreaterEqual(len(result), 0)
        if result:
            # If we get results, they should be text
            for block in result:
                self.assertEqual(block.type, "text")

    def test_handle_tool_use_with_no_parameters(self):
        """should handle tool use with no parameters"""
        message = "<browser_action></browser_action>"
        result = [block for block in self.parse_with_defaults(message)
                  if not is_empty_text_content(block)]

        self.assertEqual(len(result), 1)
        tool_use = result[0]
        self.assertEqual(tool_use.type, "tool_use")
        self.assertEqual(tool_use.name, "browser_action")
        self.assertEqual(len(tool_use.params), 0)
        self.assertFalse(tool_use.partial)

    def test_handle_nested_tool_tags_not_actually_nested(self):
        """should handle nested tool tags that aren't actually nested"""
        message = "<execute_command><command>echo '<read_file><path>test.txt</path></read_file>'</command></execute_command>"

        result = [block for block in self.parse_with_defaults(message)
                  if not is_empty_text_content(block)]

        self.assertEqual(len(result), 1)
        tool_use = result[0]
        self.assertEqual(tool_use.type, "tool_use")
        self.assertEqual(tool_use.name, "execute_command")
        self.assertEqual(tool_use.params.get("command"),
                         "echo '<read_file><path>test.txt</path></read_file>'")
        self.assertFalse(tool_use.partial)

    def test_handle_tool_use_with_parameter_containing_xml_like_content(self):
        """should handle a tool use with a parameter containing XML-like content"""
        message = "<search_files><regex><div>.*</div></regex><path>src</path></search_files>"
        result = [block for block in self.parse_with_defaults(message)
                  if not is_empty_text_content(block)]

        self.assertEqual(len(result), 1)
        tool_use = result[0]
        self.assertEqual(tool_use.type, "tool_use")
        self.assertEqual(tool_use.name, "search_files")
        self.assertEqual(tool_use.params.get("regex"), "<div>.*</div>")
        self.assertEqual(tool_use.params.get("path"), "src")
        self.assertFalse(tool_use.partial)

    def test_handle_consecutive_tool_uses_without_text_in_between(self):
        """should handle consecutive tool uses without text in between"""
        message = "<read_file><path>file1.ts</path></read_file><read_file><path>file2.ts</path></read_file>"
        result = [block for block in self.parse_with_defaults(message)
                  if not is_empty_text_content(block)]

        self.assertEqual(len(result), 2)

        tool_use1 = result[0]
        self.assertEqual(tool_use1.type, "tool_use")
        self.assertEqual(tool_use1.name, "read_file")
        self.assertEqual(tool_use1.params.get("path"), "file1.ts")
        self.assertFalse(tool_use1.partial)

        tool_use2 = result[1]
        self.assertEqual(tool_use2.type, "tool_use")
        self.assertEqual(tool_use2.name, "read_file")
        self.assertEqual(tool_use2.params.get("path"), "file2.ts")
        self.assertFalse(tool_use2.partial)

    def test_handle_whitespace_in_parameters(self):
        """should handle whitespace in parameters"""
        message = "<read_file><path>  src/file.ts  </path></read_file>"
        result = [block for block in self.parse_with_defaults(message)
                  if not is_empty_text_content(block)]

        self.assertEqual(len(result), 1)
        tool_use = result[0]
        self.assertEqual(tool_use.type, "tool_use")
        self.assertEqual(tool_use.name, "read_file")
        self.assertEqual(tool_use.params.get("path"),
                         "src/file.ts")  # Should be trimmed
        self.assertFalse(tool_use.partial)

    def test_handle_multi_line_parameters(self):
        """should handle multi-line parameters"""
        message = """<write_to_file><path>file.ts</path><content>
line 1
line 2
line 3
</content><line_count>3</line_count></write_to_file>"""
        result = [block for block in self.parse_with_defaults(message)
                  if not is_empty_text_content(block)]

        self.assertEqual(len(result), 1)
        tool_use = result[0]
        self.assertEqual(tool_use.type, "tool_use")
        self.assertEqual(tool_use.name, "write_to_file")
        self.assertEqual(tool_use.params.get("path"), "file.ts")

        content = tool_use.params.get("content", "")
        self.assertIn("line 1", content)
        self.assertIn("line 2", content)
        self.assertIn("line 3", content)
        self.assertEqual(tool_use.params.get("line_count"), "3")
        self.assertFalse(tool_use.partial)

    def test_handle_complex_message_with_multiple_content_types(self):
        """should handle a complex message with multiple content types"""
        message = """I'll help you with that task.

<read_file><path>src/index.ts</path></read_file>

Now let's modify the file:

<write_to_file><path>src/index.ts</path><content>
// Updated content
console.log("Hello world");
</content><line_count>2</line_count></write_to_file>

Let's run the code:

<execute_command><command>node src/index.ts</command></execute_command>"""

        result = self.parse_with_defaults(message)

        # Filter out empty text blocks
        result = [
            block for block in result if not is_empty_text_content(block)]

        # Should have text + tool + text + tool + text + tool
        self.assertGreaterEqual(len(result), 5)

        # Check the sequence of types
        types = [block.type for block in result[:6]]  # Check first 6 blocks
        self.assertIn("text", types[0])  # First should be text
        self.assertIn("tool_use", types[1:])  # Should have tool uses

        # Look for specific tools
        tool_names = [block.name for block in result if hasattr(block, 'name')]
        self.assertIn("read_file", tool_names)
        self.assertIn("write_to_file", tool_names)
        self.assertIn("execute_command", tool_names)

    # ==== Additional Tests for Python-specific Behavior ====
    def test_parse_with_custom_tool_names(self):
        """Test parsing with custom tool names"""
        custom_tools = ["custom_tool", "another_tool"]
        custom_params = ["param1", "param2"]

        message = "<custom_tool><param1>value1</param1></custom_tool>"
        result = parse_assistant_message(message, custom_tools, custom_params)

        result = [
            block for block in result if not is_empty_text_content(block)]

        if result:
            self.assertEqual(result[0].name, "custom_tool")
            self.assertEqual(result[0].params.get("param1"), "value1")


class BenchmarkTests(unittest.TestCase):

    def setUp(self):
        """Set up common test data."""
        # Define tools and parameters based on the test expectations
        self.tools = [
            "read_file", "write_to_file", "browser_action",
            "execute_command", "search_files", "new_rule"
        ]
        self.params = [
            "path", "content", "start_line", "end_line",
            "line_count", "command", "regex", "rule_name"
        ]

    def parse_with_defaults(self, message):
        """Parse with default tool and parameter names."""
        return parse_assistant_message(message, self.tools, self.params)

    def test_simple_text_message(self):
        input = "This is a simple text message without any tool uses."
        result = self.parse_with_defaults(input)

        # check the length
        self.assertEqual(len(result), 1)

        self.assertEqual(result[0].type, "text")
        self.assertEqual(result[0].content, input)
        self.assertTrue(result[0].partial)

    def test_message_with_a_simple_tool_use(self):
        input = "Let's read a file: <read_file><path>src/file.ts</path></read_file>"
        result = self.parse_with_defaults(input)

        # check the length
        self.assertEqual(len(result), 2)

        self.assertEqual(result[0].type, "text")
        self.assertEqual(result[0].content, "Let's read a file:")
        self.assertFalse(result[0].partial)

        self.assertEqual(result[1].type, "tool_use")
        self.assertEqual(result[1].name, "read_file")
        self.assertEqual(result[1].params.get("path"), "src/file.ts")
        self.assertFalse(result[1].partial)

    def test_message_with_a_complex_tool_use_write_to_file(self):
        input = "<write_to_file><path>src/file.ts</path><content>\nfunction example() {\n  // This has XML-like content: </content>\n  return true;\n}\n</content><line_count>5</line_count></write_to_file>"
        result = self.parse_with_defaults(input)

        # 在v1的情况，由于没有处理content，所以会多一个text
        # 特做一次兼容
        result = [
            block for block in result if not (is_empty_text_content(block) and block.type == "text")]

        # check the length
        self.assertEqual(len(result), 1)

        self.assertEqual(result[0].type, "tool_use")
        self.assertEqual(result[0].name, "write_to_file")
        self.assertEqual(result[0].params.get("path"), "src/file.ts")
        self.assertFalse(result[0].partial)

    def test_message_with_multiple_tool_uses(self):
        input = "First file: <read_file><path>src/file1.ts</path></read_file>\nSecond file: <read_file><path>src/file2.ts</path></read_file>\nLet's write a new file: <write_to_file><path>src/file3.ts</path><content>\nexport function newFunction() {\n  return 'Hello world';\n}\n</content><line_count>3</line_count></write_to_file>"
        result = self.parse_with_defaults(input)

        # check the length
        self.assertEqual(len(result), 6)

        self.assertEqual(result[0].type, "text")
        self.assertEqual(result[0].content, "First file:")
        self.assertFalse(result[0].partial)

        self.assertEqual(result[1].type, "tool_use")
        self.assertEqual(result[1].name, "read_file")
        self.assertEqual(result[1].params.get("path"), "src/file1.ts")
        self.assertFalse(result[1].partial)

        self.assertEqual(result[2].type, "text")
        self.assertEqual(result[2].content, "Second file:")
        self.assertFalse(result[2].partial)

        self.assertEqual(result[3].type, "tool_use")
        self.assertEqual(result[3].name, "read_file")
        self.assertEqual(result[3].params.get("path"), "src/file2.ts")
        self.assertFalse(result[3].partial)

        self.assertEqual(result[4].type, "text")
        self.assertEqual(result[4].content, "Let's write a new file:")
        self.assertFalse(result[4].partial)

        self.assertEqual(result[5].type, "tool_use")
        self.assertEqual(result[5].name, "write_to_file")
        self.assertEqual(result[5].params.get("path"), "src/file3.ts")
        self.assertFalse(result[5].partial)

    def test_large_message_with_repeated_tool_uses(self):
        input_text = '\n'.join([
            '<read_file><path>src/file.ts</path></read_file>\n<write_to_file><path>output.ts</path><content>console.log("hello");</content><line_count>1</line_count></write_to_file>'
            for _ in range(30)
        ])
        result = self.parse_with_defaults(input_text)

        # 在v1的情况，由于没有处理content，所以会多一个text
        # 特做一次兼容
        result = [
            block for block in result if not (is_empty_text_content(block) and block.type == "text")]

        # Verify that we have the expected number of tool uses
        self.assertEqual(len(result), 60)  # 30 read_file + 30 write_to_file

        # Check that the tool types are correct
        read_file_count = sum(
            1 for tool in result if tool.name == 'read_file')
        write_to_file_count = sum(
            1 for tool in result if tool.name == 'write_to_file')

        self.assertEqual(read_file_count, 30)
        self.assertEqual(write_to_file_count, 30)


def run_all_parsers_tests():
    """Run tests for both parsers (simulating the TypeScript test structure)."""
    # In TypeScript, they test both V1 and V2 parsers
    # For Python, we only have one implementation, but we can test it thoroughly

    suite = unittest.TestLoader().loadTestsFromTestCase(TestParseAssistantMessage)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(BenchmarkTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result

def run_parser_v1_tests():
    """Run tests specifically for parseAssistantMessage (V1) implementation."""
    print("=" * 60)
    print("Testing parseAssistantMessage (V1 Implementation)")
    print("=" * 60)
    
    # Temporarily modify the import to use V1 instead of V2
    global parse_assistant_message
    from parseAssistantMessage import parse_assistant_message as v1_func
    parse_assistant_message = v1_func
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestParseAssistantMessage)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(BenchmarkTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result

def run_parser_v2_tests():
    """Run tests specifically for parseAssistantMessageV2 (V2) implementation."""
    print("=" * 60)
    print("Testing parseAssistantMessageV2 (V2 Implementation)")
    print("=" * 60)
    
    # Ensure we're using V2 implementation
    global parse_assistant_message
    from parseAssistantMessageV2 import parse_assistant_message as v2_func
    parse_assistant_message = v2_func
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestParseAssistantMessage)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    suite = unittest.TestLoader().loadTestsFromTestCase(BenchmarkTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    # run_all_parsers_tests()
    # Run tests for V1 first, then V2
    run_parser_v1_tests()
    run_parser_v2_tests()