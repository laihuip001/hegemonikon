"""
UX Utilities for CLI applications.
"""
import sys

try:
    from termcolor import colored
except ImportError:
    # Fallback if termcolor is not installed
    def colored(text, color=None, on_color=None, attrs=None):
        return text


def print_header(text: str):
    """Prints a styled header."""
    print(colored(f"\n[{text}]", "cyan", attrs=["bold"]))


def print_success(text: str):
    """Prints a success message."""
    print(colored(f"✓ {text}", "green"))


def print_error(text: str):
    """Prints an error message."""
    print(colored(f"✗ {text}", "red"), file=sys.stderr)


def print_warning(text: str):
    """Prints a warning message."""
    print(colored(f"⚠ {text}", "yellow"))


def print_info(text: str, label: str = ""):
    """Prints an info message."""
    prefix = f"{label}: " if label else ""
    print(colored(f"ℹ {prefix}{text}", "blue"))


def colorize_usage(current: int, limit: int) -> str:
    """Returns a colorized usage string."""
    if limit == 0:
        return f"{current:,} / 0"

    percentage = (current / limit) * 100
    text = f"{current:,} / {limit:,} ({percentage:.1f}%)"
    if percentage > 90:
        return colored(text, "red")
    elif percentage > 70:
        return colored(text, "yellow")
    return colored(text, "green")
