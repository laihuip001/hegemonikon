"""
UX Utilities for CLI Tools

Provides standardized ANSI color support and helper functions for CLI output.
"""

import sys

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"

def _color(text: str, color: str) -> str:
    """Apply color if stdout is a tty."""
    if not sys.stdout.isatty():
        return text
    return f"{color}{text}{Colors.RESET}"

def print_header(text: str):
    """Print a header in bold cyan."""
    print(f"\n{_color(text, Colors.BOLD + Colors.CYAN)}")

def print_success(text: str):
    """Print a success message in green."""
    print(_color(f"✔ {text}", Colors.GREEN))

def print_error(text: str):
    """Print an error message in red."""
    print(_color(f"✘ {text}", Colors.RED))

def print_warning(text: str):
    """Print a warning message in yellow."""
    print(_color(f"⚠ {text}", Colors.YELLOW))

def print_info(text: str):
    """Print an info message in blue."""
    print(_color(f"ℹ {text}", Colors.BLUE))

def print_dim(text: str):
    """Print a dimmed message."""
    print(_color(text, Colors.DIM))
