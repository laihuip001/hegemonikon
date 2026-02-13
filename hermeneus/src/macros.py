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
# PURPOSE: [L2-auto] マクロ定義
class MacroDefinition:
    """マクロ定義"""
    name: str
    parameters: Dict[str, str]  # パラメータ名 → 型/説明
    expansion: str  # CCL 展開形
    description: str
    source_file: Path


# PURPOSE: マクロ定義ファイル (.md) をパース
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


# PURPOSE: ccl/macros/ から全マクロを読み込む
def load_standard_macros() -> Dict[str, MacroDefinition]:
    """ccl/macros/ から全マクロを読み込む"""
    macros = {}
    
    if not CCL_MACROS_DIR.exists():
        return macros
    
    for path in CCL_MACROS_DIR.glob("*.md"):
        macro = parse_macro_file(path)
        if macro and macro.expansion:  # 空展開は除外 (YAML multiline 未対応)
            macros[macro.name] = macro
    
    return macros


# PURPOSE: .agent/workflows/ccl-*.md からマクロ展開形を読み込む
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


# PURPOSE: マクロ名から展開形を取得 (全ソース検索)
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


# PURPOSE: Expander 互換形式でマクロレジストリを返す
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
# v2: hub-only 9定理を既存+新規マクロに統合 (DX-008 対応)
BUILTIN_MACROS = {
    # 問いの深化 — 認知昇華: Prior→Likelihood→Posterior
    "nous": "/pro_/s-_R:{F:[×2]{/u+*^/u^}}_~(/noe*/dia)_/pis_/dox-",
    "dig": "/pro_/s+~(/p*/a)_/ana_/dia*/o+_/pis",
    # S-series (設計)
    "plan": "/bou+_/chr_/s+~(/p*/k)_V:{/dia}_/pis_/dox-",
    "build": "/bou-_/chr_/kho_/s+_/ene+_V:{/dia-}_I:[✓]{/dox-}",  # ✅ 十分
    "tak": "/s1_F:[×3]{/sta~/chr}_F:[×3]{/kho~/zet}_I:[∅]{/sop}_/euk_/bou",  # ✅ 十分
    # H-series (動機)
    "osc": "R:{F:[/s,/dia,/noe]{L:[x]{x~x+}}, ~(/h*/k)}",  # ✅ 十分
    "learn": "/pro_/dox+_F:[×2]{/u+~(/noe*/dia)}_~(/h*/k)_/pis_/bye+",
    # A-series (精密)
    "fix": "/kho_/tel_C:{/dia+_/ene+}_I:[✓]{/pis_/dox-}",
    "vet": "/kho{git_diff}_C:{V:{/dia+}_/ene+}_/pra{test}_/pis_/dox",  # ✅ 十分
    "proof": '/kat_V:{/noe~/dia}_I:[✓]{/ene{PROOF.md}}_E:{/ene{_limbo/}}',  # ✅ 十分
    "syn": "/kho_/s-_/pro_/dia+{synteleia}_~(/noe*/dia)_V:{/pis+}_/dox-",
    # P-series (条件)
    "ground": "/pro_/tak-*/bou+{6w3h}~/p-_/ene-_/pis",
    "ready": "/bou-_/pro_/kho_/chr_/euk_/tak-_~(/h*/k)_/pis",
    # K-series (文脈)
    "kyc": "/pro_C:{/sop_/noe_/ene_/dia-}_/pis_/dox-",
    # Hub-only 統合 (DX-008)
    "feel": "/pro_/ore~(/pis_/ana)_/dox-",
    "clean": "/s-_/kat_/sym~(/tel_/dia-)_/pis",
    # 反復マクロ (Repetition Principle — 認知の絡み合い再現)
    "chew": "/s-_/pro_F:[×3]{/eat+~(/noe*/dia)}_~(/h*/k)_@proof_/pis_/dox-",
    "read": "/s-_/pro_F:[×3]{/m.read~(/noe*/dia)}_/ore_~(/h*/k)_/pis_/dox-",
    # 方向性マクロ (FuseOuter + Pipeline)
    "helm": "/pro_/kho_/bou+*%/zet+|>/u++_~(/h*/k)_/pis_/dox-",
    # FuseOuter マクロ
    "weigh": "/bou*%/noe",
    "scan": "/s*%/dia",
    # Utility マクロ
    "go": "/s+_/ene+",
    "wake": "/boot+_@dig_@plan",
    "why": "F:5{/zet{why}}_/noe{root_cause}",
    "eat": "/mek{digest}_/ene{mapping}_/dia{quality}_/dox",
    "fit": "/dia{naturality}_/pis{integration}",
    "lex": "/dia{expression}_/gno{feedback}",
    # Legacy (互換用)
    "think": "/noe+ >> V[] < 0.3",
    "review": "/dia+ _ /pre+ _ /sta.done",
}


# PURPOSE: 全マクロを取得 (統合)
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
