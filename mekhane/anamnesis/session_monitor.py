# PROOF: [L1/Trokhia] <- mekhane/anamnesis/
# PURPOSE: 起動中の Antigravity LS セッションを監視し、更新があればインデックスする
"""
PROOF: [L2/インフラ] <- mekhane/anamnesis/

P3 → 記憶の永続化が必要
   → リアルタイムのセッション監視とインデックスが必要
   → session_monitor.py が担う

Q.E.D.

---

Session Monitor — リアルタイムセッション監視デーモン

Antigravity LS の GetAllCascadeTrajectories をポーリングし、
lastModifiedTime が更新されたセッションを検知して session_indexer.py を呼び出す。

Usage:
    python mekhane/anamnesis/session_monitor.py
"""

import time
import sys
import subprocess
import signal
from pathlib import Path
from datetime import datetime

# Ensure hegemonikon root is in path
_HEGEMONIKON_ROOT = Path(__file__).parent.parent.parent
if str(_HEGEMONIKON_ROOT) not in sys.path:
    sys.path.insert(0, str(_HEGEMONIKON_ROOT))

from mekhane.ochema.antigravity_client import AntigravityClient


# PURPOSE: [L2-auto] グレースフルシャットダウン用フラグ
_shutdown = False


def signal_handler(sig, frame):
    # PURPOSE: [L2-auto] シグナルハンドラ
    """PURPOSE: [L2-auto] シグナルハンドラ"""
    global _shutdown
    print("\n[Monitor] Shutting down...")
    _shutdown = True


# PURPOSE: [L2-auto] 変更されたセッションを検知してインデックスするメインループ
def monitor_sessions(interval: float = 10.0):
    """PURPOSE: [L2-auto] 変更されたセッションを検知してインデックスするメインループ"""
    client = AntigravityClient()
    last_checked = datetime.utcnow().isoformat() + "Z"
    known_modified: dict[str, str] = {}

    print(f"[Monitor] Starting session monitor (interval={interval}s)")

    while not _shutdown:
        try:
            # LS からセッション一覧を取得
            data = client._rpc(
                "exa.language_server_pb.LanguageServerService/GetAllCascadeTrajectories", {}
            )
            summaries = data.get("trajectorySummaries", {})

            current_time = datetime.utcnow().isoformat() + "Z"
            updated_sessions = []

            for cid, meta in summaries.items():
                modified = meta.get("lastModifiedTime", "")
                if not modified:
                    continue

                # 前回チェック時より新しい、または前回記録した変更時刻より新しい
                if modified > last_checked and modified > known_modified.get(cid, ""):
                    updated_sessions.append(cid)
                    known_modified[cid] = modified

            if updated_sessions:
                print(f"[Monitor] Detected {len(updated_sessions)} updated sessions")
                # インデクサを呼び出す (今回は簡易的に全体更新、最適化はID指定で)
                # TODO: session_indexer.py に ID 指定オプションを追加して部分更新する
                subprocess.run(
                    [sys.executable, "mekhane/anamnesis/session_indexer.py", "--from-api"],
                    check=False
                )

            last_checked = current_time
            time.sleep(interval)

        except Exception as e:
            print(f"[Monitor] Error: {e}")
            time.sleep(interval)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    monitor_sessions()
