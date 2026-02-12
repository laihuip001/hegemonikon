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


# PURPOSE: の統一的インターフェースを実現する
@dataclass
# PURPOSE: A CCL macro definition.
class Macro:
    """A CCL macro definition."""

    name: str
    ccl: str
    description: str
    usage_count: int = 0
    is_builtin: bool = False


# Built-in macros — ccl-*.md の正規定義に同期 (2026-02-11)
BUILTIN_MACROS: Dict[str, Macro] = {
    # === Core Macros (ccl-*.md 由来) ===
    "build": Macro(
        name="build",
        ccl="/bou-_/chr_/kho_/s+_/ene+_V:{/dia-}_I:[✓]{M:{/dox-}}",
        description="構築: 目的簡略→資源→場→戦略→実行→判定→✓時記録",
        is_builtin=True,
    ),
    "dig": Macro(
        name="dig",
        ccl="/s+~(/p*/a)_/dia*/o+",
        description="深掘り: 戦略↔環境×判断の振動→判定×認識融合",
        is_builtin=True,
    ),
    "fix": Macro(
        name="fix",
        ccl="/tel_C:{/dia+_/ene+}_I:[✓]{M:{/dox-}}",
        description="修正: 判定+実行のチェック→成功時記録",
        is_builtin=True,
    ),
    "ground": Macro(
        name="ground",
        ccl="/tak-*/bou+{6w3h}~/p-_/ene-",
        description="落とす: 整理×意志の融合→条件縮小→実行縮小",
        is_builtin=True,
    ),
    "kyc": Macro(
        name="kyc",
        ccl="C:{/sop_/noe_/ene_/dia-}",
        description="κύκλος: 観察→推論→行動→判定のチェック",
        is_builtin=True,
    ),
    "learn": Macro(
        name="learn",
        ccl="/dox+_*^/u+_M:{/bye+}",
        description="学習: 信念記録→メモ化(対話のメタ化)→終了時記録",
        is_builtin=True,
    ),
    "nous": Macro(
        name="nous",
        ccl="R:{F:[×2]{/u+*^/u^}}_M:{/dox-}",
        description="問いの深化: 再帰(2回対話のメタ化)→記録",
        is_builtin=True,
    ),
    "osc": Macro(
        name="osc",
        ccl="R:{F:[/s,/dia,/noe]{L:[x]{x~x+}}, ~(/h*/k)}",
        description="振動: 各WFをλ振動→動機×文脈で検証",
        is_builtin=True,
    ),
    "plan": Macro(
        name="plan",
        ccl="/bou+_/s+~(/p*/k)_V:{/dia}",
        description="段取り: 意志→戦略↔環境×文脈の振動→判定検証",
        is_builtin=True,
    ),
    "proof": Macro(
        name="proof",
        ccl="/kat_V:{/noe~/dia}_I:[✓]{/ene{PROOF.md}}_E:{/ene{_limbo/}}",
        description="裁く: 認識↔判定の検証→成功時PROOF.md生成→失敗時limbo",
        is_builtin=True,
    ),
    "tak": Macro(
        name="tak",
        ccl="/s1_F:[×3]{/sta~/chr}_F:[×3]{/kho~/zet}_I:[∅]{/sop}_/euk_/bou",
        description="捌く: スケール→基準×活用→場×探求→∅時調査→好機→意志",
        is_builtin=True,
    ),
    "vet": Macro(
        name="vet",
        ccl="/kho{git_diff}_C:{V:{/dia+}_/ene+}_/pra{test}_M:{/pis_/dox}",
        description="確かめる: diff確認→判定+実行チェック→テスト→確信度+信念記録",
        is_builtin=True,
    ),
    # === Utility Macros ===
    "go": Macro(
        name="go",
        ccl="/s+_/ene+",
        description="即実行: 詳細戦略→詳細実行",
        is_builtin=True,
    ),
    "wake": Macro(
        name="wake",
        ccl="/boot+_@dig_@plan",
        description="目覚め: ブート→深掘り→計画",
        is_builtin=True,
    ),
    "why": Macro(
        name="why",
        ccl="F:5{/zet{why}}_/noe{root_cause}",
        description="Five Whys: 5回問い→根本原因認識",
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

    # PURPOSE: a new user macro の概念を明確にする
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
