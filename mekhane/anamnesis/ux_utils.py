"""
UX Utilities for CLI applications.
Provides standardized colors and semantic print functions.
"""

from typing import Optional

try:
    from termcolor import colored, cprint
except ImportError:
    # Fallback if termcolor is not installed
    def colored(text: str, color: Optional[str] = None, **kwargs) -> str:
        return text

    def cprint(text: str, color: Optional[str] = None, **kwargs) -> None:
        print(text)


# Symbols
CHECK = "✓"
CROSS = "✗"
WARN = "⚠"
INFO = "ℹ"

# Standard Colors
SUCCESS_COLOR = "green"
ERROR_COLOR = "red"
WARNING_COLOR = "yellow"
INFO_COLOR = "cyan"


def print_success(message: str, label: str = "SUCCESS"):
    """Print a success message with a checkmark."""
    cprint(f"{colored(CHECK, SUCCESS_COLOR)} [{label}] {message}", SUCCESS_COLOR)


def print_error(message: str, label: str = "ERROR"):
    """Print an error message with a cross."""
    cprint(
        f"{colored(CROSS, ERROR_COLOR)} [{label}] {message}",
        ERROR_COLOR,
        attrs=["bold"],
    )


def print_warning(message: str, label: str = "WARNING"):
    """Print a warning message with a warning symbol."""
    cprint(f"{colored(WARN, WARNING_COLOR)} [{label}] {message}", WARNING_COLOR)


def print_info(message: str, label: str = "INFO"):
    """Print an info message."""
    cprint(f"{colored(INFO, INFO_COLOR)} [{label}] {message}", INFO_COLOR)


def colorize_usage(current: int, limit: int) -> str:
    """Colorize usage percentage."""
    if limit == 0:
        return f"{current}/{limit}"

    percentage = (current / limit) * 100
    text = f"{current:,} / {limit:,} ({percentage:.1f}%)"

    if percentage < 50:
        return colored(text, "green")
    elif percentage < 80:
        return colored(text, "yellow")
    else:
        return colored(text, "red", attrs=["bold"])


def print_header(title: str):
    """Print a styled header."""
    print()
    cprint(f"=== {title} ===", "blue", attrs=["bold"])
    print()
