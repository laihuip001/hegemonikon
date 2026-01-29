import sys
import time
import threading
import itertools
from contextlib import contextmanager

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"

    @staticmethod
    def is_enabled():
        return sys.stdout.isatty()

    @classmethod
    def format(cls, text, color):
        if not cls.is_enabled():
            return text
        return f"{color}{text}{cls.RESET}"

def print_header(text):
    line = "=" * 40
    print(f"\n{Colors.format(line, Colors.CYAN)}")
    print(Colors.format(f" {text}", Colors.BOLD + Colors.CYAN))
    print(Colors.format(line, Colors.CYAN))

def print_success(text):
    print(f"{Colors.format('✓', Colors.GREEN)} {text}")

def print_error(text):
    print(f"{Colors.format('✗', Colors.RED)} {text}", file=sys.stderr)

def print_warning(text):
    print(f"{Colors.format('⚠', Colors.YELLOW)} {text}")

def print_info(text):
    print(f"{Colors.format('ℹ', Colors.BLUE)} {text}")

class Spinner:
    def __init__(self, message="Loading...", delay=0.1):
        self.message = message
        self.delay = delay
        self.stop_running = threading.Event()
        self.spin_thread = None

    def spin(self):
        spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        while not self.stop_running.is_set():
            if Colors.is_enabled():
                sys.stdout.write(f"\r{Colors.format(next(spinner), Colors.CYAN)} {self.message}")
                sys.stdout.flush()
            time.sleep(self.delay)

    def __enter__(self):
        if Colors.is_enabled():
            self.stop_running.clear()
            self.spin_thread = threading.Thread(target=self.spin)
            self.spin_thread.start()
        else:
            print(f"... {self.message}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if Colors.is_enabled() and self.spin_thread:
            self.stop_running.set()
            self.spin_thread.join()
            sys.stdout.write("\r" + " " * (len(self.message) + 2) + "\r")
            sys.stdout.flush()
