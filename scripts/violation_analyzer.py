#!/usr/bin/env python3
# PROOF: [L2/運用] <- scripts/
# PURPOSE: violations.md の自動分析 + /boot 用サマリー生成
"""
violation_analyzer.py — 違反パターン自動分析

violations.md から構造化エントリを読み込み、
パターン統計と傾向レポートを生成する。
/boot 時に呼び出して「過去の違反傾向」を想起させる。

Usage:
    python scripts/violation_analyzer.py                 # フルレポート
    python scripts/violation_analyzer.py --summary       # /boot 用サマリー
    python scripts/violation_analyzer.py --pattern skip_bias  # パターン別
    python scripts/violation_analyzer.py --since 7       # 直近N日
"""

import re
import sys
import argparse
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import yaml


# ============================================================
# Config
# ============================================================

VIOLATIONS_PATH = (
    Path(__file__).parent.parent / ".agent" / "rules" /
    "behavioral_constraints" / "violations.md"
)

PATTERN_NAMES = {
    "skip_bias": "知っている→省略",
    "env_gap": "環境強制なし",
    "accuracy_vs_utility": "正確 ≠ 有用",
    "false_impossibility": "できない ≠ やっていない",
    "selective_omission": "勝手な省略",
    "stale_handoff": "古い情報を信じる",
}


# ============================================================
# Parser
# ============================================================

def parse_violations(path: Optional[Path] = None) -> list[dict]:
    """violations.md から YAML エントリを抽出する。"""
    path = path or VIOLATIONS_PATH
    if not path.exists():
        return []

    content = path.read_text(encoding="utf-8")

    # ```yaml ... ``` ブロックを全て抽出
    entries = []
    for match in re.finditer(r"```yaml\n(.+?)\n```", content, re.DOTALL):
        try:
            data = yaml.safe_load(match.group(1))
            if isinstance(data, dict) and "id" in data:
                entries.append(data)
        except yaml.YAMLError:
            continue

    return entries


# ============================================================
# Analysis
# ============================================================

def analyze(
    entries: list[dict],
    pattern_filter: Optional[str] = None,
    since_days: Optional[int] = None,
) -> dict:
    """違反エントリを分析して統計を返す。"""
    # フィルタリング
    filtered = entries

    if pattern_filter:
        filtered = [e for e in filtered if e.get("pattern") == pattern_filter]

    if since_days is not None:
        cutoff = datetime.now() - timedelta(days=since_days)
        filtered = [
            e for e in filtered
            if datetime.strptime(e.get("date", "2000-01-01"), "%Y-%m-%d") >= cutoff
        ]

    # 統計
    pattern_counts = Counter(e.get("pattern", "unknown") for e in filtered)
    bc_counts: Counter = Counter()
    for e in filtered:
        bcs = e.get("bc", [])
        if isinstance(bcs, list):
            bc_counts.update(bcs)
        else:
            bc_counts[str(bcs)] += 1

    severity_counts = Counter(e.get("severity", "unknown") for e in filtered)
    recurrence_count = sum(1 for e in filtered if e.get("recurrence"))

    return {
        "total": len(filtered),
        "patterns": dict(pattern_counts.most_common()),
        "bc_counts": dict(bc_counts.most_common()),
        "severity": dict(severity_counts),
        "recurrence": recurrence_count,
        "entries": filtered,
    }


# ============================================================
# Formatters
# ============================================================

def format_full_report(stats: dict) -> str:
    """フルレポートを生成。"""
    lines = [
        "📊 違反パターン分析レポート",
        f"   総件数: {stats['total']}",
        f"   再犯数: {stats['recurrence']}",
        "",
        "── パターン別 ──",
    ]

    for pattern, count in stats["patterns"].items():
        name = PATTERN_NAMES.get(pattern, pattern)
        lines.append(f"  {count}件  {name} ({pattern})")

    lines.append("")
    lines.append("── BC 別 ──")
    for bc, count in stats["bc_counts"].items():
        lines.append(f"  {count}件  {bc}")

    lines.append("")
    lines.append("── 深刻度 ──")
    for sev, count in stats["severity"].items():
        icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(sev, "⚪")
        lines.append(f"  {icon} {sev}: {count}件")

    return "\n".join(lines)


def format_boot_summary(stats: dict) -> str:
    """/boot 用の簡潔なサマリー。"""
    if stats["total"] == 0:
        return "✅ 違反記録なし"

    # 最頻出パターンを1つ
    top_pattern = max(stats["patterns"], key=stats["patterns"].get) if stats["patterns"] else None
    top_name = PATTERN_NAMES.get(top_pattern, top_pattern) if top_pattern else "不明"
    top_count = stats["patterns"].get(top_pattern, 0) if top_pattern else 0

    lines = [
        f"⚠️ 違反傾向 ({stats['total']}件)",
        f"  最頻出: {top_name} ({top_count}/{stats['total']})",
    ]

    if stats["recurrence"] > 0:
        lines.append(f"  🔴 再犯: {stats['recurrence']}件")

    # 直近の教訓
    if stats["entries"]:
        latest = stats["entries"][-1]
        lesson = latest.get("lesson", latest.get("summary", ""))
        lines.append(f"  最新教訓: {lesson}")

    return "\n".join(lines)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="違反パターン自動分析 — /boot 用サマリー生成"
    )
    parser.add_argument("--summary", action="store_true", help="/boot 用簡潔サマリー")
    parser.add_argument("--pattern", type=str, help="パターンIDでフィルタ")
    parser.add_argument("--since", type=int, help="直近N日間")
    parser.add_argument("--json", action="store_true", help="JSON出力")
    parser.add_argument("--path", type=str, help="violations.md パス（デフォルト: 自動検出）")
    args = parser.parse_args()

    path = Path(args.path) if args.path else None
    entries = parse_violations(path)
    stats = analyze(entries, pattern_filter=args.pattern, since_days=args.since)

    if args.json:
        import json
        # entries は冗長なので除外
        output = {k: v for k, v in stats.items() if k != "entries"}
        print(json.dumps(output, ensure_ascii=False, indent=2))
    elif args.summary:
        print(format_boot_summary(stats))
    else:
        print(format_full_report(stats))

    sys.exit(0)


if __name__ == "__main__":
    main()
