# PROOF: [L2/Mekhane] <- mekhane/symploke/ A0->Auto->AddedByCI
#!/usr/bin/env python3
# PROOF: [L2/ユーティリティ] <- mekhane/symploke/ A4→ログ分析→analyze_basanos_logs が担う
# PURPOSE: Jules Daily Scheduler のログを集計し、ドメインローテーション網羅率を可視化
"""
Basanos Log Analyzer

Usage:
    python analyze_basanos_logs.py --days 7
    python analyze_basanos_logs.py --days 30 --format json
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs" / "specialist_daily"

# 全 20 ドメイン (Basanos PerspectiveMatrix 定義)
ALL_DOMAINS = [
    "Architecture", "Security", "Performance", "Reliability",
    "Testing", "Documentation", "Maintainability", "ErrorHandling",
    "DataIntegrity", "Concurrency", "API", "Configuration",
    "Logging", "Observability", "Dependency", "Usability",
    "Accessibility", "Internationalization", "Resource", "Compliance",
]


# PURPOSE: ログファイルを読み込む
def load_logs(days: int) -> list[dict]:
    """過去 N 日間のスケジューラーログを読み込む。"""
    cutoff = datetime.now() - timedelta(days=days)
    logs = []

    if not LOG_DIR.exists():
        return logs

    for log_file in sorted(LOG_DIR.glob("scheduler_*.json")):
        try:
            data = json.loads(log_file.read_text())
            ts = datetime.strptime(data.get("timestamp", ""), "%Y-%m-%d %H:%M")
            if ts >= cutoff:
                logs.append(data)
        except (json.JSONDecodeError, ValueError):
            continue

    return logs


# PURPOSE: ドメインローテーション分析
def analyze_domain_coverage(logs: list[dict]) -> dict:
    """ドメインの使用頻度と網羅率を計算。"""
    domain_counts: dict[str, int] = {d: 0 for d in ALL_DOMAINS}
    basanos_runs = 0

    for log in logs:
        if log.get("mode") != "basanos":
            continue
        basanos_info = log.get("basanos", {})
        domains = basanos_info.get("domains", [])
        basanos_runs += 1
        for d in domains:
            if d in domain_counts:
                domain_counts[d] += 1

    covered = sum(1 for c in domain_counts.values() if c > 0)
    total = len(ALL_DOMAINS)

    return {
        "basanos_runs": basanos_runs,
        "coverage": f"{covered}/{total} ({covered/total*100:.0f}%)" if total else "N/A",
        "domain_frequency": dict(sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)),
        "uncovered": [d for d, c in domain_counts.items() if c == 0],
    }


# PURPOSE: Pre-audit スコア分析
def analyze_pre_audit(logs: list[dict]) -> dict:
    """Pre-audit スコアの統計。"""
    scores = []
    files_with_issues_total = 0
    files_total = 0

    for log in logs:
        audit = log.get("pre_audit", {})
        if not audit:
            continue
        scores.append(audit.get("total_score", 0))
        files_with_issues_total += audit.get("files_with_issues", 0)
        files_total += len(audit.get("file_scores", {})) + audit.get("files_with_issues", 0)

    if not scores:
        return {"runs": 0, "message": "No pre-audit data found"}

    return {
        "runs": len(scores),
        "avg_score": sum(scores) / len(scores),
        "max_score": max(scores),
        "total_files_with_issues": files_with_issues_total,
    }


# PURPOSE: モード比較
def analyze_mode_comparison(logs: list[dict]) -> dict:
    """specialist vs basanos の使用統計。"""
    modes: dict[str, dict] = {
        "specialist": {"runs": 0, "total_tasks": 0, "total_started": 0},
        "basanos": {"runs": 0, "total_tasks": 0, "total_started": 0},
    }

    for log in logs:
        mode = log.get("mode", "specialist")
        result = log.get("result", {})
        if mode in modes:
            modes[mode]["runs"] += 1
            modes[mode]["total_tasks"] += result.get("total_tasks", 0)
            modes[mode]["total_started"] += result.get("total_started", 0)

    return modes


# PURPOSE: メイン
def main():
    parser = argparse.ArgumentParser(description="Basanos Log Analyzer")
    parser.add_argument("--days", type=int, default=7, help="Days to analyze (default: 7)")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    logs = load_logs(args.days)

    if args.format == "json":
        result = {
            "period_days": args.days,
            "total_logs": len(logs),
            "domain_coverage": analyze_domain_coverage(logs),
            "pre_audit": analyze_pre_audit(logs),
            "mode_comparison": analyze_mode_comparison(logs),
        }
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    # Text format
    print(f"\n{'='*50}")
    print(f"Jules Basanos Log Analysis — past {args.days} days")
    print(f"{'='*50}")
    print(f"Total log entries: {len(logs)}")

    # Domain coverage
    coverage = analyze_domain_coverage(logs)
    print(f"\n📊 Domain Coverage:")
    print(f"  Basanos runs: {coverage['basanos_runs']}")
    print(f"  Coverage:     {coverage['coverage']}")
    if coverage["uncovered"]:
        print(f"  Uncovered:    {', '.join(coverage['uncovered'])}")
    print(f"\n  Frequency:")
    for domain, count in coverage["domain_frequency"].items():
        bar = "█" * count
        print(f"    {domain:24s} {count:2d} {bar}")

    # Pre-audit
    audit = analyze_pre_audit(logs)
    print(f"\n🔍 Pre-audit:")
    if audit.get("runs", 0) > 0:
        print(f"  Runs:         {audit['runs']}")
        print(f"  Avg score:    {audit['avg_score']:.1f}")
        print(f"  Max score:    {audit['max_score']}")
        print(f"  Files w/ issues: {audit['total_files_with_issues']}")
    else:
        print(f"  {audit.get('message', 'No data')}")

    # Mode comparison
    modes = analyze_mode_comparison(logs)
    print(f"\n⚔️  Mode Comparison:")
    for mode, stats in modes.items():
        rate = (stats["total_started"] / stats["total_tasks"] * 100) if stats["total_tasks"] else 0
        print(f"  {mode:12s}: {stats['runs']} runs, {stats['total_started']}/{stats['total_tasks']} tasks ({rate:.0f}%)")

    print()


if __name__ == "__main__":
    main()
