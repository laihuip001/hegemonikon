# PROOF: [L2/文脈] <- mekhane/symploke/ O1→意図の継続性→intent_wal が担う
# PURPOSE: 意図の継続性管理 (WAL: Write-Ahead Log)
"""
Intent-WAL: Write-Ahead Log for Intent Persistence

セッションをまたいで「意図(Intent)」を維持するための仕組み。
セッション終了時に未完了タスクを記録し、次回起動時に復元する。
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# PURPOSE: WALのエントリー (1アクション)
@dataclass
class WALEntry:
    action: str
    status: str  # pending, done, blocked
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

# PURPOSE: WAL全体構造 (1セッション)
@dataclass
class IntentWAL:
    session_id: str
    session_goal: str
    context_health_level: int  # 0-100
    blockers: List[str]
    progress: List[WALEntry]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

# PURPOSE: WALの永続化管理
class IntentWALManager:
    WAL_PATH = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "intent_wal.json"

    def __init__(self):
        self.WAL_PATH.parent.mkdir(parents=True, exist_ok=True)

    # PURPOSE: WALを保存
    def save(self, wal: IntentWAL):
        data = {
            "session_id": wal.session_id,
            "session_goal": wal.session_goal,
            "context_health_level": wal.context_health_level,
            "blockers": wal.blockers,
            "progress": [
                {"action": e.action, "status": e.status, "timestamp": e.timestamp}
                for e in wal.progress
            ],
            "created_at": wal.created_at
        }
        self.WAL_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    # PURPOSE: 最新のWALを読み込み
    def load_latest(self) -> Optional[IntentWAL]:
        if not self.WAL_PATH.exists():
            return None
        try:
            data = json.loads(self.WAL_PATH.read_text())
            return IntentWAL(
                session_id=data.get("session_id", ""),
                session_goal=data.get("session_goal", ""),
                context_health_level=data.get("context_health_level", 0),
                blockers=data.get("blockers", []),
                progress=[
                    WALEntry(
                        action=e.get("action", ""),
                        status=e.get("status", ""),
                        timestamp=e.get("timestamp", "")
                    )
                    for e in data.get("progress", [])
                ],
                created_at=data.get("created_at", "")
            )
        except Exception:
            return None

    # PURPOSE: ブート画面用のサマリー生成
    def to_boot_section(self) -> str:
        wal = self.load_latest()
        if not wal:
            return ""

        lines = ["## Intent-WAL (Previous Session)"]
        lines.append(f"- **Goal**: {wal.session_goal}")
        lines.append(f"- **Health**: {wal.context_health_level}%")
        if wal.blockers:
            lines.append(f"- **Blockers**: {', '.join(wal.blockers)}")

        pending = [e for e in wal.progress if e.status != "done"]
        if pending:
            lines.append("- **Pending Actions**:")
            for e in pending[:5]:
                lines.append(f"  - [ ] {e.action}")
            if len(pending) > 5:
                lines.append(f"  - ... ({len(pending) - 5} more)")

        return "\n".join(lines)
