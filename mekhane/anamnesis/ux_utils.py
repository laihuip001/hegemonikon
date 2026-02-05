"""
UX Utilities for CLI output.
Provides standardized colors and semantic print functions.
"""

import sys

try:
    from termcolor import cprint, colored
except ImportError:
    # Fallback if termcolor is not installed
    def cprint(text, color=None, on_color=None, attrs=None, **kwargs):
        print(text, **kwargs)

    def colored(text, color=None, on_color=None, attrs=None):
        return text


def print_success(msg: str):
    """Print a success message (green)."""
    cprint(f"✅ {msg}", "green")


def print_error(msg: str):
    """Print an error message (red)."""
    cprint(f"❌ {msg}", "red")


def print_warning(msg: str):
    """Print a warning message (yellow)."""
    cprint(f"⚠️  {msg}", "yellow")


def print_info(msg: str):
    """Print an info message (cyan)."""
    cprint(f"ℹ️  {msg}", "cyan")


def print_header(msg: str):
    """Print a header message (bold/underline)."""
    cprint(f"\n{msg}", attrs=["bold", "underline"])


def colorize_usage(text: str) -> str:
    """Colorize usage statistics (e.g. 50% -> yellow)."""
    # Simple heuristic helper for stats
    return colored(text, "cyan")
