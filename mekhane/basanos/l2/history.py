#!/usr/bin/env python3
# PROOF: [L2/Basanos] <- mekhane/basanos/l2/ A0->History->Track
# PURPOSE: Basanos L2 deficit 履歴の永続化 — JSONL 形式で時系列追跡
# REASON: deficit の推移を記録し、体系の健全性トレンドを可視化するため
"""Deficit history persistence for Basanos L2.

Stores scan results as JSONL (one JSON object per line) for efficient
append-only writing and streaming reads.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from mekhane.basanos.l2.models import Deficit, DeficitType


# Default history file location
_DEFAULT_HISTORY_DIR = Path(os.environ.get(
    "BASANOS_HISTORY_DIR",
    Path.home() / "oikos" / "mneme" / ".hegemonikon" / "basanos",
))
_HISTORY_FILE = "l2_history.jsonl"


def _serialize_deficit(d: Deficit) -> dict[str, Any]:
    """Serialize a Deficit to a JSON-safe dict."""
    return {
        "type": d.type.value,
        "severity": d.severity,
        "source": d.source,
        "target": d.target,
        "description": d.description,
        "evidence": d.evidence,
        "suggested_action": d.suggested_action or "",
    }


def _deserialize_deficit(data: dict[str, Any]) -> Deficit:
    """Deserialize a dict back into a Deficit."""
    type_map = {t.value: t for t in DeficitType}
    return Deficit(
        type=type_map.get(data["type"], DeficitType.DELTA),
        severity=data.get("severity", 0.5),
        source=data.get("source", ""),
        target=data.get("target", ""),
        description=data.get("description", ""),
        evidence=data.get("evidence", []),
        suggested_action=data.get("suggested_action") or None,
    )


def record_scan(
    deficits: list[Deficit],
    history_dir: Optional[Path] = None,
    scan_type: str = "full",
) -> Path:
    """Append scan result to JSONL history file.

    Args:
        deficits: List of detected deficits
        history_dir: Custom history directory (default: ~/oikos/mneme/.hegemonikon/basanos/)
        scan_type: Type of scan (full, eta, epsilon, delta)

    Returns:
        Path to the history file
    """
    hdir = history_dir or _DEFAULT_HISTORY_DIR
    hdir.mkdir(parents=True, exist_ok=True)
    filepath = hdir / _HISTORY_FILE

    # Build summary counts
    by_type: dict[str, int] = {}
    for d in deficits:
        key = d.type.value
        by_type[key] = by_type.get(key, 0) + 1

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scan_type": scan_type,
        "total": len(deficits),
        "by_type": by_type,
        "deficits": [_serialize_deficit(d) for d in deficits],
    }

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return filepath


def load_history(
    history_dir: Optional[Path] = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Load scan history records (most recent first).

    Args:
        history_dir: Custom history directory
        limit: Maximum number of records to return

    Returns:
        List of scan records, newest first
    """
    hdir = history_dir or _DEFAULT_HISTORY_DIR
    filepath = hdir / _HISTORY_FILE

    if not filepath.exists():
        return []

    records: list[dict[str, Any]] = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # Return newest first
    records.reverse()
    return records[:limit]


def get_trend(
    history_dir: Optional[Path] = None,
    window: int = 10,
) -> dict[str, Any]:
    """Calculate deficit trend from recent history.

    Returns:
        Dict with trend info: direction, current, previous, delta, sparkline
    """
    records = load_history(history_dir, limit=window)

    if not records:
        return {"direction": "unknown", "current": 0, "previous": 0, "delta": 0, "sparkline": ""}

    totals = [r.get("total", 0) for r in records]
    current = totals[0] if totals else 0
    previous = totals[1] if len(totals) > 1 else current
    delta = current - previous

    if delta > 0:
        direction = "worsening"
    elif delta < 0:
        direction = "improving"
    else:
        direction = "stable"

    # Build sparkline (newest on right)
    spark_chars = "▁▂▃▄▅▆▇█"
    max_val = max(totals) if totals else 1
    sparkline = ""
    for t in reversed(totals):
        idx = min(int(t / max(max_val, 1) * (len(spark_chars) - 1)), len(spark_chars) - 1)
        sparkline += spark_chars[idx]

    return {
        "direction": direction,
        "current": current,
        "previous": previous,
        "delta": delta,
        "sparkline": sparkline,
        "window": len(totals),
    }
