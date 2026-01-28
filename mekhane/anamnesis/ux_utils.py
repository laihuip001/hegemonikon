import sys

# Constants for ANSI colors
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Check if we should disable colors (non-TTY)
DISABLE_COLORS = not sys.stdout.isatty()

def _c(color, text):
    """Apply color if supported."""
    if DISABLE_COLORS:
        return text
    return f"{color}{text}{Colors.ENDC}"

def print_header(text):
    """Print a header message."""
    print(f"\n{_c(Colors.HEADER, '=== ' + text + ' ===')}")

def print_success(text):
    """Print a success message."""
    print(_c(Colors.GREEN, f"✓ {text}"))

def print_error(text):
    """Print an error message."""
    print(_c(Colors.FAIL, f"✗ {text}"))

def print_warning(text):
    """Print a warning message."""
    print(_c(Colors.WARNING, f"⚠ {text}"))

def print_info(text):
    """Print an informational message."""
    print(_c(Colors.BLUE, f"ℹ {text}"))
