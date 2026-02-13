# PROOF: [P3/Trokhia] <- mekhane/anamnesis/session_monitor.py
# PURPOSE: 実行中の Antigravity セッションを監視し、メタデータを記録する
"""
Session Monitor — リアルタイムセッション監視

Antigravity Language Server のステータスをポーリングし、
アクティブなセッションの変更 (step count, turn state) を検知して
ログや通知を行う。

Usage:
    python mekhane/anamnesis/session_monitor.py
"""

import time
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Ensure hegemonikon root is in path
_HEGEMONIKON_ROOT = Path(__file__).parent.parent.parent
if str(_HEGEMONIKON_ROOT) not in sys.path:
    sys.path.insert(0, str(_HEGEMONIKON_ROOT))

from mekhane.ochema.antigravity_client import AntigravityClient


# PURPOSE: [L2-auto] セッション監視クラス
class SessionMonitor:
    """セッション監視クラス"""

    def __init__(self, interval: float = 2.0):
        self.interval = interval
        self.client = AntigravityClient()
        self.last_state: dict[str, dict] = {}
        self.active_cascade_id: Optional[str] = None

    # PURPOSE: [L2-auto] 監視ループを実行
    def run(self):
        """監視ループを実行"""
        print(f"[SessionMonitor] Started monitoring (interval={self.interval}s)")

        while True:
            try:
                self._check()
            except Exception as e:
                print(f"[Error] {e}")

            time.sleep(self.interval)

    # PURPOSE: [L2-auto] 状態チェック
    def _check(self):
        """状態チェック"""
        # LS から全セッション情報を取得
        # Note: session_info() は trajectorySummaries を返す
        info = self.client.session_info()
        if "error" in info:
            # LS が起動していない場合などは静かに待機
            return

        sessions = info.get("sessions", [])
        current_state = {}

        # 最新の RUNNING セッションを探す
        running_session = None
        for s in sessions:
            cid = s["cascade_id"]
            step_count = s["step_count"]
            status = s["status"]
            modified = s["modified"]

            current_state[cid] = {
                "step_count": step_count,
                "status": status,
                "modified": modified,
            }

            if "RUNNING" in status:
                running_session = s

        # 変更検知
        for cid, state in current_state.items():
            last = self.last_state.get(cid)
            if not last:
                # New session found
                print(f"[New] {cid[:8]} (steps={state['step_count']})")
                continue

            if state["step_count"] != last["step_count"]:
                diff = state["step_count"] - last["step_count"]
                print(f"[Update] {cid[:8]} +{diff} steps -> {state['step_count']}")

            if state["status"] != last["status"]:
                print(f"[Status] {cid[:8]} {last['status']} -> {state['status']}")

        self.last_state = current_state

        # アクティブセッションの切り替わり
        if running_session:
            if self.active_cascade_id != running_session["cascade_id"]:
                print(f"[Active] Switched to {running_session['cascade_id'][:8]}")
                self.active_cascade_id = running_session["cascade_id"]
        elif self.active_cascade_id:
            print(f"[Active] No running session")
            self.active_cascade_id = None


# PURPOSE: [L2-auto] 関数: main
def main():
    monitor = SessionMonitor()
    try:
        monitor.run()
    except KeyboardInterrupt:
        print("\n[SessionMonitor] Stopped")


if __name__ == "__main__":
    main()
