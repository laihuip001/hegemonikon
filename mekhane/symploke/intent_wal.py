#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/symploke/ S2->Mekhane->Intent WAL
"""Intent-WAL (Write-Ahead Log) Manager.

Manages session intent WAL files for crash recovery and context continuity.
Based on DB WAL pattern: write intent BEFORE execution.

Path: ~/oikos/mneme/.hegemonikon/wal/intent_{YYYYMMDD}_{HHMM}.yaml
Schema: intent_wal_schema.md v1.0
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

# WAL default directory
WAL_DIR = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "wal"

# Context health levels (BC-18)
CONTEXT_HEALTH_LEVELS = ("green", "yellow", "orange", "red")


@dataclass
class ProgressEntry:
    """A single progress log entry (append-only)."""

    timestamp: str
    step: int
    action: str
    status: str  # pending | in_progress | done | blocked
    detail: str = ""

    def to_dict(self) -> dict:
        d = {
            "timestamp": self.timestamp,
            "step": self.step,
            "action": self.action,
            "status": self.status,
        }
        if self.detail:
            d["detail"] = self.detail
        return d


@dataclass
class IntentWAL:
    """Intent-WAL data structure."""

    # Meta
    session_id: str
    agent: str = "Claude"
    created_at: str = ""
    updated_at: str = ""
    n_chat_messages: int = 0

    # Intent (required)
    session_goal: str = ""
    acceptance_criteria: list[str] = field(default_factory=list)
    context: str = ""

    # Progress (append-only)
    progress: list[ProgressEntry] = field(default_factory=list)

    # Recovery
    last_file_edited: str = ""
    uncommitted_changes: bool = False
    blockers: list[str] = field(default_factory=list)

    # Context health (BC-18)
    context_health_level: str = "green"
    savepoint: Optional[str] = None
    recommendation: Optional[str] = None

    def __post_init__(self):
        now = datetime.now().astimezone().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

    def to_dict(self) -> dict:
        """Serialize to YAML-compatible dict."""
        return {
            "version": "1.0",
            "meta": {
                "session_id": self.session_id,
                "agent": self.agent,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "n_chat_messages": self.n_chat_messages,
            },
            "intent": {
                "session_goal": self.session_goal,
                "acceptance_criteria": self.acceptance_criteria,
                "context": self.context,
            },
            "progress": [e.to_dict() for e in self.progress],
            "recovery": {
                "last_file_edited": self.last_file_edited,
                "uncommitted_changes": self.uncommitted_changes,
                "blockers": self.blockers,
            },
            "context_health": {
                "level": self.context_health_level,
                "savepoint": self.savepoint,
                "recommendation": self.recommendation,
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> IntentWAL:
        """Deserialize from YAML dict."""
        meta = data.get("meta", {})
        intent = data.get("intent", {})
        recovery = data.get("recovery", {})
        health = data.get("context_health", {})

        progress_entries = []
        for entry in data.get("progress", []):
            progress_entries.append(
                ProgressEntry(
                    timestamp=entry.get("timestamp", ""),
                    step=entry.get("step", 0),
                    action=entry.get("action", ""),
                    status=entry.get("status", "pending"),
                    detail=entry.get("detail", ""),
                )
            )

        return cls(
            session_id=meta.get("session_id", ""),
            agent=meta.get("agent", "Claude"),
            created_at=meta.get("created_at", ""),
            updated_at=meta.get("updated_at", ""),
            n_chat_messages=meta.get("n_chat_messages", 0),
            session_goal=intent.get("session_goal", ""),
            acceptance_criteria=intent.get("acceptance_criteria", []),
            context=intent.get("context", ""),
            progress=progress_entries,
            last_file_edited=recovery.get("last_file_edited", ""),
            uncommitted_changes=recovery.get("uncommitted_changes", False),
            blockers=recovery.get("blockers", []),
            context_health_level=health.get("level", "green"),
            savepoint=health.get("savepoint"),
            recommendation=health.get("recommendation"),
        )


class IntentWALManager:
    """Manages Intent-WAL lifecycle: create, update, load, convert."""

    def __init__(self, wal_dir: Path = WAL_DIR):
        self.wal_dir = wal_dir
        self.wal_dir.mkdir(parents=True, exist_ok=True)
        self._current: Optional[IntentWAL] = None
        self._current_path: Optional[Path] = None

    def create(
        self,
        session_goal: str,
        session_id: str,
        agent: str = "Claude",
        acceptance_criteria: Optional[list[str]] = None,
        context: str = "",
    ) -> tuple[IntentWAL, Path]:
        """Create a new WAL file. Returns (wal, path)."""
        now = datetime.now()
        filename = f"intent_{now.strftime('%Y%m%d_%H%M')}.yaml"
        path = self.wal_dir / filename

        wal = IntentWAL(
            session_id=session_id,
            agent=agent,
            session_goal=session_goal,
            acceptance_criteria=acceptance_criteria or [],
            context=context,
        )

        self._write(wal, path)
        self._current = wal
        self._current_path = path
        return wal, path

    def update_progress(
        self,
        step: int,
        action: str,
        status: str = "done",
        detail: str = "",
    ) -> IntentWAL:
        """Append a progress entry (append-only)."""
        if not self._current or not self._current_path:
            raise RuntimeError("No active WAL. Call create() or load() first.")
        assert self._current is not None
        assert self._current_path is not None

        entry = ProgressEntry(
            timestamp=datetime.now().astimezone().isoformat(),
            step=step,
            action=action,
            status=status,
            detail=detail,
        )
        self._current.progress.append(entry)
        self._current.updated_at = datetime.now().astimezone().isoformat()
        self._write(self._current, self._current_path)
        return self._current

    def update_context_health(
        self,
        level: str,
        savepoint: Optional[str] = None,
        recommendation: Optional[str] = None,
    ) -> IntentWAL:
        """Update context health (BC-18 integration)."""
        if not self._current or not self._current_path:
            raise RuntimeError("No active WAL. Call create() or load() first.")
        assert self._current is not None
        assert self._current_path is not None

        if level not in CONTEXT_HEALTH_LEVELS:
            raise ValueError(f"Invalid level: {level}. Must be one of {CONTEXT_HEALTH_LEVELS}")

        self._current.context_health_level = level
        if savepoint is not None:
            self._current.savepoint = savepoint
        if recommendation is not None:
            self._current.recommendation = recommendation
        self._current.updated_at = datetime.now().astimezone().isoformat()
        self._write(self._current, self._current_path)
        return self._current

    def update_recovery(
        self,
        last_file_edited: Optional[str] = None,
        uncommitted_changes: Optional[bool] = None,
        blockers: Optional[list[str]] = None,
    ) -> IntentWAL:
        """Update recovery information."""
        if not self._current or not self._current_path:
            raise RuntimeError("No active WAL. Call create() or load() first.")
        assert self._current is not None
        assert self._current_path is not None

        if last_file_edited is not None:
            self._current.last_file_edited = last_file_edited
        if uncommitted_changes is not None:
            self._current.uncommitted_changes = uncommitted_changes
        if blockers is not None:
            self._current.blockers = blockers
        self._current.updated_at = datetime.now().astimezone().isoformat()
        self._write(self._current, self._current_path)
        return self._current

    def load(self, path: Path) -> IntentWAL:
        """Load a WAL from file."""
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        wal = IntentWAL.from_dict(data)
        self._current = wal
        self._current_path = path
        return wal

    def load_latest(self) -> Optional[IntentWAL]:
        """Load the most recent WAL file."""
        files = sorted(self.wal_dir.glob("intent_*.yaml"), reverse=True)
        if not files:
            return None
        return self.load(files[0])

    def to_handoff_section(self) -> str:
        """Convert current WAL to a Handoff-compatible section."""
        if not self._current:
            return ""

        wal = self._current
        lines = ["## Intent-WAL (セッション意図)"]
        lines.append("")
        lines.append(f"**Session Goal**: {wal.session_goal}")

        if wal.acceptance_criteria:
            lines.append("")
            lines.append("**Acceptance Criteria**:")
            for ac in wal.acceptance_criteria:
                lines.append(f"- {ac}")

        if wal.progress:
            lines.append("")
            lines.append("**Progress**:")
            lines.append("")
            lines.append("| Step | Action | Status |")
            lines.append("|:-----|:-------|:-------|")
            for entry in wal.progress:
                lines.append(f"| {entry.step} | {entry.action} | {entry.status} |")

        lines.append("")
        lines.append(f"**Context Health**: {wal.context_health_level}")

        if wal.blockers:
            lines.append(f"**Blockers**: {', '.join(wal.blockers)}")

        return "\n".join(lines)

    def to_boot_section(self) -> str:
        """Convert current WAL to a Boot Report section (for /boot integration)."""
        if not self._current:
            return ""

        wal = self._current
        lines = ["## Intent-WAL"]
        lines.append("")
        lines.append("```yaml")
        lines.append("intent_wal:")
        lines.append(f"  session_goal: \"{wal.session_goal}\"")
        lines.append("```")

        if wal.progress:
            done = sum(1 for e in wal.progress if e.status == "done")
            total = len(wal.progress)
            lines.append(f"\n**Progress**: {done}/{total} steps completed")

        return "\n".join(lines)

    @property
    def current(self) -> Optional[IntentWAL]:
        """Get current WAL."""
        return self._current

    @property
    def current_path(self) -> Optional[Path]:
        """Get current WAL file path."""
        return self._current_path

    def _write(self, wal: IntentWAL, path: Path) -> None:
        """Write WAL to YAML file."""
        data = wal.to_dict()
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(
                data,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
