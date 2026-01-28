import sys
import threading
import time
import itertools

# ANSI Colors
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
CYAN = "\033[36m"

USE_COLOR = sys.stdout.isatty()

def _c(color, text):
    return f"{color}{text}{RESET}" if USE_COLOR else text

def print_header(text):
    print(f"\n{_c(BOLD + CYAN, '== ' + text + ' ==')}")

def print_success(text):
    print(f"{_c(GREEN, '✓')} {text}")

def print_error(text):
    print(f"{_c(RED, '✗ Error:')} {text}")

def print_warning(text):
    print(f"{_c(YELLOW, '! Warning:')} {text}")

def print_info(text):
    print(f"{_c(BLUE, 'ℹ')} {text}")

class Spinner:
    def __init__(self, message="Processing..."):
        self.message = message
        self.stop_event = threading.Event()
        self.thread = None

    def __enter__(self):
        if not USE_COLOR:
            print(f"{self.message}...")
            return
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.thread:
            self.stop_event.set()
            self.thread.join()
            sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
            sys.stdout.flush()

    def _spin(self):
        for char in itertools.cycle(["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]):
            if self.stop_event.is_set():
                break
            sys.stdout.write(f"\r{_c(CYAN, char)} {self.message}")
            sys.stdout.flush()
            time.sleep(0.1)
