"""
UX Utilities for CLI tools.
Provides ANSI colors and a threaded Spinner.
"""
import sys
import time
import threading
import itertools
from typing import Optional, Any

# ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"

# Cursor
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

# Disable colors if not TTY
if not sys.stdout.isatty():
    RESET = ""
    BOLD = ""
    DIM = ""
    RED = ""
    GREEN = ""
    YELLOW = ""
    BLUE = ""
    CYAN = ""
    HIDE_CURSOR = ""
    SHOW_CURSOR = ""

def print_header(text: str) -> None:
    """Print a styled header."""
    print(f"\n{BOLD}{CYAN}=== {text} ==={RESET}")

def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{BLUE}ℹ {text}{RESET}")

def print_dim(text: str) -> None:
    """Print dim text."""
    print(f"{DIM}{text}{RESET}")

class Spinner:
    """
    A threaded spinner for CLI loading states.
    Usage:
        with Spinner("Loading..."):
            do_work()
    """
    def __init__(self, message: str = "Loading...", delay: float = 0.1):
        self.message = message
        self.delay = delay
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def spin(self) -> None:
        """Spin animation loop."""
        spinner_chars = itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"])
        while self.running:
            sys.stdout.write(f"\r{next(spinner_chars)} {self.message}")
            sys.stdout.flush()
            time.sleep(self.delay)
            # Clear line is handled by the carriage return and overwrite,
            # but we need to ensure we don't leave artifacts if message changes length.
            # Here we just overwrite.

    def __enter__(self) -> 'Spinner':
        if sys.stdout.isatty():
            sys.stdout.write(HIDE_CURSOR)
            self.running = True
            self.thread = threading.Thread(target=self.spin)
            self.thread.start()
        else:
            print(f"{self.message}...")
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self.running and self.thread:
            self.running = False
            self.thread.join()
            # Clear the spinner line and show cursor
            sys.stdout.write(f"\r{' ' * (len(self.message) + 2)}\r")
            sys.stdout.write(SHOW_CURSOR)
            sys.stdout.flush()
