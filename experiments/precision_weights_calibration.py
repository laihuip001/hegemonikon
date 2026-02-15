"""
F5: Precision Weights Default Calibration

PURPOSE: ソース別 (arxiv/session/handoff/github/manual) の検索有用性を
過去の Handoff データから推測し、デフォルトの precision_weights (π) を決定する。

Approach:
- 各ソースの Doxa/信念で引用された回数を計測
- 頻繁に引用されるソース = 高い π
- 結果を search() のデフォルト引数として使用
"""

import sys
import re
import json
from pathlib import Path
from collections import Counter

HANDOFF_DIR = Path.home() / "oikos/mneme/.hegemonikon/sessions"
OUTPUT_PATH = Path(__file__).parent / "precision_weights_defaults.json"


def count_source_references(handoff_path: Path) -> Counter:
    """Handoff 内のソース参照パターンを分析"""
    text = handoff_path.read_text(encoding="utf-8", errors="replace")
    counts = Counter()

    # arxiv pattern
    counts["arxiv"] += len(re.findall(r"arxiv|arXiv|論文|paper", text, re.IGNORECASE))

    # session/handoff pattern
    counts["session"] += len(re.findall(r"handoff|セッション|前回|session", text, re.IGNORECASE))

    # github pattern
    counts["github"] += len(re.findall(r"github|commit|PR|pull request", text, re.IGNORECASE))

    # manual/direct pattern
    counts["manual"] += len(re.findall(r"Creator|ユーザー|手動|直接", text, re.IGNORECASE))

    return counts


def main():
    handoff_files = sorted(HANDOFF_DIR.glob("handoff_*.md"))
    print(f"Analyzing {len(handoff_files)} handoff files")

    total_counts = Counter()
    for hf in handoff_files:
        counts = count_source_references(hf)
        total_counts += counts

    print(f"\nRaw reference counts:")
    for source, count in total_counts.most_common():
        print(f"  {source}: {count}")

    # Normalize to weights (highest = 1.5, lowest = 0.5)
    if total_counts:
        max_count = max(total_counts.values())
        min_count = min(total_counts.values())
        range_count = max_count - min_count if max_count != min_count else 1

        weights = {}
        for source, count in total_counts.items():
            # Linear scale from 0.5 to 1.5
            normalized = (count - min_count) / range_count
            weights[source] = round(0.5 + normalized * 1.0, 2)

        # Ensure unknown source gets 1.0 (neutral)
        weights["unknown"] = 1.0
    else:
        weights = {"arxiv": 1.2, "session": 1.0, "handoff": 1.1, "github": 0.8, "manual": 1.3, "unknown": 1.0}

    print(f"\nCalibrated precision weights (π):")
    for source, weight in sorted(weights.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {weight}")

    # Save results
    results = {
        "raw_counts": dict(total_counts),
        "precision_weights": weights,
        "calibration_date": "2026-02-15",
        "handoff_count": len(handoff_files),
    }
    OUTPUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nSaved to {OUTPUT_PATH}")

    return weights


if __name__ == "__main__":
    main()
