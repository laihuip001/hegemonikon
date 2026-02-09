#!/usr/bin/env python3
# PROOF: [L3/機能] <- mekhane/fep/ FEP Agent と Attractor の一致率を追跡
"""
Convergence Tracker — Agent/Attractor 一致率の永続的追跡

PURPOSE: FEP Agent と Attractor が同じ Series を選ぶかの収束を証明する。

Law: convergence_rate = Σ(agreements) / Σ(total)

Convergence proof (3-layer criteria, /noe+ designed):
  1. Statistical: rate > chance (1/6) with p < 0.05 (binomial test)
  2. Categorical: disagreements classified as explore/exploit/error
  3. Temporal: trend != "degrading"

If all 3 hold, convergence is proven.
"""

import json
import math
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal

# Disagreement categories (/noe+ design)
DisagreementCategory = Literal["explore", "exploit", "error", "unknown"]

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


def classify_disagreement(
    agent_series: Optional[str],
    attractor_series: Optional[str],
    agent_action: str = "",
) -> DisagreementCategory:
    """Classify why Agent and Attractor disagreed.

    Categories (/noe+ design):
    - explore: Agent chose observe, Attractor recommended a Series
              → Agent is gathering info, healthy divergence
    - exploit: Agent chose a different Series than Attractor
              → Both are acting but on different domains
    - error:   One returned None/invalid unexpectedly
    - unknown: Cannot determine category
    """
    if agent_series == attractor_series:
        return "unknown"  # agreement, not a disagreement

    # Agent observes while Attractor recommends → explore
    if agent_action == "observe" or agent_series is None:
        return "explore"

    # Both have a Series but different → exploit
    if agent_series and attractor_series:
        return "exploit"

    # Something None/invalid → error
    return "error"


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
    agreed = agent_series == attractor_series

    record = {
        "timestamp": datetime.now().isoformat(),
        "agent_series": agent_series,
        "attractor_series": attractor_series,
        "agent_action": agent_action,
        "agreed": agreed,
        "epsilon": epsilon,
    }

    # Add disagreement category if not agreed
    if not agreed:
        record["disagreement_category"] = classify_disagreement(
            agent_series, attractor_series, agent_action
        )

    records.append(record)

    # Truncate to MAX_RECORDS (keep most recent)
    if len(records) > MAX_RECORDS:
        records = records[-MAX_RECORDS:]

    _save_records(records)

    return convergence_summary(records)


def _binomial_p_value(successes: int, trials: int, chance: float = 1/6) -> float:
    """Compute one-sided binomial test p-value (H0: rate <= chance).

    Pure Python implementation — no scipy dependency.
    P(X >= successes | n=trials, p=chance) using the survival function.
    """
    if trials == 0 or successes == 0:
        return 1.0

    # P(X >= k) = 1 - P(X < k) = 1 - Σ_{i=0}^{k-1} C(n,i) * p^i * (1-p)^(n-i)
    p_value = 0.0
    for i in range(successes):
        # log-space to avoid overflow
        log_pmf = (
            _log_comb(trials, i)
            + i * math.log(chance)
            + (trials - i) * math.log(1 - chance)
        )
        p_value += math.exp(log_pmf)

    return round(1.0 - p_value, 6)


def _log_comb(n: int, k: int) -> float:
    """log(C(n, k)) using lgamma for numerical stability."""
    if k < 0 or k > n:
        return float("-inf")
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def convergence_summary(
    records: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Compute convergence statistics.

    Returns:
        Dict with:
        - total: number of records
        - agreements: number of agreements
        - rate: agreement rate (0.0-1.0)
        - p_value: binomial test p-value (H0: rate <= 1/6)
        - converged: True if p < 0.05 AND trend != "degrading"
        - recent_rate: agreement rate of last 10 records
        - trend: "improving" | "stable" | "degrading"
        - disagreement_breakdown: {explore: N, exploit: N, error: N}
    """
    if records is None:
        records = _load_records()

    if not records:
        return {
            "total": 0,
            "agreements": 0,
            "rate": 0.0,
            "p_value": 1.0,
            "converged": False,
            "recent_rate": 0.0,
            "trend": "unknown",
            "disagreement_breakdown": {},
        }

    total = len(records)
    agreements = sum(1 for r in records if r.get("agreed"))
    rate = agreements / total if total > 0 else 0.0

    # Binomial test: H0: rate <= 1/6 (chance with 6 Series)
    p_value = _binomial_p_value(agreements, total, chance=1/6)

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

    # Disagreement breakdown
    breakdown: Dict[str, int] = {}
    for r in records:
        if not r.get("agreed"):
            cat = r.get("disagreement_category", "unknown")
            breakdown[cat] = breakdown.get(cat, 0) + 1

    # Convergence: 3-layer criteria (/noe+ design)
    #   1. Statistical: p < 0.05
    #   2. Temporal: trend != "degrading"
    #   3. Minimum data: total >= 10
    converged = p_value < 0.05 and trend != "degrading" and total >= 10

    return {
        "total": total,
        "agreements": agreements,
        "rate": round(rate, 3),
        "p_value": p_value,
        "converged": converged,
        "recent_rate": round(recent_rate, 3),
        "trend": trend,
        "disagreement_breakdown": breakdown,
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

    p = summary.get("p_value", 1.0)
    p_str = f"p={p:.3f}" if p >= 0.001 else "p<0.001"
    p_icon = "✓" if p < 0.05 else "✗"

    base = (
        f"{icon} Convergence: {summary['rate']*100:.0f}% "
        f"({summary['agreements']}/{summary['total']}) "
        f"{p_str}{p_icon} "
        f"recent={summary['recent_rate']*100:.0f}% {trend_icon}"
    )

    # Add disagreement breakdown if any
    bd = summary.get("disagreement_breakdown", {})
    if bd:
        parts = [f"{k}={v}" for k, v in sorted(bd.items())]
        base += f" disagree=[{', '.join(parts)}]"

    return base
