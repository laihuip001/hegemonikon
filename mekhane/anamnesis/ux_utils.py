"""
UX Utilities for CLI applications.
Provides standardized semantic coloring using termcolor.
"""
import sys
import os
from termcolor import colored, cprint

# Disable colors if not in a TTY
if not sys.stdout.isatty():
    os.environ["ANSI_COLORS_DISABLED"] = "1"

def print_header(message: str):
    """Print a header message in magenta and bold."""
    cprint(message, "magenta", attrs=["bold"])

def print_success(message: str):
    """Print a success message with a green checkmark."""
    print(f"{colored('✓', 'green', attrs=['bold'])} {message}")

def print_error(message: str):
    """Print an error message with a red cross."""
    print(f"{colored('✗', 'red', attrs=['bold'])} {message}")

def print_warning(message: str):
    """Print a warning message with a yellow symbol."""
    print(f"{colored('⚠', 'yellow', attrs=['bold'])} {message}")

def print_info(message: str):
    """Print an informational message with a blue symbol."""
    print(f"{colored('ℹ', 'blue', attrs=['bold'])} {message}")

def print_dim(message: str):
    """Print a message in dim/dark color."""
    cprint(message, "white", attrs=["dark"])

class Colors:
    """
    Standard ANSI color codes for manual usage.
    """
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

    @staticmethod
    def disable():
        Colors.HEADER = ''
        Colors.OKBLUE = ''
        Colors.OKCYAN = ''
        Colors.OKGREEN = ''
        Colors.WARNING = ''
        Colors.FAIL = ''
        Colors.ENDC = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''
        Colors.DIM = ''

if not sys.stdout.isatty():
    Colors.disable()
