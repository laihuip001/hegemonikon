# PROOF: [L1/定理] <- mekhane/ccl/ CCL→CCLパーサーが必要→pattern_cache が担う
"""
Pattern Cache for CCL v2.0

Layer 3 of the 4-layer fallback system.
Static heuristic-based pattern matching (migrated from ccl_generator.py v1.0).
"""

import re
from typing import Optional


# PURPOSE: Static pattern matcher (Layer 3).
class PatternCache:
    """
    Static pattern matcher (Layer 3).

    Uses keyword-based heuristics to generate CCL expressions.
    This is the fallback when LLM and Doxa patterns fail.
    """

    # Keyword to workflow mapping
    KEYWORD_MAP = {
        # O-Series
        r"(分析|調査|理解|把握)": "/s",
        r"(認識|本質|意味|深く考)": "/noe",
        r"(意志|目標|ゴール|望み|したい)": "/bou",
        r"(問い|疑問|探求|リサーチ|調べ)": "/zet",
        r"(実行|作成|実装|やる|する)": "/ene",
        # S-Series
        r"(設計|計画|戦略|構成|プラン)": "/s",
        r"(方法|ツール|手段|生成)": "/mek",
        r"(基準|評価|テスト|チェック)": "/sta",
        # A-Series
        r"(判定|判断|審査|批評|レビュー)": "/dia",
    }

    # Modifier keywords
    MODIFIER_MAP = {
        r"(詳細|詳しく|具体的|深堀り|もっと)": "+",
        r"(要約|シンプル|簡単|概要|短く)": "-",
        r"(メタ|俯瞰|全体|なぜ|理由)": "^",
        r"(具体化|実践的|落とし込む)": "/",
    }

    # Structure keywords
    STRUCTURE_MAP = {
        r"(と|and|そして|してから|して)": "_",
        r"(同時|並行|融合|統合)": "*",
        r"(往復|対話|交互|行き来)": "~",
    }

    # PURPOSE: Generate CCL from intent using heuristics.
    def generate(self, intent: str) -> Optional[str]:
        """
        Generate CCL from intent using heuristics.

        Args:
            intent: Natural language intent

        Returns:
            CCL expression or None if no match
        """
        intent_lower = intent.lower()

        # Check for loop pattern
        loop_match = re.search(r"(\d+)回", intent)
        if loop_match:
            count = loop_match.group(1)
            inner_intent = re.sub(r"\d+回(繰り返す|ループ)?", "", intent).strip()
            inner_ccl = self._generate_inner(inner_intent)
            if inner_ccl:
                return f"F:×{count}{{ {inner_ccl} }}"

        return self._generate_inner(intent_lower)

    # PURPOSE: Generate the inner CCL expression.
    def _generate_inner(self, intent: str) -> Optional[str]:
        """Generate the inner CCL expression."""
        workflows = []
        modifiers = []

        # Find workflows
        for pattern, workflow in self.KEYWORD_MAP.items():
            if re.search(pattern, intent):
                if workflow not in workflows:
                    workflows.append(workflow)

        # Find modifiers
        for pattern, modifier in self.MODIFIER_MAP.items():
            if re.search(pattern, intent):
                modifiers.append(modifier)

        # No workflows found
        if not workflows:
            return None

        # Apply modifiers to workflows
        modifier_str = "".join(modifiers[:1])  # Only first modifier

        # Determine structure
        structure = "_"  # Default to sequence
        for pattern, struct in self.STRUCTURE_MAP.items():
            if re.search(pattern, intent):
                structure = struct
                break

        # Build expression
        if len(workflows) == 1:
            return f"{workflows[0]}{modifier_str}"
        else:
            return structure.join(f"{w}{modifier_str}" for w in workflows)
