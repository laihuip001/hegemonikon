"""
UX Utilities for CLI
Provides standardized ANSI color support and helper functions.
"""
import sys
import os

try:
    from termcolor import colored, cprint
    HAS_TERMCOLOR = True
except ImportError:
    HAS_TERMCOLOR = False

    def colored(text, color=None, on_color=None, attrs=None):
        return text

    def cprint(text, color=None, on_color=None, attrs=None, **kwargs):
        print(text, **kwargs)

# Disable colors if not TTY
if not sys.stdout.isatty() and not os.environ.get("FORCE_COLOR"):
    if HAS_TERMCOLOR:
        os.environ["ANSI_COLORS_DISABLED"] = "1"

def print_header(message: str):
    """Print a header message (Magenta, Bold)."""
    cprint(f"\n{message}", "magenta", attrs=["bold"])

def print_success(message: str):
    """Print a success message (Green checkmark)."""
    print(f"{colored('✓', 'green', attrs=['bold'])} {message}")

def print_error(message: str):
    """Print an error message (Red cross)."""
    print(f"{colored('✗', 'red', attrs=['bold'])} {message}")

def print_warning(message: str):
    """Print a warning message (Yellow warning sign)."""
    print(f"{colored('⚠', 'yellow', attrs=['bold'])} {message}")

def print_info(message: str):
    """Print an info message (Blue info sign)."""
    print(f"{colored('ℹ', 'blue', attrs=['bold'])} {message}")

def print_dim(message: str):
    """Print a dimmed message."""
    # 'dark' attribute is effectively dim in many terminals
    cprint(message, attrs=["dark"])

def get_colored(text: str, color: str, attrs: list = None) -> str:
    """Get colored text string."""
    return colored(text, color, attrs=attrs)
