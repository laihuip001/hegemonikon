# PROOF: [L2/Session] <- mekhane/anamnesis/ Session Activity Monitor
# PURPOSE: セッションの活動状況を監視する
"""Session Monitor Module."""

import time
import threading
from typing import Dict, Optional, Callable
from dataclasses import dataclass, field

@dataclass
class SessionActivity:
    """セッション活動情報"""
    session_id: str
    last_active: float
    status: str
    metrics: Dict[str, float] = field(default_factory=dict)

class SessionMonitor:
    """セッションモニタ"""

    def __init__(self, check_interval: float = 60.0):
        self.interval = check_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._sessions: Dict[str, SessionActivity] = {}
        self._callbacks: Dict[str, Callable[[str], None]] = {}

    def start(self):
        """監視を開始"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """監視を停止"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    def register_session(self, session_id: str):
        """セッションを監視対象に追加"""
        self._sessions[session_id] = SessionActivity(
            session_id=session_id,
            last_active=time.time(),
            status="active"
        )

    def update_activity(self, session_id: str):
        """活動時間を更新"""
        if session_id in self._sessions:
            self._sessions[session_id].last_active = time.time()
            self._sessions[session_id].status = "active"

    def on_timeout(self, callback: Callable[[str], None]):
        """タイムアウト時のコールバック登録"""
        self._callbacks["timeout"] = callback

    def _monitor_loop(self):
        """監視ループ"""
        while self._running:
            now = time.time()
            # 非アクティブなセッションを検出 (5分以上)
            timeout_threshold = 300.0

            for sid, activity in list(self._sessions.items()):
                if now - activity.last_active > timeout_threshold:
                    if activity.status == "active":
                        activity.status = "idle"
                        if "timeout" in self._callbacks:
                            try:
                                self._callbacks["timeout"](sid)
                            except Exception:
                                pass

            time.sleep(self.interval)
