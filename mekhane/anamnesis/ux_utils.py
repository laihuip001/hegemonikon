"""
UX Utilities for Gnōsis CLI
"""
import sys

# Check if stdout is a TTY to decide whether to use colors
IS_TTY = sys.stdout.isatty()

class Colors:
    HEADER = '\033[95m' if IS_TTY else ''
    BLUE = '\033[94m' if IS_TTY else ''
    CYAN = '\033[96m' if IS_TTY else ''
    GREEN = '\033[92m' if IS_TTY else ''
    WARNING = '\033[93m' if IS_TTY else ''
    FAIL = '\033[91m' if IS_TTY else ''
    ENDC = '\033[0m' if IS_TTY else ''
    BOLD = '\033[1m' if IS_TTY else ''
    UNDERLINE = '\033[4m' if IS_TTY else ''
    DIM = '\033[2m' if IS_TTY else ''

def print_header(text: str):
    """Prints a header with bold purple color."""
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")

def print_success(text: str):
    """Prints a success message in green."""
    print(f"{Colors.GREEN}{text}{Colors.ENDC}")

def print_error(text: str):
    """Prints an error message in red."""
    print(f"{Colors.FAIL}{text}{Colors.ENDC}")

def print_warning(text: str):
    """Prints a warning message in yellow."""
    print(f"{Colors.WARNING}{text}{Colors.ENDC}")

def color_text(text: str, color: str) -> str:
    """Returns text wrapped in the specified color code."""
    # Note: color argument might already be empty string if IS_TTY is False
    # But we still need to append ENDC only if color is applied?
    # Actually, if Colors.HEADER is '', then `color` passed here (e.g. Colors.HEADER) is ''.
    # And Colors.ENDC is ''. So f"{''}{text}{''}" is just text.
    return f"{color}{text}{Colors.ENDC}"
