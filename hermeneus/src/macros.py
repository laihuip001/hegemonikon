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

# .agent/workflows/ccl-*.md の場所
WF_MACROS_DIR = Path(__file__).parent.parent.parent / ".agent" / "workflows"


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


def load_workflow_macros() -> Dict[str, str]:
    """
    .agent/workflows/ccl-*.md からマクロ展開形を読み込む
    
    各ファイルの以下のパターンを認識:
        > **CCL**: `@name = CCL_EXPANSION`
    
    Returns:
        {"macro_name": "CCL expansion string", ...}
    """
    macros = {}
    
    if not WF_MACROS_DIR.exists():
        return macros
    
    for path in WF_MACROS_DIR.glob("ccl-*.md"):
        # ファイル名からマクロ名を抽出: ccl-build.md → build
        name = path.stem.replace("ccl-", "")
        
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            continue
        
        # パターン: `@name = CCL_EXPANSION`
        match = re.search(r"`@\w+\s*=\s*(.+?)`", content)
        if match:
            expansion = match.group(1).strip()
            macros[name] = expansion
    
    return macros


def get_macro_expansion(name: str) -> Optional[str]:
    """マクロ名から展開形を取得 (全ソース検索)"""
    # 優先順位: ccl-*.md > ccl/macros/*.md > BUILTIN
    wf_macros = load_workflow_macros()
    if name in wf_macros:
        return wf_macros[name]
    
    std_macros = load_standard_macros()
    if name in std_macros:
        return std_macros[name].expansion
    
    if name in BUILTIN_MACROS:
        return BUILTIN_MACROS[name]
    
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


# 標準マクロ (ハードコード版 — ccl-*.md が見つからない場合のフォールバック)
# ccl-*.md 由来の正規定義に同期 (2026-02-11)
BUILTIN_MACROS = {
    # O-series (認知)
    "nous": 'R:{F:[×2]{/u+*^/u^}}_M:{/dox-}',
    "dig": "/s+~(/p*/a)_/dia*/o+",
    # S-series (設計)
    "plan": "/bou+_/s+~(/p*/k)_V:{/dia}",
    "build": "/bou-{goal:define}_/s+_/ene+_V:{/dia-}_I:[pass]{M:{/dox-}}",
    "tak": "/s1_F:[×3]{/sta~/chr}_F:[×3]{/kho~/zet}_I:[gap]{/sop}_/euk_/bou",
    # H-series (動機)
    "osc": "R:{F:[/s,/dia,/noe]{L:[x]{x~x+}}, ~(/h*/k)}",
    "learn": "/dox+_*^/u+_M:{/bye+}",
    # A-series (精密)
    "fix": "C:{/dia+_/ene+}_I:[pass]{M:{/dox-}}",
    "vet": "/kho{git_diff}_C:{V:{/dia+}_/ene+}_/pra{test}_M:{/pis_/dox}",
    "proof": 'V:{/noe~/dia}_I:[pass]{/ene{PROOF.md}}_E:{/ene{_limbo/}}',
    # P-series (条件)
    "ground": "/tak-*/bou+{6w3h}~/p-_/ene-",
    # K-series (文脈)
    "kyc": "C:{/sop_/noe_/ene_/dia-}",
    # Legacy (互換用)
    "think": "/noe+ >> V[] < 0.3",
    "review": "/dia+ _ /pre+ _ /sta.done",
}


def get_all_macros() -> Dict[str, str]:
    """
    全マクロを取得 (統合)
    
    優先順位 (後勝ち):
        1. BUILTIN_MACROS (フォールバック)
        2. ccl/macros/*.md (ファイル定義)
        3. .agent/workflows/ccl-*.md (正規定義 — 最優先)
    """
    result = BUILTIN_MACROS.copy()
    result.update(get_macro_registry())  # ccl/macros/*.md
    result.update(load_workflow_macros())  # ccl-*.md (最優先)
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
