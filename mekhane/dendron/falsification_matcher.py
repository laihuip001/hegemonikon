# PROOF: [L2/Mekhane] <- mekhane/dendron/falsification_matcher.py A0→Necessity
"""
S7: Falsification Condition Matcher

PURPOSE: 新しい論文が消化された際に、その内容が
epistemic_status.yaml の反証条件にマッチするかをチェックする。

- 入力: 論文の要約 (Summary), 主張 (Claims)
- 照合: `falsification` フィールドのキーワード/条件
- 出力: 警告リスト (Alerts)
"""

import sys
from pathlib import Path
import yaml

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent
REGISTRY_PATH = PROJECT_ROOT / "kernel" / "epistemic_status.yaml"


# PURPOSE: Load the epistemic status registry from YAML file
def load_registry() -> dict:
    """Load the epistemic status registry"""
    if not REGISTRY_PATH.exists():
        return {}

    try:
        with open(REGISTRY_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return {}


# PURPOSE: Check if a paper's claims match any falsification conditions in the registry
def check_falsification(paper_summary: str, paper_claims: list[str]) -> list[str]:
    """
    Check if the paper matches any falsification conditions.

    Args:
        paper_summary: Abstract or summary of the paper
        paper_claims: List of claims extracted from the paper

    Returns:
        List of alert messages strings
    """
    registry = load_registry()
    patches = registry.get("patches", {})
    alerts = []

    text_content = (paper_summary + " " + " ".join(paper_claims)).lower()

    for patch_id, patch in patches.items():
        falsification = patch.get("falsification", "")
        if not falsification:
            continue

        # Simple keyword matching for now (MVP)
        # In the future, this should use embedding/LLM
        keywords = [k.strip().lower() for k in falsification.split(",")]

        # Check if all keywords are present? Or any?
        # Let's say if >50% of meaningful keywords match
        meaningful_keywords = [k for k in keywords if len(k) > 3]
        if not meaningful_keywords:
            continue

        matches = sum(1 for k in meaningful_keywords if k in text_content)
        match_rate = matches / len(meaningful_keywords)

        if match_rate >= 0.7:  # High confidence match
            alerts.append(
                f"🚨 **Falsification Alert**: This paper may falsify '{patch_id}'\n"
                f"   Condition: {falsification}\n"
                f"   Claim in registry: {patch.get('claim')}"
            )

    return alerts


# PURPOSE: Format a list of alert strings into a single report string
def format_alerts(alerts: list[str]) -> str:
    """Format alerts for display"""
    if not alerts:
        return "✅ No falsification conditions triggered."

    return "\n\n".join(alerts)
