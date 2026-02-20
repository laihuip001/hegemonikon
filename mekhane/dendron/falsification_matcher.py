# PROOF: [L2/インフラ] <- mekhane/dendron/ A0→Quality
"""
S7 Falsification Matcher

Matches paper content against the epistemic status registry
to detect potential falsifications.

PURPOSE: /eat 消化時に呼び出し、新論文の主張が既存パッチの反証条件に
該当する可能性がないか自動チェックする。

Usage:
    from mekhane.dendron.falsification_matcher import check_falsification
    alerts = check_falsification(paper_text="...")
"""

import sys
from pathlib import Path
import yaml

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
REGISTRY_PATH = PROJECT_ROOT / "kernel" / "epistemic_status.yaml"


# PURPOSE: Load the epistemic status registry
def load_registry() -> dict:
    """Load the epistemic status registry"""
    if not REGISTRY_PATH.exists():
        return {"patches": {}}
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f) or {"patches": {}}


# PURPOSE: Check for potential falsifications in paper text
def check_falsification(
    paper_text: str,
    paper_title: str = "",
    threshold: float = 0.5,
) -> list[dict]:
    """
    論文テキストが反証条件にマッチするかチェックする。

    Args:
        paper_text: 論文の本文または要約
        paper_title: 論文タイトル (ログ用)
        threshold: キーワードマッチの閾値 (0-1)

    Returns:
        警告リスト [{patch_id, claim, falsification, matched_keywords, score}]
    """
    registry = load_registry()
    patches = registry.get("patches", {})
    alerts = []

    paper_lower = paper_text.lower()

    for patch_id, data in patches.items():
        # Check if patch is active
        if data.get("status") not in ("active", "provisional"):
            continue

        falsification = data.get("falsification", {})
        condition = falsification.get("condition", "")
        keywords = falsification.get("keywords", [])

        if not condition:
            continue

        # Check keywords
        matched = [k for k in keywords if k.lower() in paper_lower]

        # Simple scoring based on keyword matches
        score = 0.0
        if keywords:
            score = len(matched) / len(keywords)

        # If score exceeds threshold, add alert
        if score >= threshold:
            alerts.append({
                "patch_id": patch_id,
                "claim": data.get("claim", ""),
                "falsification": condition,
                "matched_keywords": matched,
                "score": score
            })

    # Sort by score (highest first)
    alerts.sort(key=lambda a: a["score"], reverse=True)
    return alerts


# PURPOSE: Format alerts into readable text
def format_alerts(alerts: list[dict], paper_title: str = "") -> str:
    """警告をフォーマットされたテキストに変換"""
    if not alerts:
        return ""

    lines = [
        f"⚠️ Falsification Alert: '{paper_title}'",
        "The following claims might be challenged:",
    ]

    for alert in alerts:
        lines.append(f"\n[{alert['patch_id']}] Score: {alert['score']:.2f}")
        lines.append(f"  Claim: {alert['claim']}")
        lines.append(f"  Condition: {alert['falsification']}")
        lines.append(f"  Matched: {', '.join(alert['matched_keywords'])}")

    return "\n".join(lines)


if __name__ == "__main__":
    # Test run
    sample = """
    We demonstrate that attention is not all you need.
    Recurrent models with efficient state space layers outperform Transformers.
    Chain-of-Thought is harmful for simple reasoning tasks.
    Shallow layers in LLMs do not process syntax;
    only deep layers handle causal reasoning. Our architecture shows
    that parallel sampling outperforms sequential Chain-of-Thought
    in knowledge-intensive tasks.
    """

    alerts = check_falsification(sample, "Demo Paper")
    if alerts:
        print(format_alerts(alerts, "Demo Paper"))
    else:
        print("✅ No falsification conditions triggered")
