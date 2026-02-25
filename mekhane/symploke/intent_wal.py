#!/usr/bin/env python3
# PROOF: [L2/Impl] <- mekhane/symploke/ Automated fix for CI
# PURPOSE: Intent Write-Ahead Log (WAL) for session recovery
"""
Intent Write-Ahead Log

Persists session intent and progress to disk to allow recovery
after crashes or restarts.

Schema:
  - session_id: str
  - goal: str
  - steps: List[Step]
  - current_step_index: int
  - status: "active" | "completed" | "failed"
"""

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Dict, Any

# Default path
WAL_PATH = Path.home() / ".hegemonikon" / "intent_wal.json"


@dataclass
class WALStep:
    """A single step in the WAL."""
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class IntentWAL:
    """The full WAL state."""
    session_id: str
    session_goal: str
    progress: List[WALStep] = field(default_factory=list)
    context_health_level: str = "unknown"
    blockers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntentWAL':
        # Handle nested objects
        if "progress" in data:
            data["progress"] = [WALStep(**s) if isinstance(s, dict) else s for s in data["progress"]]
        return cls(**data)


class IntentWALManager:
    """Manages WAL persistence."""

    def __init__(self, path: Path = WAL_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._current_wal: Optional[IntentWAL] = None

    # PURPOSE: Load the latest WAL from disk
    def load_latest(self) -> Optional[IntentWAL]:
        if not self.path.exists():
            return None
        try:
            with open(self.path, "r") as f:
                data = json.load(f)
                self._current_wal = IntentWAL.from_dict(data)
                return self._current_wal
        except Exception:
            return None

    # PURPOSE: Save current WAL to disk
    def save(self, wal: IntentWAL) -> None:
        self._current_wal = wal
        with open(self.path, "w") as f:
            json.dump(wal.to_dict(), f, indent=2)

    # PURPOSE: Create a boot section summary
    def to_boot_section(self) -> str:
        if not self._current_wal:
            return ""

        wal = self._current_wal
        lines = [
            f"📋 **Intent-WAL** (Session: {wal.session_id})",
            f"   Goal: {wal.session_goal}",
            f"   Health: {wal.context_health_level}"
        ]

        pending = [s for s in wal.progress if s.status == "pending"]
        if pending:
            lines.append(f"   Remaining: {len(pending)} steps")

        return "\n".join(lines)
