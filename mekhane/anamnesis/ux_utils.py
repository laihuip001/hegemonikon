"""
Palette: UX Utilities for CLI
Provides standardized colors and semantic print functions.
"""

import sys
from typing import Optional

try:
    from termcolor import cprint as _cprint, colored
except ImportError:
    # Fallback if termcolor is not installed
    def _cprint(text, color=None, on_color=None, attrs=None, **kwargs):
        print(text, **kwargs)

    def colored(text, color=None, on_color=None, attrs=None):
        return text


def cprint(text: str, color: Optional[str] = None, **kwargs):
    """Wrapper around termcolor.cprint"""
    _cprint(text, color=color, **kwargs)


def print_header(text: str):
    """Prints a header in cyan, bold, with underline"""
    print()  # Add spacing before header
    _cprint(text, "cyan", attrs=["bold"])
    _cprint("-" * len(text), "cyan")


def print_success(text: str):
    """Prints success message with green checkmark"""
    _cprint(f"✓ {text}", "green")


def print_error(text: str):
    """Prints error message with red cross"""
    _cprint(f"✗ {text}", "red", attrs=["bold"])


def print_warning(text: str):
    """Prints warning message with yellow alert"""
    _cprint(f"⚠ {text}", "yellow")


def print_info(text: str):
    """Prints info message with blue info icon"""
    _cprint(f"ℹ {text}", "cyan")


def colorize_usage(current: int, limit: int) -> str:
    """Returns colored string for token usage"""
    if limit == 0:
        return f"{current}/{limit} (?%)"

    percentage = (current / limit) * 100
    text = f"{current:,}/{limit:,} ({percentage:.1f}%)"

    if percentage > 95:
        return colored(text, "red", attrs=["bold"])
    elif percentage > 80:
        return colored(text, "yellow")
    else:
        return colored(text, "green")
