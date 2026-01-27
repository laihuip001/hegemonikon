"""
UX Utilities - ANSI Colors and Helpers
Provides standardized color support and spinner for CLI tools.
"""
import sys
import threading
import time
import itertools
from contextlib import contextmanager

class Style:
    """ANSI Escape Codes"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def disable():
        """Disable all colors"""
        Style.HEADER = ''
        Style.BLUE = ''
        Style.CYAN = ''
        Style.GREEN = ''
        Style.WARNING = ''
        Style.FAIL = ''
        Style.ENDC = ''
        Style.BOLD = ''
        Style.UNDERLINE = ''

# Disable colors if not a TTY or explicitly requested (e.g. NO_COLOR env var could be checked here)
if not sys.stdout.isatty():
    Style.disable()

def print_header(msg: str):
    """Print a header message with visual distinction"""
    print(f"\n{Style.HEADER}{Style.BOLD}=== {msg} ==={Style.ENDC}")

def print_success(msg: str):
    """Print a success message in green"""
    print(f"{Style.GREEN}✔ {msg}{Style.ENDC}")

def print_error(msg: str):
    """Print an error message in red"""
    print(f"{Style.FAIL}✘ {msg}{Style.ENDC}")

def print_warning(msg: str):
    """Print a warning message in yellow"""
    print(f"{Style.WARNING}⚠ {msg}{Style.ENDC}")

def print_info(msg: str):
    """Print an info message in blue"""
    print(f"{Style.BLUE}ℹ {msg}{Style.ENDC}")

class Spinner:
    """
    Context manager for a CLI spinner.
    Usage:
        with Spinner("Loading..."):
            do_something_long()
    """
    def __init__(self, message: str = "Loading...", delay: float = 0.1):
        self.spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        self.delay = delay
        self.busy = False
        self.message = message
        self._screen_lock = threading.Lock()
        self.thread = None
        self._stop_event = threading.Event()

    def _spin(self):
        """Spinner animation loop"""
        while not self._stop_event.is_set():
            with self._screen_lock:
                sys.stdout.write(next(self.spinner) + " " + self.message + "\r")
                sys.stdout.flush()
            time.sleep(self.delay)

    def __enter__(self):
        if sys.stdout.isatty():
            self._stop_event.clear()
            self.thread = threading.Thread(target=self._spin)
            self.thread.start()
        else:
            print(f"{self.message}...")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if sys.stdout.isatty() and self.thread:
            self._stop_event.set()
            self.thread.join()
            with self._screen_lock:
                # Clear the line
                sys.stdout.write(' ' * (len(self.message) + 2) + '\r')
                sys.stdout.flush()
