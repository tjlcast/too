
from datetime import datetime


def get_current_timestamp() -> str:
    """
    Get the current timestamp.

    Returns:
        Current timestamp as a string
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
