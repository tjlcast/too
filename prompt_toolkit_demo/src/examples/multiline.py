"""
Multi-line Input Example
========================

This example demonstrates how to handle multi-line input with prompt_toolkit.
"""

from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML


def run():
    """Run the multi-line input example."""
    print("=== Multi-line Input Example ===\n")

    # Simple multi-line input
    print("1. Simple multi-line input:")
    print("Press [Meta+Enter] or [Esc] followed by [Enter] to accept input.")
    text = prompt("Enter multi-line text: ", multiline=True)
    print(f"You entered:\n{text}\n")

    # Multi-line input with custom key bindings
    print("2. Multi-line input with custom key bindings:")

    bindings = KeyBindings()

    @bindings.add('c-c')
    def _(event):
        """Clear the current input."""
        event.app.current_buffer.reset()

    @bindings.add('c-s')
    def _(event):
        """Save and submit the current input."""
        event.app.exit(result=event.app.current_buffer.text)

    print("Available key bindings:")
    print("  [Enter]     - New line")
    print("  [Alt+Enter] - Submit")
    print("  Ctrl+C      - Clear input")
    print("  Ctrl+S      - Save and submit")
    print()

    try:
        text = prompt(
            HTML('<b>Enter your story:</b> '),
            multiline=True,
            key_bindings=bindings
        )
        print(f"Your story:\n{text}\n")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")

    # Multi-line with custom validator
    from prompt_toolkit.validation import Validator, ValidationError

    class PythonValidator(Validator):
        def validate(self, document):
            text = document.text
            if text and not text.endswith(':'):
                # Just a simple check for demo purposes
                if 'def ' in text and not text.strip().endswith(':'):
                    raise ValidationError(
                        message='Function definitions should end with a colon (:)',
                        cursor_position=len(text))

    print("3. Multi-line with Python code validation:")
    print("Try entering a function definition (should end with colon)")
    try:
        code = prompt(
            "Enter Python code: ",
            multiline=True,
            validator=PythonValidator()
        )
        print(f"You entered:\n{code}\n")
    except KeyboardInterrupt:
        print("\nOperation cancelled.")

    # Demonstrating a toggleable summary/full text view
    print("4. Toggleable summary/full text view:")
    print("Press 1 to toggle between summary and full text view, Ctrl+C to continue.")
    create_summary_app().run()

    input("Press Enter to continue...")

    create_summary_app().run()
    input("Press Enter to continue...")
    print("4. Toggleable summary/full text view:")


def create_summary_app():
    """Create an app that toggles between summary and full text view."""
    from prompt_toolkit import Application
    from prompt_toolkit.layout import Layout, Window, HSplit
    from prompt_toolkit.layout.controls import FormattedTextControl
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.widgets import Box, Frame

    # 多个内容块
    content_blocks = [
        "这是第一个很长的文本内容，需要被缩略显示，可以通过按1来切换完整显示和摘要显示...",
        "这是第二个内容块，它也包含很多信息，需要能够独立控制显示摘要还是全文...",
        "第三个内容块也有类似的需求，应该能够单独控制其显示模式..."
    ]

    # 每个块的显示模式（True表示摘要，False表示全文）
    show_summary = [True] * len(content_blocks)

    # 当前选中的块
    selected_block = 0

    def get_content():
        result = []
        for i, content in enumerate(content_blocks):
            # 添加块标识和选择指示器
            if i == selected_block:
                result.append(("class:selected", f"[块 {i+1}] "))
            else:
                result.append(("", f"[块 {i+1}] "))

            # 根据显示模式显示摘要或全文
            if show_summary[i] and len(content) > 20:
                summary = content[:17] + "..."
                result.append(("", f"概要: {summary}"))
            else:
                result.append(("", f"全文: {content}"))

            # 添加操作提示
            if i == selected_block:
                result.append(("", " (按 1 切换显示模式)"))

            # 添加换行
            result.append(("", "\n"))

        # 移除最后一个换行符
        if result:
            result.pop()
        return result

    content_control = FormattedTextControl(get_content)

    kb = KeyBindings()

    @kb.add('1')
    def _(event):
        """切换当前选中块的显示模式"""
        show_summary[selected_block] = not show_summary[selected_block]
        event.app.invalidate()

    @kb.add('up')
    def _(event):
        """选择上一个块"""
        nonlocal selected_block
        selected_block = (selected_block - 1) % len(content_blocks)
        event.app.invalidate()

    @kb.add('down')
    def _(event):
        """选择下一个块"""
        nonlocal selected_block
        selected_block = (selected_block + 1) % len(content_blocks)
        event.app.invalidate()

    @kb.add('c-c')
    def _(event):
        event.app.exit()

    # 创建带框图的布局，类似于create_radio_selection
    body = HSplit([
        Window(FormattedTextControl("多块文本显示切换演示"), height=1),
        Frame(Box(Window(content=content_control,
              height=len(content_blocks)), padding=1)),
        Window(
            FormattedTextControl(
                HTML(
                    "Press <b>1</b> to toggle view, <b>↑/↓</b> to select block, <b>Ctrl+C</b> to continue.")
            ),
            height=1
        )
    ])

    # 添加样式
    from prompt_toolkit.styles import Style
    style = Style.from_dict({
        "selected": "#ffffff bg:#444444"
    })

    layout = Layout(body)

    app = Application(
        layout=layout,
        key_bindings=kb,
        full_screen=False,
        style=style
    )

    return app
