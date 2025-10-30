"""
Progress Bars Example
=====================

This example demonstrates how to use progress bars in prompt_toolkit.
"""

import time
import threading
from prompt_toolkit.shortcuts import ProgressBar
from prompt_toolkit.formatted_text import HTML


def run():
    """Run the progress bars example."""
    print("=== Progress Bars Example ===\n")

    # Simple progress bar
    print("1. Simple progress bar:")
    with ProgressBar() as pb:
        for i in pb(range(100)):
            time.sleep(0.01)  # Simulate work

    print("\nDone!\n")

    # Progress bar with custom title
    print("2. Progress bar with custom title:")
    with ProgressBar(title='Processing items') as pb:
        for i in pb(range(50), label='Items'):
            time.sleep(0.05)  # Simulate work

    print("\nDone!\n")

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

    print("\nAll tasks completed!\n")

    # Progress bar with custom formatting
    print("4. Progress bar with custom formatting:")

    def get_title():
        return HTML('<b>Processing...</b>')

    with ProgressBar(title=get_title) as pb:
        for i in pb(range(80)):
            time.sleep(0.05)

    print("\nDone!\n")

    input("Press Enter to continue...")