#!/usr/bin/env python3
"""Sunset Checker — Experimental マクロの再審査リマインダー

Boot Phase 4 で自動実行。Sunset 日に近づいたら警告。
"""
import sys
from datetime import date

# ── Sunset Schedule ──
SUNSETS = [
    {
        "name": "Experimental マクロ (12件)",
        "date": date(2026, 8, 7),
        "file": "ccl/operators.md",
        "section": "11.3",
        "action": "未使用なら PHANTOM 削除。/dia で再審査。",
    },
]


def check_sunsets(warn_days: int = 30) -> list[dict]:
    """Sunset 日までの残り日数をチェック"""
    today = date.today()
    alerts = []
    for s in SUNSETS:
        delta = (s["date"] - today).days
        if delta <= 0:
            alerts.append({**s, "days": delta, "level": "🔴 EXPIRED"})
        elif delta <= warn_days:
            alerts.append({**s, "days": delta, "level": "🟡 APPROACHING"})
        else:
            alerts.append({**s, "days": delta, "level": "🟢 OK"})
    return alerts


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Sunset Checker")
    parser.add_argument("--warn-days", type=int, default=30)
    parser.add_argument("--quiet", action="store_true",
                        help="Only output if warnings exist")
    args = parser.parse_args()

    alerts = check_sunsets(args.warn_days)
    warnings = [a for a in alerts if a["level"] != "🟢 OK"]

    if args.quiet and not warnings:
        return

    print("=== Sunset Checker ===")
    for a in alerts:
        print(f"  {a['level']} {a['name']} — {a['days']}d remaining ({a['date']})")
        if a["days"] <= 0:
            print(f"    ⚠️ Action: {a['action']}")
            print(f"    📄 File: {a['file']} §{a['section']}")

    if warnings:
        sys.exit(1)


if __name__ == "__main__":
    main()
