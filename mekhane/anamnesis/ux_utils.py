"""
UX Utilities for CLI tools.
Provides standardized coloring and formatting.
"""
import sys
import os

try:
    from termcolor import colored, cprint
except ImportError:
    # Fallback if termcolor is not installed
    def colored(text, color=None, on_color=None, attrs=None):
        return text

    def cprint(text, color=None, on_color=None, attrs=None, **kwargs):
        print(text, **kwargs)

# Disable colors if not in a TTY
if not sys.stdout.isatty():
    os.environ["ANSI_COLORS_DISABLED"] = "1"

class Colors:
    HEADER = "magenta"
    INFO = "cyan"
    SUCCESS = "green"
    WARNING = "yellow"
    ERROR = "red"

def print_header(text):
    """Print a header line."""
    cprint(f"\n=== {text} ===", Colors.HEADER, attrs=["bold"])

def print_success(text):
    """Print a success message."""
    cprint(f"✓ {text}", Colors.SUCCESS)

def print_error(text):
    """Print an error message."""
    cprint(f"✗ {text}", Colors.ERROR)

def print_warning(text):
    """Print a warning message."""
    cprint(f"! {text}", Colors.WARNING)

def print_info(text):
    """Print an informational message."""
    cprint(f"ℹ {text}", Colors.INFO)

def print_dim(text):
    """Print dim text (e.g. details)."""
    cprint(text, attrs=["dark"])
