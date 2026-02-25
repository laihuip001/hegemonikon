#!/usr/bin/env python3
# PROOF: [L3/Utility] <- scripts/ A0→Implementation→k_series_metrics
"""K-series metrics: Handoff からの K-series 出現頻度を計測する。

Usage:
    python scripts/k_series_metrics.py              # 全期間
    python scripts/k_series_metrics.py --since 7     # 直近7日
    python scripts/k_series_metrics.py --weekly       # 週次推移
"""

import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path


HANDOFF_DIR = Path.home() / "oikos/mneme/.hegemonikon/sessions"
# K-series patterns: K1-K12, K-series, /k, /k1-/k12
K_PATTERNS = [
    re.compile(r"\bK-series\b", re.IGNORECASE),
    re.compile(r"\bK[1-9]\d?\b"),           # K1, K2, ..., K12
    re.compile(r"/k\d{0,2}\b"),             # /k, /k1, /k12
    re.compile(r"\bKairos\b", re.IGNORECASE),
]


def _extract_date(filename: str) -> datetime | None:
    """handoff_YYYY-MM-DD_HHMM.md → datetime."""
    m = re.search(r"handoff_(\d{4}-\d{2}-\d{2})_(\d{4})", filename)
    if m:
        return datetime.strptime(f"{m.group(1)} {m.group(2)}", "%Y-%m-%d %H%M")
    # Fallback: date only
    m2 = re.search(r"handoff_(\d{4}-\d{2}-\d{2})", filename)
    if m2:
        return datetime.strptime(m2.group(1), "%Y-%m-%d")
    return None


def scan_handoffs(since_days: int | None = None) -> dict:
    """Scan all handoffs and return K-series metrics."""
    cutoff = None
    if since_days is not None:
        cutoff = datetime.now() - timedelta(days=since_days)

    files = sorted(HANDOFF_DIR.glob("handoff_*.md"))
    total = 0
    k_files = 0
    k_detail: dict[str, int] = {}  # K theorem → count
    weekly_data: dict[str, dict] = {}  # week → {total, k_count}

    for f in files:
        dt = _extract_date(f.name)
        if cutoff and dt and dt < cutoff:
            continue

        total += 1
        content = f.read_text(errors="replace")
        found = False

        for pat in K_PATTERNS:
            for match in pat.finditer(content):
                found = True
                key = match.group(0)
                k_detail[key] = k_detail.get(key, 0) + 1

        if found:
            k_files += 1

        # Weekly aggregation
        if dt:
            week_key = dt.strftime("%Y-W%W")
            if week_key not in weekly_data:
                weekly_data[week_key] = {"total": 0, "k_count": 0}
            weekly_data[week_key]["total"] += 1
            if found:
                weekly_data[week_key]["k_count"] += 1

    return {
        "total": total,
        "k_files": k_files,
        "rate": (k_files / total * 100) if total > 0 else 0,
        "detail": dict(sorted(k_detail.items(), key=lambda x: -x[1])),
        "weekly": dict(sorted(weekly_data.items())),
    }


def print_summary(metrics: dict) -> None:
    """Print formatted summary."""
    print("=" * 50)
    print("K-series ベースライン計測")
    print("=" * 50)
    print(f"  Handoff 総数: {metrics['total']}")
    print(f"  K-series 含有: {metrics['k_files']}")
    print(f"  出現率: {metrics['rate']:.1f}%")
    print()

    if metrics["detail"]:
        print("--- 出現パターン (降順) ---")
        for k, v in metrics["detail"].items():
            print(f"  {k:15s} {v:3d} 回")
    print()


def print_weekly(metrics: dict) -> None:
    """Print weekly trend."""
    if not metrics["weekly"]:
        print("週次データなし")
        return

    print("--- 週次推移 ---")
    print(f"  {'週':12s} {'総数':>5s} {'K含有':>5s} {'率':>7s}")
    print(f"  {'-'*12} {'-'*5} {'-'*5} {'-'*7}")
    for week, data in metrics["weekly"].items():
        rate = (data["k_count"] / data["total"] * 100) if data["total"] > 0 else 0
        bar = "█" * int(rate / 5)
        print(f"  {week:12s} {data['total']:5d} {data['k_count']:5d} {rate:5.1f}% {bar}")


def main():
    parser = argparse.ArgumentParser(description="K-series metrics")
    parser.add_argument("--since", type=int, help="直近N日のみ")
    parser.add_argument("--weekly", action="store_true", help="週次推移を表示")
    args = parser.parse_args()

    metrics = scan_handoffs(since_days=args.since)
    print_summary(metrics)
    if args.weekly:
        print_weekly(metrics)


if __name__ == "__main__":
    main()
