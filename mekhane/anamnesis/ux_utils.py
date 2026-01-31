"""
UX Utilities for CLI Tools

Provides standardized ANSI color support and helper functions for CLI output.
"""

import sys

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'

def _colorize(text: str, color: str) -> str:
    """Apply color if stdout is a TTY."""
    if not sys.stdout.isatty():
        return text
    return f"{color}{text}{Colors.ENDC}"

def print_header(text: str):
    """Print a bold header."""
    print(_colorize(f"\n=== {text} ===", Colors.HEADER + Colors.BOLD))

def print_success(text: str):
    """Print a success message in green."""
    print(_colorize(f"✓ {text}", Colors.OKGREEN))

def print_error(text: str):
    """Print an error message in red."""
    print(_colorize(f"✖ {text}", Colors.FAIL))

def print_warning(text: str):
    """Print a warning message in yellow."""
    print(_colorize(f"⚠ {text}", Colors.WARNING))

def print_info(text: str):
    """Print an info message in blue/cyan."""
    print(_colorize(f"ℹ {text}", Colors.OKCYAN))

def print_dim(text: str):
    """Print a dim message."""
    print(_colorize(text, Colors.DIM))

def strip_ansi(text: str) -> str:
    """Remove ANSI codes from text."""
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)
