import sys
import os
from typing import Optional

try:
    from termcolor import colored, cprint
except ImportError:
    # Fallback if termcolor is not installed
    def colored(text: str, color: Optional[str] = None, on_color: Optional[str] = None, attrs: Optional[list] = None) -> str:
        return text

    def cprint(text: str, color: Optional[str] = None, on_color: Optional[str] = None, attrs: Optional[list] = None, **kwargs):
        print(text, **kwargs)

# Check if we should disable colors
if not sys.stdout.isatty() or os.environ.get("ANSI_COLORS_DISABLED"):
    os.environ["ANSI_COLORS_DISABLED"] = "1"

class Colors:
    HEADER = "cyan"
    SUCCESS = "green"
    WARNING = "yellow"
    ERROR = "red"
    INFO = "blue"
    DIM = "grey"

def print_header(text: str):
    """Print a header with cyan color and bold attribute."""
    cprint(f"\n=== {text} ===", Colors.HEADER, attrs=["bold"])

def print_success(text: str):
    """Print a success message with green color."""
    cprint(f"✓ {text}", Colors.SUCCESS)

def print_error(text: str):
    """Print an error message with red color and bold attribute."""
    cprint(f"✗ {text}", Colors.ERROR, attrs=["bold"])

def print_warning(text: str):
    """Print a warning message with yellow color."""
    cprint(f"! {text}", Colors.WARNING)

def print_info(text: str):
    """Print an info message with blue color."""
    cprint(f"ℹ {text}", Colors.INFO)

def print_dim(text: str):
    """Print text with grey color (dim)."""
    cprint(text, Colors.DIM)
