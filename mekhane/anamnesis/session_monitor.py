# PROOF: [L2/Anamnesis] <- mekhane/anamnesis/ A0→記憶の監視→セッションモニタ
# PURPOSE: Session Monitor — チャットセッションのリアルタイム監視
"""Session Monitor — Real-time monitoring of chat sessions.

Detects new sessions and updates, triggering indexing.
"""

import os
import time
from typing import Callable, Optional

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

# Target directory
SESSIONS_DIR = os.path.expanduser("~/.config/Code/User/globalStorage/robolison.antigravity/trajectories")


class SessionHandler(FileSystemEventHandler):
    """Watchdog handler for session files."""

    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".json"):
            self.callback(event.src_path)

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(".json"):
            self.callback(event.src_path)


class SessionMonitor:
    """Session Monitor."""

    def __init__(self, target_dir: str = SESSIONS_DIR):
        self.target_dir = target_dir
        self.observer = Observer()

    def start(self, callback: Callable[[str], None]):
        """Start monitoring."""
        if not os.path.isdir(self.target_dir):
            print(f"Warning: Directory not found: {self.target_dir}")
            return

        handler = SessionHandler(callback)
        self.observer.schedule(handler, self.target_dir, recursive=False)
        self.observer.start()
        print(f"Started monitoring: {self.target_dir}")

    def stop(self):
        """Stop monitoring."""
        self.observer.stop()
        self.observer.join()

    def run_forever(self, callback: Callable[[str], None]):
        """Run monitoring loop."""
        self.start(callback)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
