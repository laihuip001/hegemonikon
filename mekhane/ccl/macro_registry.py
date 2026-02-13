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


# Built-in macros — Single Source of Truth: hermeneus/src/macros.py + ccl-*.md
# 正規定義: .agent/workflows/ccl-*.md → hermeneus/src/macros.py BUILTIN_MACROS
# この変数は上記から自動生成される (二重定義の解消)
def _build_macro_dict() -> Dict[str, "Macro"]:
    """hermeneus の get_all_macros() (全ソース統合) から Macro dict を生成"""
    try:
        from hermeneus.src.macros import get_all_macros
        all_macros = get_all_macros()
    except ImportError:
        # hermeneus が利用不可の場合は空辞書 (graceful degradation)
        return {}

    result: Dict[str, "Macro"] = {}
    for name, ccl in all_macros.items():
        result[name] = Macro(
            name=name,
            ccl=ccl,
            description=f"@{name} macro (auto-synced from hermeneus)",
            is_builtin=True,
        )
    return result


BUILTIN_MACROS: Dict[str, Macro] = _build_macro_dict()



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
