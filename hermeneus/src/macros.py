# PROOF: [L2/インフラ] <- hermeneus/src/ CCL マクロローダー
"""
Hermēneus Macro Loader — ccl/macros/ から標準マクロを読み込む

Synergeia/Pythosis など他プロジェクトが共通マクロを参照するための
統一ローダー。

Usage:
    from hermeneus.src.macros import load_standard_macros, get_macro
    
    macros = load_standard_macros()
    expanded = macros.get("think")  # /noe+ >> V[] < 0.3
"""

import re
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass


# ccl/macros/ の場所
CCL_MACROS_DIR = Path(__file__).parent.parent.parent / "ccl" / "macros"


@dataclass
class MacroDefinition:
    """マクロ定義"""
    name: str
    parameters: Dict[str, str]  # パラメータ名 → 型/説明
    expansion: str  # CCL 展開形
    description: str
    source_file: Path


def parse_macro_file(path: Path) -> Optional[MacroDefinition]:
    """
    マクロ定義ファイル (.md) をパース
    
    Expected format:
        # @macro_name マクロ
        ...
        ## CCL 展開
        ```ccl
        @macro($param) $target
        →
        /wf{...} _$target
        ```
    """
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return None
    
    # マクロ名を抽出 (both "# @name マクロ" and "# @name — Description マクロ")
    name_match = re.search(r"#\s*@(\w+)[\s—]", content)
    if not name_match:
        return None
    name = name_match.group(1)
    
    # パラメータを抽出 (YAML ブロックから)
    params = {}
    param_match = re.search(r"parameters:\s*\n((?:\s+\w+:.*\n)+)", content)
    if param_match:
        for line in param_match.group(1).strip().split("\n"):
            if ":" in line:
                key, val = line.strip().split(":", 1)
                params[key.strip()] = val.strip()
    
    # CCL 展開を抽出
    expansion = ""
    expansion_match = re.search(r"##\s*CCL\s*展開\s*\n```ccl\n(.+?)```", content, re.DOTALL)
    if expansion_match:
        expansion = expansion_match.group(1).strip()
    
    # 目的/説明を抽出
    desc_match = re.search(r"##\s*目的\s*\n\n(.+?)(?=\n##|\n---|\Z)", content, re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""
    
    return MacroDefinition(
        name=name,
        parameters=params,
        expansion=expansion,
        description=description,
        source_file=path,
    )


def load_standard_macros() -> Dict[str, MacroDefinition]:
    """ccl/macros/ から全マクロを読み込む"""
    macros = {}
    
    if not CCL_MACROS_DIR.exists():
        return macros
    
    for path in CCL_MACROS_DIR.glob("*.md"):
        macro = parse_macro_file(path)
        if macro:
            macros[macro.name] = macro
    
    return macros


def get_macro_expansion(name: str) -> Optional[str]:
    """マクロ名から展開形を取得"""
    macros = load_standard_macros()
    if name in macros:
        return macros[name].expansion
    return None


def get_macro_registry() -> Dict[str, str]:
    """
    Expander 互換形式でマクロレジストリを返す
    
    Returns:
        {"macro_name": "CCL expansion string", ...}
    """
    macros = load_standard_macros()
    registry = {}
    
    for name, macro in macros.items():
        # 展開形から変換パターンを抽出
        # 例: "@scoped($scope) $target → /kho{scope=$scope} _$target _/kho{exit}"
        if "→" in macro.expansion:
            parts = macro.expansion.split("→")
            if len(parts) >= 2:
                # シンプルな展開のみ対応
                registry[name] = parts[1].strip().split("\n")[0]
    
    return registry


# 標準マクロ (ハードコード版 - ccl/macros/ が見つからない場合のフォールバック)
BUILTIN_MACROS = {
    "think": "/noe+ >> V[] < 0.3",
    "tak": "/s+ _ /ene",
    "dig": "/zet+ _ /noe+",
    "plan": "/bou+ _ /s+ _ /sta.done",
    "review": "/dia+ _ /pre+ _ /sta.done",
}


def get_all_macros() -> Dict[str, str]:
    """全マクロを取得 (ccl/macros/ + ビルトイン)"""
    result = BUILTIN_MACROS.copy()
    result.update(get_macro_registry())
    return result


# =============================================================================
# Test
# =============================================================================

if __name__ == "__main__":
    print("=== Standard Macros ===")
    macros = load_standard_macros()
    for name, macro in macros.items():
        print(f"@{name}: {macro.description[:50]}...")
    
    print(f"\n=== Total: {len(macros)} macros ===")
    
    print("\n=== Expander Registry ===")
    registry = get_all_macros()
    for name, expansion in registry.items():
        print(f"@{name} → {expansion}")
