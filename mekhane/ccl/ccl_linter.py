# PROOF: [L2/Infra] <- mekhane/ccl/
"""CCL Linter — CCL 式の静的検証。

operators.md (SSOT) に基づいて CCL 式を検証し、
未定義演算子、矛盾する演算子の組合せ、ネスト深度超過を検出する。

>>> from mekhane.ccl.ccl_linter import lint
>>> warnings = lint("/noe+$zet")
>>> warnings[0].message
'未定義演算子: $'
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from mekhane.ccl.operator_loader import load_operators, OperatorDef
from mekhane.ccl.spec_injector import ALL_OPERATORS, COMPOUND_OPERATORS, OPERATOR_DEFINITIONS


@dataclass
class LintWarning:
    """Lint 警告。"""
    level: str       # "error", "warning", "info"
    message: str
    position: Optional[int] = None  # CCL 式中の位置


# PURPOSE: 矛盾する演算子ペア
_CONFLICTING_PAIRS = [
    ("+", "-"),   # 深化と縮約は通常同時に使わない
]

# PURPOSE: ネスト深度上限
_MAX_NESTING = 4

# PURPOSE: 演算子でもWF名でもないASCII記号 (CCL 的に未定義の可能性)
_KNOWN_NON_OPERATORS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 \t\n")
# WF/マクロで使うがパースしない文字
_STRUCTURAL_CHARS = set("(){}[]@:,.=|")


def lint(ccl_expr: str) -> List[LintWarning]:
    """CCL 式を静的検証し、警告リストを返す。"""
    warnings: List[LintWarning] = []

    # Rule 1: 未定義演算子の検出
    all_defined = set(ALL_OPERATORS.keys())
    i = 0
    while i < len(ccl_expr):
        ch = ccl_expr[i]
        # 既知の非演算子はスキップ
        if ch in _KNOWN_NON_OPERATORS or ch in _STRUCTURAL_CHARS:
            i += 1
            continue
        # 2文字複合演算子チェック
        if i + 1 < len(ccl_expr):
            bigram = ccl_expr[i:i+2]
            if bigram in COMPOUND_OPERATORS:
                i += 2
                continue
        # 1文字演算子チェック
        if ch in OPERATOR_DEFINITIONS:
            i += 1
            continue
        # Unicode 演算子チェック (∂, ∫, Σ, √ etc.)
        if ch in all_defined:
            i += 1
            continue
        # 未定義
        warnings.append(LintWarning(
            level="warning",
            message=f"未定義演算子: {ch}",
            position=i,
        ))
        i += 1

    # Rule 2: 矛盾する演算子ペア
    found_ops = set()
    for k in ALL_OPERATORS:
        if k in ccl_expr:
            found_ops.add(k)

    for a, b in _CONFLICTING_PAIRS:
        if a in found_ops and b in found_ops:
            warnings.append(LintWarning(
                level="info",
                message=f"演算子 '{a}' と '{b}' が同時に使用されています（意図的か確認してください）",
            ))

    # Rule 3: ネスト深度チェック
    max_depth = 0
    current_depth = 0
    for ch in ccl_expr:
        if ch in "({":
            current_depth += 1
            max_depth = max(max_depth, current_depth)
        elif ch in ")}":
            current_depth -= 1

    if max_depth > _MAX_NESTING:
        warnings.append(LintWarning(
            level="warning",
            message=f"ネスト深度 {max_depth} は推奨上限 {_MAX_NESTING} を超えています（let マクロで分解を推奨）",
        ))

    return warnings


if __name__ == "__main__":
    # Usage example
    test_cases = [
        "/noe+",
        "/noe+$zet",
        "/bou+_/dia-",
        "((({/noe+((/dia))}))",
    ]
    for expr in test_cases:
        result = lint(expr)
        if result:
            print(f"  {expr}:")
            for w in result:
                print(f"    [{w.level}] {w.message}")
        else:
            print(f"  {expr}: OK")
