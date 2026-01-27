"""
UX Utilities for Gnōsis CLI

Provides ANSI color support, spinners, and formatted output helpers.
Gracefully degrades to plain text when not running in a TTY.
"""

import sys
import time
import threading
import itertools
from typing import Optional, ContextManager

# Check if we are in a TTY
IS_TTY = sys.stdout.isatty()

class Colors:
    """ANSI Color Codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DIM = '\033[2m'

    @staticmethod
    def disable():
        Colors.HEADER = ''
        Colors.BLUE = ''
        Colors.CYAN = ''
        Colors.GREEN = ''
        Colors.WARNING = ''
        Colors.FAIL = ''
        Colors.ENDC = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''
        Colors.DIM = ''

# Disable colors if not in TTY
if not IS_TTY:
    Colors.disable()

def print_header(msg: str):
    """Print a header with purple color."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {msg} ==={Colors.ENDC}")

def print_success(msg: str):
    """Print a success message with a checkmark."""
    print(f"{Colors.GREEN}✔ {msg}{Colors.ENDC}")

def print_error(msg: str):
    """Print an error message with a cross."""
    print(f"{Colors.FAIL}✘ {msg}{Colors.ENDC}")

def print_warning(msg: str):
    """Print a warning message with an exclamation mark."""
    print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")

def print_info(msg: str):
    """Print an info message with an info icon."""
    print(f"{Colors.BLUE}ℹ {msg}{Colors.ENDC}")

def print_table_row(col1: str, col2: str, width: int = 20):
    """Print a simple two-column row."""
    print(f"{col1:<{width}} : {Colors.BOLD}{col2}{Colors.ENDC}")

class Spinner:
    """
    A simple thread-based spinner for CLI.
    Usage:
        with Spinner("Loading..."):
            long_running_task()
    """
    def __init__(self, message: str = "Loading...", delay: float = 0.1):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.delay = delay
        self.busy = False
        self.spinner_visible = False
        self.message = message
        self._screen_lock = threading.Lock()
        self.thread: Optional[threading.Thread] = None

    def write_next(self):
        with self._screen_lock:
            if not self.spinner_visible:
                sys.stdout.write(self.message + " ")
                self.spinner_visible = True
            sys.stdout.write(next(self.spinner))
            sys.stdout.flush()
            sys.stdout.write('\b')

    def run(self):
        while self.busy:
            self.write_next()
            time.sleep(self.delay)
        self.remove_spinner()

    def remove_spinner(self):
        with self._screen_lock:
            if self.spinner_visible:
                sys.stdout.write('\r') # Go to start of line
                sys.stdout.write(' ' * (len(self.message) + 2)) # Clear everything
                sys.stdout.write('\r') # Go back to start
                sys.stdout.flush()
                self.spinner_visible = False

    def __enter__(self):
        if IS_TTY:
            self.busy = True
            self.thread = threading.Thread(target=self.run)
            self.thread.start()
        else:
            print(f"{self.message}...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if IS_TTY:
            self.busy = False
            if self.thread:
                self.thread.join()

            # Print result status if spinner was used
            if exc_type:
                print(f"{Colors.FAIL}✘ {self.message} Failed{Colors.ENDC}")
            else:
                print(f"{Colors.GREEN}✔ {self.message} Done{Colors.ENDC}")

if __name__ == "__main__":
    # Test the UX utilities
    print_header("UX Utils Test")
    print_info("This is an info message")
    print_warning("This is a warning")
    print_error("This is an error")
    print_success("This is a success")

    print("\nTesting Spinner...")
    with Spinner("Processing data"):
        time.sleep(2)

    print("\nTesting Table Row:")
    print_table_row("Status", "Active")
    print_table_row("Users", "42")
