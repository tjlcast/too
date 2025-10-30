"""
Progress Bars Example
=====================

This example demonstrates how to use progress bars in prompt_toolkit.
"""

import sys
import time
import threading
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import ProgressBar
from prompt_toolkit.formatted_text import HTML


def run():
    """Run the progress bars example."""
    print("=== Progress Bars Example ===\\n")

    # Simple progress bar
    print("1. Simple progress bar:")
    with ProgressBar() as pb:
        for i in pb(range(100)):
            time.sleep(0.01)  # Simulate work

    print("\\nDone!\\n")

    # Progress bar with custom title
    print("2. Progress bar with custom title:")
    with ProgressBar(title='Processing items') as pb:
        for i in pb(range(50), label='Items'):
            time.sleep(0.05)  # Simulate work

    print("\\nDone!\\n")

    # Multiple parallel tasks
    print("3. Multiple parallel tasks:")

    def task_1(progress_iterator):
        for i in progress_iterator:
            time.sleep(0.02)

    def task_2(progress_iterator):
        for i in progress_iterator:
            time.sleep(0.01)

    with ProgressBar() as pb:
        pb1 = pb(range(100), label='Task 1')
        pb2 = pb(range(150), label='Task 2')

        # Run both tasks in parallel
        t1 = threading.Thread(target=task_1, args=(pb1,))
        t2 = threading.Thread(target=task_2, args=(pb2,))

        t1.start()
        t2.start()

        t1.join()
        t2.join()

    print("\\nAll tasks completed!\\n")

    # Progress bar with custom formatting
    print("4. Progress bar with custom formatting:")

    def get_title():
        return HTML('<b>Processing...</b>')

    with ProgressBar(title=get_title) as pb:
        for i in pb(range(80)):
            time.sleep(0.05)

    print("\\nDone!\\n")

    # Manual loading animation using yaspin
    print("5. Manual loading animation:")
    print("Starting loading animation... Press Enter to stop.")

    try:
        from yaspin import yaspin

        spinner = yaspin(text="Loading")
        spinner.start()

        # Wait for user input to stop
        input()
        spinner.stop()

        print("Loading animation stopped!\\n")
    except ImportError:
        print("yaspin library not installed. To see the spinner, please install it with: pip install yaspin\\n")
        input("Press Enter to continue...")

    Spinner = cross_platform_spinner()
    spinner = Spinner("Processing...", style='simple')
    spinner.start()
    # 使用prompt_toolkit获取输入
    try:
        user_input = prompt("Press Enter to stop: ")
    finally:
        spinner.stop()

    print(f"\nCompleted! You entered: {user_input}")
    input("Press Enter to continue...")


def cross_platform_spinner():
    """在多系统上兼容的spinner"""
    spinner_chars = {
        'universal': ['|', '/', '-', '\\'],
        'dots': ['.', '..', '...', '....'],
        'simple': ['●○○', '○●○', '○○●', '○●○']
    }

    current_chars = spinner_chars['universal']

    class Spinner:
        def __init__(self, text="Loading", style='universal'):
            self.text = text
            self.is_running = False
            self.thread = None
            if style in spinner_chars:
                nonlocal current_chars
                current_chars = spinner_chars[style]

        def spin(self):
            i = 0
            while self.is_running:
                sys.stdout.write(f'\r{current_chars[i]} {self.text}')
                sys.stdout.flush()
                i = (i + 1) % len(current_chars)
                time.sleep(0.2)

        def start(self):
            self.is_running = True
            self.thread = threading.Thread(target=self.spin)
            self.thread.start()

        def stop(self):
            self.is_running = False
            if self.thread:
                self.thread.join()
            sys.stdout.write('\r' + ' ' * 50 + '\r')  # 清空行

    return Spinner
