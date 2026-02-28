# PROOF: [L2/Infra] <- mekhane/dendron/
"""
Falsification Matcher — 消化論文の主張と epistemic_status.yaml の反証条件を照合

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


# PURPOSE: Check for falsification conditions in a given text
def check_falsification(
    paper_text: str,
    paper_title: str = "",
    threshold: float = 0.5,
) -> list[dict]:
    """
    消化テキストと反証条件を照合し、警告を生成。

    Args:
        paper_text: 消化対象のテキスト (全文 or 要約)
        paper_title: 論文タイトル (ログ用)
        threshold: キーワードマッチの閾値 (0-1)

    Returns:
        警告リスト [{patch_id, claim, falsification, matched_keywords, score}]
    """
    registry = load_registry()
    patches = registry.get("patches", {})
    alerts = []

    paper_lower = paper_text.lower()

    for patch_id, patch in patches.items():
        falsification = patch.get("falsification", "")
        if not falsification:
            continue

        # Keyword extraction from falsification condition
        # Split into meaningful keywords (3+ chars)
        keywords = [
            w.strip(".,;:()\"'")
            for w in falsification.lower().split()
            if len(w.strip(".,;:()\"'")) >= 3
        ]
        # Remove common stopwords
        stopwords = {
            "the", "and", "for", "that", "this", "with", "from", "not",
            "are", "was", "were", "been", "being", "have", "has", "had",
            "does", "did", "will", "would", "could", "should", "may",
            "might", "shall", "can", "its", "his", "her", "our",
            "その", "この", "あの", "する", "ある", "いる",
            "ない", "ない場合", "場合", "場合は",
        }
        keywords = [k for k in keywords if k not in stopwords]

        if not keywords:
            continue

        # Count keyword matches
        matched = [k for k in keywords if k in paper_lower]
        score = len(matched) / len(keywords) if keywords else 0

        if score >= threshold:
            alerts.append({
                "patch_id": patch_id,
                "claim": patch.get("claim", ""),
                "status": patch.get("status", ""),
                "falsification": falsification,
                "matched_keywords": matched,
                "score": score,
                "source": patch.get("source", ""),
            })

    # Sort by score (highest first)
    alerts.sort(key=lambda a: a["score"], reverse=True)
    return alerts


# PURPOSE: Format falsification alerts into readable text
def format_alerts(alerts: list[dict], paper_title: str = "") -> str:
    """警告をフォーマットされたテキストに変換"""
    if not alerts:
        return ""

    lines = [
        "⚠️ **Falsification Alert** — 以下のパッチの反証条件に関連する可能性:",
        "",
    ]

    for a in alerts:
        lines.extend([
            f"- **{a['patch_id']}** ({a['status']}): {a['claim']}",
            f"  反証条件: {a['falsification']}",
            f"  マッチ: {', '.join(a['matched_keywords'])} (score: {a['score']:.0%})",
            "",
        ])

    lines.append(
        "> 上記は自動検出です。実際に反証が成立するかは人間の判断が必要です。"
    )

    return "\n".join(lines)


if __name__ == "__main__":
    # Demo: run with sample text
    sample = """
    This paper demonstrates that attention mechanisms in shallow layers
    can capture causal dependencies, contradicting the assumption that
    only deep layers handle causal reasoning. Our architecture shows
    that parallel sampling outperforms sequential Chain-of-Thought
    in knowledge-intensive tasks.
    """

    alerts = check_falsification(sample, "Demo Paper")
    if alerts:
        print(format_alerts(alerts, "Demo Paper"))
    else:
        print("✅ No falsification conditions triggered")
