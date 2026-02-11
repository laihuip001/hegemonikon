# PROOF: [L1/定理] <- mekhane/ccl/ CCL→CCLパーサーが必要→macro_registry が担う
"""
CCL Macro Registry

Manages macro definitions (@name) for CCL v2.1.
Supports both built-in macros and user-defined macros via Doxa learning.
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import json


# PURPOSE: A CCL macro definition.
@dataclass
class Macro:
    """A CCL macro definition."""

    name: str
    ccl: str
    description: str
    usage_count: int = 0
    is_builtin: bool = False


# Built-in macros (complex patterns only, high expansion ratio)
BUILTIN_MACROS: Dict[str, Macro] = {
    # === Original Macros ===
    "dig": Macro(
        name="dig",
        ccl="/s+~(/p*/a)_/dia*/o+",
        description="深掘り・思考: 戦略↔環境×判断の振動→判定×認識融合",
        is_builtin=True,
    ),
    "go": Macro(
        name="go",
        ccl="/s+_/ene+",
        description="実行: 詳細戦略から詳細実行へ",
        is_builtin=True,
    ),
    "osc": Macro(
        name="osc",
        ccl="/s~/dia~/noe",
        description="振動: 戦略↔判定↔認識のHub内往復",
        is_builtin=True,
    ),
    "fix": Macro(
        name="fix",
        ccl="/dia+_/ene+_/dia",
        description="修正サイクル: 批判→実行→再批判",
        is_builtin=True,
    ),
    "plan": Macro(
        name="plan",
        ccl="/bou+_/s+_/dia",
        description="計画策定: 意志→戦略→批判",
        is_builtin=True,
    ),
    "learn": Macro(
        name="learn",
        ccl="/dox+*^/u+_/bye+",
        description="学習: 信念のメタ化→対話→永続化",
        is_builtin=True,
    ),
    "nous": Macro(
        name="nous",
        ccl="/u+*^/u^",
        description="問いの深化: 対話×メタ→メタ対話 (νοῦς)",
        is_builtin=True,
    ),
    # === Prompt Library Digest (2026-01-29) ===
    # 安直版を削除し、本質的マッピングのみ残す
    # CoT/ToT/StepBack/Verifier → WF 派生として実装 (/noe --mode=cot 等)
    # Reflection → 既存 /dia --mode=cold_mirror で表現可能
    "kyc": Macro(
        name="kyc",
        ccl="~(/sop_/noe_/ene_/dia-)",
        description="κύκλος: 観察→推論→行動→判定の振動サイクル + Focused ReAct (焦点維持・早期終了)",
        is_builtin=True,
    ),
    "wake": Macro(
        name="wake",
        ccl="/boot+_@dig_@plan",
        description="目覚め: 詳細ブート→深掘り→計画のセッション開始シーケンス",
        is_builtin=True,
    ),
    # === v2.5 Macros ===
    "tak": Macro(
        name="tak",
        ccl="/s1_F:3{/sta~/chr}_F:3{/kho~/zet}_I:gap{/sop}_/euk_/bou",
        description="タスク整理: スケール→基準×時間→空間×探求→ギャップ調査→好機→意志",
        is_builtin=True,
    ),
    "v": Macro(
        name="v",
        ccl="/kho{git_diff}_@fix_/pra{test}_/pis_/dox",
        description="自己検証: スコープ検出→修正サイクル→テスト→確信度→Doxa永続化",
        is_builtin=True,
    ),
    "why": Macro(
        name="why",
        ccl="F:5{/zet{why}}_/noe{root_cause}",
        description="Five Whys: 5回問い→深い認識で根本原因を発見",
        is_builtin=True,
    ),
    "eat": Macro(
        name="eat",
        ccl="/mek{digest}_/ene{mapping}_/dia{quality}_/dox",
        description="消化: 調理→マッピング→品質判定→永続化",
        is_builtin=True,
    ),
    "fit": Macro(
        name="fit",
        ccl="/dia{naturality}_/pis{integration}",
        description="消化品質診断: 可換性検証→統合確認",
        is_builtin=True,
    ),
    "lex": Macro(
        name="lex",
        ccl="/dia{expression}_/gno{feedback}",
        description="表現分析: プロンプト表現の批判→フィードバック",
        is_builtin=True,
    ),
    "vet": Macro(
        name="vet",
        ccl="/dia+{cross_model}_/epi{verify}_/pis",
        description="Cross-Model監査: 敵対的検証→知識昇格→確信度",
        is_builtin=True,
    ),
}


# PURPOSE: Registry for CCL macros.
class MacroRegistry:
    """Registry for CCL macros."""

    DEFAULT_PATH = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "ccl_macros.json"

    # PURPOSE: Initialize the macro registry.
    def __init__(self, path: Optional[Path] = None):
        """
        Initialize the macro registry.

        Args:
            path: Path to user macros file
        """
        self.path = path or self.DEFAULT_PATH
        self.user_macros: Dict[str, Macro] = {}
        self._load()

    # PURPOSE: Load user macros from file.
    def _load(self):
        """Load user macros from file."""
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                for item in data:
                    macro = Macro(**item)
                    self.user_macros[macro.name] = macro
            except (json.JSONDecodeError, TypeError):
                pass  # TODO: Add proper error handling

    # PURPOSE: Save user macros to file.
    def _save(self):
        """Save user macros to file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(m) for m in self.user_macros.values()]
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    # PURPOSE: Get a macro by name.
    def get(self, name: str) -> Optional[Macro]:
        """
        Get a macro by name.

        Args:
            name: Macro name (without @)

        Returns:
            Macro if found, None otherwise
        """
        # Check builtins first
        if name in BUILTIN_MACROS:
            return BUILTIN_MACROS[name]
        # Then user macros
        return self.user_macros.get(name)

    # PURPOSE: Define a new user macro.
    def define(self, name: str, ccl: str, description: str = "") -> Macro:
        """
        Define a new user macro.

        Args:
            name: Macro name (without @)
            ccl: CCL expression
            description: Human-readable description

        Returns:
            Created macro
        """
        macro = Macro(name=name, ccl=ccl, description=description)
        self.user_macros[name] = macro
        self._save()
        return macro

    # PURPOSE: Record that a macro was used.
    def record_usage(self, name: str):
        """Record that a macro was used."""
        macro = self.get(name)
        if macro and not macro.is_builtin:
            macro.usage_count += 1
            self._save()

    # PURPOSE: List all available macros.
    def list_all(self) -> List[Macro]:
        """List all available macros."""
        all_macros = list(BUILTIN_MACROS.values()) + list(self.user_macros.values())
        return sorted(all_macros, key=lambda m: (-m.is_builtin, m.name))

    # PURPOSE: Check if a CCL pattern should be suggested as a macro.
    def suggest_from_pattern(self, ccl: str, threshold: int = 3) -> bool:
        """
        Check if a CCL pattern should be suggested as a macro.

        Args:
            ccl: CCL expression
            threshold: Minimum operators to consider for macro

        Returns:
            True if pattern is complex enough for macro
        """
        # Count operators in the expression
        operators = ["_", "~", "*", "+", "-", "^", "/"]
        count = sum(1 for c in ccl if c in operators)
        return count >= threshold
