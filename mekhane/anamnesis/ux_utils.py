"""
UX Utilities for CLI tools.

This module provides standardized ANSI color support and a threaded Spinner class
for loading states, along with semantic print helpers.
"""

import sys
import threading
import time
import itertools
from typing import Optional, Any


class Colors:
    """ANSI color codes for CLI output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def format(text: str, color: str) -> str:
        """Format text with color if stdout is a TTY."""
        if sys.stdout.isatty():
            return f"{color}{text}{Colors.ENDC}"
        return text


class Spinner:
    """Threaded spinner for long-running operations."""

    def __init__(self, message: str = "Loading...", delay: float = 0.1):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.delay = delay
        self.message = message
        self.running = False
        self.thread: Optional[threading.Thread] = None

    def spin(self) -> None:
        """Spin animation loop."""
        while self.running:
            sys.stdout.write(f"\r{next(self.spinner)} {self.message}")
            sys.stdout.flush()
            time.sleep(self.delay)

    def __enter__(self) -> 'Spinner':
        self.running = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.start()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, exc_traceback: Any) -> None:
        self.running = False
        if self.thread:
            self.thread.join()
        # Clear the line
        sys.stdout.write(f"\r{' ' * (len(self.message) + 2)}\r")
        sys.stdout.flush()


def print_header(msg: str) -> None:
    """Print a header message."""
    print(Colors.format(f"\n=== {msg} ===", Colors.HEADER))


def print_success(msg: str) -> None:
    """Print a success message."""
    print(Colors.format(f"✓ {msg}", Colors.GREEN))


def print_error(msg: str) -> None:
    """Print an error message."""
    print(Colors.format(f"✗ {msg}", Colors.FAIL))


def print_info(msg: str) -> None:
    """Print an info message."""
    print(Colors.format(f"ℹ {msg}", Colors.BLUE))


def print_warning(msg: str) -> None:
    """Print a warning message."""
    print(Colors.format(f"⚠ {msg}", Colors.WARNING))
