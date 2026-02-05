"""
UX Utilities for Gnōsis CLI.
Provides standardized colors and semantic print functions.
"""

import sys

try:
    from termcolor import colored, cprint
except ImportError:
    # Fallback if termcolor is not available
    def colored(text, color=None, on_color=None, attrs=None):
        return text

    def cprint(text, color=None, on_color=None, attrs=None, **kwargs):
        print(text, **kwargs)


def print_success(msg: str):
    """Print a success message (green)."""
    cprint(f"✅ {msg}", "green")


def print_error(msg: str):
    """Print an error message (red)."""
    cprint(f"❌ {msg}", "red", attrs=["bold"])


def print_warning(msg: str):
    """Print a warning message (yellow)."""
    cprint(f"⚠️ {msg}", "yellow")


def print_info(msg: str):
    """Print an informational message (cyan)."""
    cprint(f"ℹ️ {msg}", "cyan")


def print_header(msg: str):
    """Print a header message (bold white/underlined)."""
    cprint(f"\n{msg}", "white", attrs=["bold", "underline"])


def colorize_usage(text: str) -> str:
    """Colorize usage/help text."""
    # Simple heuristic to colorize command names or arguments
    # This assumes standard argparse help format
    return text  # For now just return as is, can be enhanced later
