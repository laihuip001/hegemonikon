#!/usr/bin/env python3
"""
Dispatch Log 自動集計スクリプト
==============================

dispatch_log.yaml から統計を生成し、dispatch_stats.json を出力。
タスクスケジューラから日次実行される。

Phase B移行条件:
- dispatch_count >= 50
- failure_rate < 10%
- exception_patterns >= 3
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

# パス設定
DISPATCH_LOG = Path(r"M:\Brain\.hegemonikon\logs\dispatch_log.yaml")
DISPATCH_STATS = Path(r"M:\Brain\.hegemonikon\logs\dispatch_stats.json")

def load_dispatch_log() -> dict:
    """dispatch_log.yaml を読み込み"""
    if not DISPATCH_LOG.exists():
        return {"entries": []}
    
    with open(DISPATCH_LOG, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {"entries": []}

def calculate_stats(data: dict) -> dict:
    """統計を計算"""
    entries = data.get("entries", [])
    
    if not entries:
        return {
            "dispatch_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "failure_rate": 0.0,
            "exception_patterns": [],
            "exception_count": 0,
            "phase_b_ready": False,
            "phase_b_progress": {
                "dispatch": "0/50",
                "failure_rate": "N/A",
                "exceptions": "0/3"
            },
            "t_series_distribution": {},
            "agent_distribution": {},
            "last_updated": datetime.now().isoformat()
        }
    
    # 基本統計
    total = len(entries)
    success = sum(1 for e in entries if e.get("status") == "success")
    failure = total - success
    failure_rate = (failure / total * 100) if total > 0 else 0.0
    
    # 例外パターン
    exceptions = [e.get("exception") for e in entries if e.get("exception")]
    exception_patterns = list(set(exceptions))
    
    # T-series分布
    t_series_counts = Counter(e.get("t_series", "unknown") for e in entries)
    
    # Agent分布
    source_counts = Counter(e.get("source_agent", "unknown") for e in entries)
    target_counts = Counter(e.get("target_agent", "unknown") for e in entries)
    
    # Phase B判定
    phase_b_ready = (
        total >= 50 and
        failure_rate < 10.0 and
        len(exception_patterns) >= 3
    )
    
    return {
        "dispatch_count": total,
        "success_count": success,
        "failure_count": failure,
        "failure_rate": round(failure_rate, 2),
        "exception_patterns": exception_patterns,
        "exception_count": len(exception_patterns),
        "phase_b_ready": phase_b_ready,
        "phase_b_progress": {
            "dispatch": f"{total}/50",
            "dispatch_pct": round(total / 50 * 100, 1),
            "failure_rate": f"{round(failure_rate, 1)}% (< 10%)",
            "exceptions": f"{len(exception_patterns)}/3"
        },
        "t_series_distribution": dict(t_series_counts),
        "agent_distribution": {
            "source": dict(source_counts),
            "target": dict(target_counts)
        },
        "last_updated": datetime.now().isoformat()
    }

def save_stats(stats: dict):
    """dispatch_stats.json に保存"""
    DISPATCH_STATS.parent.mkdir(parents=True, exist_ok=True)
    
    with open(DISPATCH_STATS, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Stats saved to {DISPATCH_STATS}")

def print_summary(stats: dict):
    """コンソールにサマリー表示"""
    print("\n" + "=" * 50)
    print("📊 Dispatch Log Statistics")
    print("=" * 50)
    print(f"Total Dispatches: {stats['dispatch_count']}")
    print(f"Success: {stats['success_count']} | Failure: {stats['failure_count']}")
    print(f"Failure Rate: {stats['failure_rate']}%")
    print(f"Exception Patterns: {stats['exception_count']}")
    print()
    print("🎯 Phase B Progress:")
    progress = stats["phase_b_progress"]
    print(f"  Dispatches: {progress['dispatch']} ({progress.get('dispatch_pct', 0)}%)")
    print(f"  Failure Rate: {progress['failure_rate']}")
    print(f"  Exceptions: {progress['exceptions']}")
    print()
    if stats["phase_b_ready"]:
        print("✅ PHASE B READY!")
    else:
        print("⏳ Phase B: Not Ready")
    print("=" * 50)

def main():
    """メイン処理"""
    print(f"Loading: {DISPATCH_LOG}")
    data = load_dispatch_log()
    
    stats = calculate_stats(data)
    save_stats(stats)
    print_summary(stats)
    
    return 0

if __name__ == "__main__":
    exit(main())
