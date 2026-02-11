# PROOF: [L2/インフラ] <- hermeneus/src/ CCL マクロローダー
"""
Hermēneus Macro Loader — ccl/macros/ から標準マクロを読み込む

Synergeia/Pythosis など他プロジェクトが共通マクロを参照するための
統一ローダー。

Usage:
    from hermeneus.src.macros import load_standard_macros, expand_macro
    
    expanded = expand_macro("repeat", ["/noe", "3"])
"""

import re
from pathlib import Path
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field


# ccl/macros/ の場所
CCL_MACROS_DIR = Path(__file__).parent.parent.parent / "ccl" / "macros"


@dataclass
class MacroDefinition:
    """マクロ定義"""
    name: str
    parameters: Dict[str, Any]  # パラメータ名 → デフォルト値/型情報
    expansion: str  # CCL 展開形 (ボディのみ、またはシグネチャ付き)
    description: str
    source_file: Path
    signature: Optional[str] = None  # 明示的なシグネチャ (@macro(args) -> body 形式の場合)


def parse_macro_file(path: Path) -> Optional[MacroDefinition]:
    """
    マクロ定義ファイル (.md) をパース
    
    Supports two formats:
    1. Signature-based (Old):
        ## CCL 展開
        ```ccl
        @macro($param) $target
        →
        ...
        ```
    2. YAML-based (New):
        ## 定義
        ```yaml
        macro: @macro
        parameters: ...
        expansion: |
          ...
        ```
    """
    try:
        content = path.read_text(encoding="utf-8")
    except Exception:
        return None
    
    # マクロ名を抽出
    name_match = re.search(r"#\s*@(\w+)[\s—]", content)
    if not name_match:
        return None
    name = name_match.group(1)
    
    # 目的/説明を抽出
    desc_match = re.search(r"##\s*目的\s*\n\n(.+?)(?=\n##|\n---|\Z)", content, re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""

    # YAML 定義ブロックを探索
    yaml_match = re.search(r"##\s*定義\s*\n+```yaml\n(.+?)```", content, re.DOTALL)
    macro_def = None

    if yaml_match:
        macro_def = _parse_yaml_definition(name, yaml_match.group(1), description, path)

    # 既存フォーマット (Signature-based) または YAML に expansion がない場合の補完
    expansion = ""
    expansion_match = re.search(r"##\s*CCL\s*展開\s*\n```ccl\n(.+?)```", content, re.DOTALL)
    if expansion_match:
        expansion = expansion_match.group(1).strip()

    if macro_def:
        # YAML で expansion が定義されていない、または空の場合、ブロックから取得したものを使用
        if not macro_def.expansion:
            macro_def.expansion = expansion
        return macro_def

    # パラメータ抽出 (簡易 - YAML がない場合のフォールバック)
    params = {}
    param_match = re.search(r"parameters:\s*\n((?:\s+\w+:.*\n)+)", content)
    if param_match:
        for line in param_match.group(1).strip().split("\n"):
            if ":" in line:
                key, val = line.strip().split(":", 1)
                params[key.strip()] = val.strip()

    return MacroDefinition(
        name=name,
        parameters=params,
        expansion=expansion,
        description=description,
        source_file=path,
        signature=None # Expansion string contains signature
    )

def _parse_yaml_definition(name: str, yaml_content: str, description: str, path: Path) -> MacroDefinition:
    """YAML ブロックから定義をパース (簡易パーサー)"""
    lines = yaml_content.split('\n')
    params = {}
    expansion_lines = []
    in_expansion = False
    in_params = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('parameters:'):
            in_params = True
            in_expansion = False
            continue
        elif stripped.startswith('expansion:'):
            in_expansion = True
            in_params = False
            # check for expansion: |
            if '|' in stripped:
                continue
            # if expansion starts on same line (unlikely for multiline but possible)
            parts = stripped.split(':', 1)
            if len(parts) > 1 and parts[1].strip():
                expansion_lines.append(parts[1].strip())
                in_expansion = False # done
            continue
        elif stripped.startswith('macro:'):
            continue

        if in_params:
            # key: value
            if ':' in stripped:
                key, val = stripped.split(':', 1)
                # Parse default value if present e.g. "float (default: 0.3)"
                default_val = None
                val = val.strip()
                default_match = re.search(r"\(default:\s*([^)]+)\)", val)
                if default_match:
                    default_val = default_match.group(1)
                    # Try to convert to float/int/bool
                    try:
                        if '.' in default_val:
                            default_val = float(default_val)
                        elif default_val.lower() in ('true', 'false'):
                            default_val = default_val.lower() == 'true'
                        else:
                            default_val = int(default_val)
                    except ValueError:
                        pass # keep as string

                params[key.strip()] = default_val

        elif in_expansion:
            # Collect expansion lines
            # Be careful not to eat next section if indentation is lost?
            # YAML block ends at ``` so usually safe.
            # But "parameters:" usually comes before "expansion:".
            # What if "parameters:" comes after?
            if stripped.startswith('parameters:'):
                in_params = True
                in_expansion = False
                continue

            expansion_lines.append(line)

    # Normalize expansion lines (remove common indent)
    expansion = "\n".join(expansion_lines)
    
    return MacroDefinition(
        name=name,
        parameters=params,
        expansion=expansion,
        description=description,
        source_file=path,
        signature=None
    )


def load_standard_macros() -> Dict[str, MacroDefinition]:
    """ccl/macros/ から全マクロを読み込む"""
    macros = {}
    
    if not CCL_MACROS_DIR.exists():
        # Fallback to builtins if directory missing
        for name, exp in BUILTIN_MACROS.items():
             macros[name] = MacroDefinition(
                 name=name,
                 parameters={},
                 expansion=exp,
                 description="Builtin macro",
                 source_file=Path("builtin"),
                 signature=None
             )
        return macros
    
    for path in CCL_MACROS_DIR.glob("*.md"):
        macro = parse_macro_file(path)
        if macro:
            macros[macro.name] = macro

    # Add builtins if not present
    for name, exp in BUILTIN_MACROS.items():
        if name not in macros:
             macros[name] = MacroDefinition(
                 name=name,
                 parameters={},
                 expansion=exp,
                 description="Builtin macro",
                 source_file=Path("builtin"),
                 signature=None
             )
    
    return macros


def expand_macro(name: str, args: List[str], kwargs: Dict[str, Any] = None) -> Optional[str]:
    """
    マクロを展開する
    
    Args:
        name: マクロ名 (e.g., "repeat")
        args: 位置引数リスト
        kwargs: キーワード引数辞書 (optional)

    Returns:
        展開された CCL 文字列, または None (展開失敗)
    """
    macros = load_standard_macros()
    if name not in macros:
        return None

    macro = macros[name]
    kwargs = kwargs or {}

    body = macro.expansion.strip()

    # 1. シグネチャベースの展開 (@macro(A, B) -> body)
    if "→" in body:
        parts = body.split("→", 1)
        signature_line = parts[0].strip()
        body = parts[1].strip()

        # シグネチャからパラメータ名を抽出: @name(p1, p2)
        sig_match = re.match(r"@\w+(?:\[.*\])?(?:\(([^)]+)\))?", signature_line)
        if sig_match:
            param_str = sig_match.group(1)
            param_names = [p.strip() for p in param_str.split(",")] if param_str else []

            # 引数マッピング
            mapping = {}
            # 位置引数
            for i, val in enumerate(args):
                if i < len(param_names):
                    mapping[param_names[i]] = val

            # 残りのパラメータは kwargs から、またはそのまま
            for param in param_names:
                val = mapping.get(param)
                if val is None:
                    # check kwargs
                    # if param is $var, key in kwargs might be var
                    key = param.lstrip('$')
                    if key in kwargs:
                        val = str(kwargs[key])

                if val is not None:
                    # Replace $param or param
                    if param.startswith('$'):
                        # e.g. $scope -> session
                        body = body.replace(param, val)
                    else:
                        # e.g. A -> /foo
                        # Use simple replace for now as previously decided
                        body = body.replace(param, val)

            return body

    # 2. YAML ベースまたはパラメータ指定なしの展開
    # パラメータ定義がある場合
    mapping = macro.parameters.copy() # Start with defaults

    param_keys = list(macro.parameters.keys())

    for i, val in enumerate(args):
        if i < len(param_keys):
            mapping[param_keys[i]] = val

    for k, v in kwargs.items():
        if k in mapping:
            mapping[k] = v

    # YAML defined macros usually use $param in expansion
    for key, val in mapping.items():
        if val is not None:
            # Replace $key
            body = body.replace(f"${key}", str(val))

    return body.strip()


def get_macro_registry() -> Dict[str, str]:
    """Expander 互換形式でマクロレジストリを返す"""
    macros = load_standard_macros()
    registry = {}
    
    for name, macro in macros.items():
        if "→" in macro.expansion:
            parts = macro.expansion.split("→")
            if len(parts) >= 2:
                registry[name] = parts[1].strip().split("\n")[0]
        else:
            registry[name] = macro.expansion.strip().split("\n")[0]
    
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
