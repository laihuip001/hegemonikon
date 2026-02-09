#!/usr/bin/env python3
# PROOF: [L3/機能] <- mekhane/fep/ FEP Agent と Attractor の一致率を追跡
"""
Convergence Tracker — Agent/Attractor 一致率の永続的追跡

PURPOSE: FEP Agent と Attractor が同じ Series を選ぶかの収束を証明する。

Law: convergence_rate = Σ(agreements) / Σ(total)

If converged (rate > threshold), it means two independent systems
(probabilistic inference vs. embedding similarity) agree on the same
cognitive domain — this is the fundamental consistency proof of Hegemonikón.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Max records to retain (prevents unbounded JSON growth)
MAX_RECORDS = 500

# Configurable via environment variable; falls back to default
_DEFAULT_PATH = os.path.expanduser(
    "~/oikos/mneme/.hegemonikon/convergence.json"
)
CONVERGENCE_PATH = Path(
    os.environ.get("HGK_CONVERGENCE_PATH", _DEFAULT_PATH)
)


def _load_records() -> List[Dict[str, Any]]:
    """Load convergence records from disk."""
    if not CONVERGENCE_PATH.exists():
        return []
    try:
        with open(CONVERGENCE_PATH, "r") as f:
            data = json.load(f)
        return data.get("records", [])
    except Exception:
        return []


def _save_records(records: List[Dict[str, Any]]) -> None:
    """Save convergence records to disk."""
    CONVERGENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "version": 1,
        "updated_at": datetime.now().isoformat(),
        "records": records,
    }
    with open(CONVERGENCE_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def record_agreement(
    agent_series: Optional[str],
    attractor_series: Optional[str],
    agent_action: str = "",
    epsilon: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Record an agreement/disagreement between Agent and Attractor.

    Args:
        agent_series: Series selected by FEP Agent (None = observe)
        attractor_series: Series recommended by Attractor
        agent_action: Action name (e.g. "act_O", "observe")
        epsilon: Current ε values (for correlation analysis)

    Returns:
        Updated convergence summary
    """
    records = _load_records()

    record = {
        "timestamp": datetime.now().isoformat(),
        "agent_series": agent_series,
        "attractor_series": attractor_series,
        "agent_action": agent_action,
        "agreed": agent_series == attractor_series,
        "epsilon": epsilon,
    }
    records.append(record)

    # Truncate to MAX_RECORDS (keep most recent)
    if len(records) > MAX_RECORDS:
        records = records[-MAX_RECORDS:]

    _save_records(records)

    return convergence_summary(records)


def convergence_summary(
    records: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Compute convergence statistics.

    Returns:
        Dict with:
        - total: number of records
        - agreements: number of agreements
        - rate: agreement rate (0.0-1.0)
        - converged: True if rate > 0.7 AND total >= 5
        - recent_rate: agreement rate of last 10 records
        - trend: "improving" | "stable" | "degrading"
    """
    if records is None:
        records = _load_records()

    if not records:
        return {
            "total": 0,
            "agreements": 0,
            "rate": 0.0,
            "converged": False,
            "recent_rate": 0.0,
            "trend": "unknown",
        }

    total = len(records)
    agreements = sum(1 for r in records if r.get("agreed"))
    rate = agreements / total if total > 0 else 0.0

    # Recent window (last 10)
    recent = records[-10:]
    recent_agreements = sum(1 for r in recent if r.get("agreed"))
    recent_rate = recent_agreements / len(recent) if recent else 0.0

    # Trend: compare first half vs second half
    if total >= 6:
        mid = total // 2
        first_half = records[:mid]
        second_half = records[mid:]
        rate_1 = sum(1 for r in first_half if r.get("agreed")) / len(first_half)
        rate_2 = sum(1 for r in second_half if r.get("agreed")) / len(second_half)
        if rate_2 - rate_1 > 0.1:
            trend = "improving"
        elif rate_1 - rate_2 > 0.1:
            trend = "degrading"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    converged = rate > 0.7 and total >= 5

    return {
        "total": total,
        "agreements": agreements,
        "rate": round(rate, 3),
        "converged": converged,
        "recent_rate": round(recent_rate, 3),
        "trend": trend,
    }


def format_convergence(summary: Optional[Dict[str, Any]] = None) -> str:
    """Format convergence summary for display."""
    if summary is None:
        summary = convergence_summary()

    if summary["total"] == 0:
        return "📊 Convergence: No data yet"

    icon = "✅" if summary["converged"] else "📊"
    trend_icon = {"improving": "↗", "stable": "→", "degrading": "↘"}.get(
        summary["trend"], "?"
    )

    return (
        f"{icon} Convergence: {summary['rate']*100:.0f}% "
        f"({summary['agreements']}/{summary['total']}) "
        f"recent={summary['recent_rate']*100:.0f}% {trend_icon}"
    )
