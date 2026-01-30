import sys
import threading
import time
from contextlib import contextmanager

# Check if we are in a TTY
IS_TTY = sys.stdout.isatty()

class Colors:
    """ANSI color codes with auto-disable for non-TTY."""
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

def print_header(message):
    """Prints a styled header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {message} ==={Colors.ENDC}")

def print_success(message):
    """Prints a success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Prints an error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_warning(message):
    """Prints a warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_info(message):
    """Prints an info message."""
    print(f"{Colors.CYAN}ℹ {message}{Colors.ENDC}")

def print_dim(message):
    """Prints a dimmed message."""
    print(f"{Colors.DIM}{message}{Colors.ENDC}")

class Spinner:
    """
    A simple threaded spinner for CLI feedback.
    Usage:
        with Spinner("Loading..."):
            long_running_task()
    """
    def __init__(self, message="Processing...", delay=0.1):
        self.spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.delay = delay
        self.message = message
        self.running = False
        self.thread = None

    def spin(self):
        while self.running:
            for char in self.spinner:
                if not self.running:
                    break
                sys.stdout.write(f"\r{Colors.CYAN}{char}{Colors.ENDC} {self.message}")
                sys.stdout.flush()
                time.sleep(self.delay)

    def __enter__(self):
        if IS_TTY:
            self.running = True
            self.thread = threading.Thread(target=self.spin)
            self.thread.start()
        else:
            print(f"{self.message}...")
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self.running:
            self.running = False
            self.thread.join()
            if exc_type:
                sys.stdout.write(f"\r{Colors.FAIL}✗{Colors.ENDC} {self.message} Failed!   \n")
            else:
                sys.stdout.write(f"\r{Colors.GREEN}✓{Colors.ENDC} {self.message} Done!   \n")
            sys.stdout.flush()
