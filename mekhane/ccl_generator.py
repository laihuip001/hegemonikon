# PROOF: [L1/定理] <- mekhane/ CCL→実行基盤が必要
"""
CCL Generator (v1.0)

Converts natural language intents into Cognitive Control Language (CCL) v2.0 expressions.
Uses simple heuristic-based generation for now (Phase 1).
Future versions will use LLM for complex generation.

Usage:
    from mekhane.ccl_generator import generate_ccl
    ccl = generate_ccl("ブログ記事を分析して改善案を出す")
    # Output: /s_*/dia
"""

import re
from typing import List, Dict

# Simple keyword mapping for Phase 1
KEYWORD_MAP = {
    # O-Series
    r"(分析|調査|理解|把握)": "/s",
    r"(認識|本質|意味)": "/noe",
    r"(意志|目標|ゴール|望み)": "/bou",
    r"(問い|疑問|探求|リサーチ)": "/zet",
    r"(実行|作成|実装|やる)": "/ene",
    # S-Series
    r"(設計|計画|戦略|構成)": "/s",
    r"(方法|ツール|手段)": "/mek",
    r"(基準|評価|テスト|チェック)": "/dia",  # A2/S3 mapping
    # Modifiers
    r"(詳細|詳しく|具体的|深堀り)": "+",
    r"(要約|シンプル|簡単|概要)": "-",
    r"(メタ|俯瞰|全体|なぜ)": "^",
    r"(具体化|実践的|落とし込む)": "/",
    # Structure
    r"(と|and|そして)": "_",  # Sequence default
    r"(から|→|して)": "_",
    r"(同時|並行|融合)": "*",
    r"(往復|対話|交互)": "~",
}


# PURPOSE: Generate a simple CCL expression from intent string.
def generate_ccl(intent: str) -> str:
    """
    Generate a simple CCL expression from intent string.
    This is a deterministic placeholder for the LLM-based generator.
    """
    # Normalize
    intent = intent.lower()

    # 1. Detect Loop/Iteration
    loop_match = re.search(r"(\d+)回", intent)
    if loop_match:
        count = loop_match.group(1)
        # Simplify intent by removing the loop part
        inner_intent = re.sub(r"\d+回(繰り返す|ループ)?", "", intent).strip()
        inner_ccl = _generate_inner_ccl(inner_intent)
        return f"F:×{count}{{ {inner_ccl} }}"

    return _generate_inner_ccl(intent)


# PURPOSE: generate_inner_ccl — システムの内部処理
def _generate_inner_ccl(intent: str) -> str:
    # Heuristic: Find all operators in order
    ops = []

    # Scan for keywords
    # This is very naive; a real implementation needs checking positions
    # For now, we prioritize specific keywords

    if "詳細" in intent and "実行" in intent:
        return "/s+_/ene+"

    if "分析" in intent or "調査" in intent:
        ops.append("/s")
    if "判定" in intent or "評価" in intent:
        ops.append("/dia")
    if "実行" in intent or "実装" in intent:
        ops.append("/ene")

    if not ops:
        return "/u"  # Fallback to user inquiry

    # Join with sequence by default
    return "_".join(ops)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        print(generate_ccl(sys.argv[1]))
