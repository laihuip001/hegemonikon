# PROOF: [L2/インフラ] <- mekhane/ccl/operator_loader.py
"""operators.md の SSOT パーサー。

operators.md の Markdown テーブルから演算子定義を抽出し、
spec_injector / failure_db が参照する統一辞書を提供する。

>>> from mekhane.ccl.operator_loader import load_operators
>>> ops = load_operators()
>>> ops['+']['名称']
'深化'
"""

from __future__ import annotations

import hashlib
import re
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


# PURPOSE: operators.md から抽出された演算子定義
@dataclass(frozen=True)
class OperatorDef:
    """operators.md から抽出された演算子定義。"""
    symbol: str
    name: str        # 名称 (日本語)
    effect: str      # 作用/認知的意味
    category: str    # セクション名 (e.g. "1.1 強度演算子")
    is_dangerous: bool = False  # ⚠️ を含むか
    is_compound: bool = False   # 2文字以上の複合演算子か


# PURPOSE: operators.md のテーブル行から演算子を抽出する正規表現
# | `+` | 深化 | 詳細な根拠を追加。... | のような行にマッチ
_TABLE_ROW_RE = re.compile(
    r'^\|\s*`([^`]+)`\s*\|'   # 記号 (バッククォート内)
    r'\s*([^|]+?)\s*\|'        # 名称
    r'\s*([^|]+?)\s*\|',       # 3列目 (作用/認知的意味)
    re.MULTILINE,
)

# PURPOSE: セクション見出しの正規表現
_SECTION_RE = re.compile(r'^###?\s+(\d+\.\d+\s+.+)$', re.MULTILINE)

# operators.md のデフォルトパス
_DEFAULT_PATH = Path(__file__).parent.parent.parent / "ccl" / "operators.md"

# operators.md テーブルに存在しないがコアとして必要な演算子
# (SSOT に追加すべきだが、パーサー堅牢性のためフォールバックとして定義)
_FALLBACK_OPERATORS = [
    ("*^", "融合上昇", "融合 + メタ分析（⚠️ 両セクション必要）"),
    ("?", "照会", "制約・確信度の確認"),
]


# PURPOSE: operators.md を解析して演算子辞書を返す
def load_operators(
    operators_path: Optional[Path] = None,
) -> Dict[str, OperatorDef]:
    """operators.md をパースして演算子辞書を返す。

    Returns:
        Dict[symbol, OperatorDef]: 演算子記号 → 定義のマッピング
    """
    path = operators_path or _DEFAULT_PATH
    if not path.exists():
        warnings.warn(f"operators.md が見つかりません: {path}")
        return {}

    content = path.read_text(encoding="utf-8")
    operators: Dict[str, OperatorDef] = {}

    # セクション位置をインデックス化
    sections: List[tuple] = []
    for m in _SECTION_RE.finditer(content):
        sections.append((m.start(), m.group(1).strip()))

    # 各テーブル行を解析
    for m in _TABLE_ROW_RE.finditer(content):
        symbol = m.group(1).strip()
        name = m.group(2).strip()
        effect = m.group(3).strip()

        # ヘッダ行を除外
        if symbol in ("記号",) or name in ("名称",):
            continue
        # セパレータ行を除外 (2文字以上の場合のみ — '-' 単体は CCL 演算子)
        if len(symbol) >= 2 and set(symbol) <= {"-", ":"}:
            continue

        # セクションを逆引き
        pos = m.start()
        category = ""
        for sec_start, sec_name in reversed(sections):
            if sec_start < pos:
                category = sec_name
                break

        # エスケープされたパイプを復元
        symbol = symbol.replace("\\|\\|", "||")

        op = OperatorDef(
            symbol=symbol,
            name=name,
            effect=effect,
            category=category,
            is_dangerous="⚠️" in effect or "⚠️" in content[max(0, m.end()):m.end() + 200],
            is_compound=len(symbol) >= 2,
        )
        operators[symbol] = op

    # フォールバック: operators.md テーブルにない演算子を補完
    for sym, name, effect in _FALLBACK_OPERATORS:
        if sym not in operators:
            operators[sym] = OperatorDef(
                symbol=sym,
                name=name,
                effect=effect,
                category="fallback",
                is_dangerous="⚠️" in effect,
                is_compound=len(sym) >= 2,
            )

    return operators


# PURPOSE: operators.md のハッシュを取得 (変更検知用)
def get_operators_hash(operators_path: Optional[Path] = None) -> str:
    """operators.md の SHA-256 ハッシュを返す。"""
    path = operators_path or _DEFAULT_PATH
    if not path.exists():
        return ""
    content = path.read_bytes()
    return hashlib.sha256(content).hexdigest()[:16]


# PURPOSE: spec_injector 互換の辞書形式に変換
def to_definitions_dict(
    operators: Dict[str, OperatorDef],
) -> tuple:
    """(compound_dict, single_dict, all_dict) を返す。

    spec_injector の COMPOUND_OPERATORS / OPERATOR_DEFINITIONS / ALL_OPERATORS
    互換のフォーマット。
    """
    compound: Dict[str, Dict[str, str]] = {}
    single: Dict[str, Dict[str, str]] = {}

    for sym, op in operators.items():
        entry = {"名称": op.name, "作用": op.effect}
        if op.is_compound:
            compound[sym] = entry
        else:
            single[sym] = entry

    all_ops = {**compound, **single}
    return compound, single, all_ops


# PURPOSE: 危険演算子のセットを取得
def get_dangerous_operators(
    operators: Optional[Dict[str, OperatorDef]] = None,
) -> set:
    """⚠️ マーク付きの演算子記号セットを返す。"""
    if operators is None:
        operators = load_operators()
    return {sym for sym, op in operators.items() if op.is_dangerous}


if __name__ == "__main__":
    ops = load_operators()
    print(f"=== operators.md パース結果: {len(ops)} 演算子 ===")
    print(f"ハッシュ: {get_operators_hash()}")
    print()

    compound, single, all_ops = to_definitions_dict(ops)
    print(f"複合演算子: {len(compound)}")
    for sym, d in compound.items():
        print(f"  {sym}: {d['名称']} — {d['作用']}")

    print(f"\n単一演算子: {len(single)}")
    for sym, d in single.items():
        print(f"  {sym}: {d['名称']} — {d['作用']}")

    dangerous = get_dangerous_operators(ops)
    print(f"\n危険演算子: {dangerous}")
