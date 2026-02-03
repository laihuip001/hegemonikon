"""
UX Utilities for Gnōsis CLI.
Provides standardized colors and semantic print functions.
"""
import sys

try:
    from termcolor import cprint
    HAS_TERMCOLOR = True
except ImportError:
    HAS_TERMCOLOR = False

    def cprint(text, color=None, on_color=None, attrs=None, **kwargs):
        print(text, **kwargs)

class Colors:
    """Standardized colors for the CLI."""
    HEADER = 'magenta'
    OKBLUE = 'blue'
    OKCYAN = 'cyan'
    OKGREEN = 'green'
    WARNING = 'yellow'
    FAIL = 'red'
    ENDC = 'white'
    BOLD = 'bold'
    UNDERLINE = 'underline'

def _print_styled(text, color=None, attrs=None):
    """Internal helper to handle safe printing."""
    # Only use color if available and TTY
    if HAS_TERMCOLOR and sys.stdout.isatty():
        cprint(text, color=color, attrs=attrs)
    else:
        print(text)

def print_header(text):
    """Print a section header."""
    _print_styled(f"\n{text}", Colors.HEADER, attrs=['bold'])

def print_success(text):
    """Print a success message."""
    _print_styled(f"[OK] {text}", Colors.OKGREEN)

def print_error(text):
    """Print an error message."""
    _print_styled(f"[!!] {text}", Colors.FAIL, attrs=['bold'])

def print_warning(text):
    """Print a warning message."""
    _print_styled(f"[WARN] {text}", Colors.WARNING)

def print_info(text):
    """Print an info message."""
    _print_styled(f"[INFO] {text}", Colors.OKCYAN)

def print_dim(text):
    """Print dim text (useful for dry runs or secondary info)."""
    _print_styled(text, attrs=['dark'])
