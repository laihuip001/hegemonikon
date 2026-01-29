"""
CCL Macro Registry

Manages macro definitions (@name) for CCL v2.1.
Supports both built-in macros and user-defined macros via Doxa learning.
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
import json


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
        is_builtin=True
    ),
    "go": Macro(
        name="go",
        ccl="/s+_/ene+",
        description="実行: 詳細戦略から詳細実行へ",
        is_builtin=True
    ),
    "osc": Macro(
        name="osc",
        ccl="/s~/dia~/noe",
        description="振動: 戦略↔判定↔認識のHub内往復",
        is_builtin=True
    ),
    "fix": Macro(
        name="fix",
        ccl="/dia+_/ene+_/dia",
        description="修正サイクル: 批判→実行→再批判",
        is_builtin=True
    ),
    "plan": Macro(
        name="plan",
        ccl="/bou+_/s+_/dia",
        description="計画策定: 意志→戦略→批判",
        is_builtin=True
    ),
    "learn": Macro(
        name="learn",
        ccl="/dox+*^/u+_/bye+",
        description="学習: 信念のメタ化→対話→永続化",
        is_builtin=True
    ),
    "nous": Macro(
        name="nous",
        ccl="/u+*^/u^",
        description="問いの深化: 対話×メタ→メタ対話 (νοῦς)",
        is_builtin=True
    ),
    
    # === Prompt Library Digest (2026-01-29) ===
    # 安直版を削除し、本質的マッピングのみ残す
    # CoT/ToT/StepBack/Verifier → WF 派生として実装 (/noe --mode=cot 等)
    # Reflection → 既存 /dia --mode=cold_mirror で表現可能
    
    "kyc": Macro(
        name="kyc",
        ccl="~(/sop_/noe_/ene_/dia-)",
        description="κύκλος: 観察→推論→行動→判定の振動サイクル + Focused ReAct (焦点維持・早期終了)",
        is_builtin=True
    ),
    "wake": Macro(
        name="wake",
        ccl="/boot+_@dig_@plan",
        description="目覚め: 詳細ブート→深掘り→計画のセッション開始シーケンス",
        is_builtin=True
    ),
}




class MacroRegistry:
    """Registry for CCL macros."""
    
    DEFAULT_PATH = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "ccl_macros.json"
    
    def __init__(self, path: Optional[Path] = None):
        """
        Initialize the macro registry.
        
        Args:
            path: Path to user macros file
        """
        self.path = path or self.DEFAULT_PATH
        self.user_macros: Dict[str, Macro] = {}
        self._load()
    
    def _load(self):
        """Load user macros from file."""
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text())
                for item in data:
                    macro = Macro(**item)
                    self.user_macros[macro.name] = macro
            except (json.JSONDecodeError, TypeError):
                pass
    
    def _save(self):
        """Save user macros to file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(m) for m in self.user_macros.values()]
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
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
    
    def record_usage(self, name: str):
        """Record that a macro was used."""
        macro = self.get(name)
        if macro and not macro.is_builtin:
            macro.usage_count += 1
            self._save()
    
    def list_all(self) -> List[Macro]:
        """List all available macros."""
        all_macros = list(BUILTIN_MACROS.values()) + list(self.user_macros.values())
        return sorted(all_macros, key=lambda m: (-m.is_builtin, m.name))
    
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
        operators = ['_', '~', '*', '+', '-', '^', '/']
        count = sum(1 for c in ccl if c in operators)
        return count >= threshold
