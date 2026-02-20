# PROOF: [L2/品質] <- mekhane/dendron/ A2→パターン認識→FalsificationMatcher
"""
Falsification Matcher - 反証可能性パターンマッチャー

ASTノードを解析し、既知の反証可能性パターンと照合する。
"""

import ast
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any


class PatternType(Enum):
    """パターンタイプ"""
    FALSIFIABLE = "falsifiable"       # 反証可能 (正常)
    TAUTOLOGY = "tautology"           # トートロジー (常に真)
    UNFALSIFIABLE = "unfalsifiable"   # 反証不可能 (定義など)
    UNKNOWN = "unknown"               # 不明


@dataclass
class MatchResult:
    """マッチング結果"""
    is_falsifiable: bool
    pattern_type: PatternType
    reason: str
    confidence: float


class FalsificationMatcher:
    """反証可能性パターンマッチャー"""

    def match(self, node: ast.AST) -> MatchResult:
        """ASTノードを解析し、結果を返す"""

        # 1. 定数 (True, 1, "string") -> Tautology
        if isinstance(node, (ast.Constant, ast.NameConstant)):  # NameConstant for Py3.7-
            val = node.value
            if val:
                return MatchResult(False, PatternType.TAUTOLOGY, "Constant True value", 1.0)
            else:
                # assert False は到達不能コードの明示などに使われるため、Falsifiable扱い
                return MatchResult(True, PatternType.FALSIFIABLE, "Explicit failure", 1.0)

        # 2. 比較 (==, !=, >, <)
        if isinstance(node, ast.Compare):
            return self._check_compare(node)

        # 3. 関数呼び出し (is_valid(), check())
        if isinstance(node, ast.Call):
            # 一般に関数呼び出しは副作用や外部状態に依存するため反証可能とみなす
            return MatchResult(True, PatternType.FALSIFIABLE, "Function call", 0.8)

        # 4. ブール演算 (and, or, not)
        if isinstance(node, ast.BoolOp):
            return self._check_bool_op(node)

        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                # not X -> X の反転
                inner = self.match(node.operand)
                return MatchResult(
                    inner.is_falsifiable,
                    inner.pattern_type,
                    f"Not({inner.reason})",
                    inner.confidence
                )

        # デフォルト: 変数などは値によって変わるため反証可能と仮定
        return MatchResult(True, PatternType.UNKNOWN, "Unknown structure", 0.5)

    def _check_compare(self, node: ast.Compare) -> MatchResult:
        """比較式のチェック"""
        left = node.left
        # 単純な左辺 == 右辺 の場合
        if len(node.ops) == 1 and len(node.comparators) == 1:
            op = node.ops[0]
            right = node.comparators[0]

            # 同一性のチェック (1 == 1, "a" == "a")
            if self._is_same_literal(left, right):
                return MatchResult(False, PatternType.TAUTOLOGY, "Identical literals comparison", 1.0)

            # 型チェック (type(x) == int) -> 反証可能

        return MatchResult(True, PatternType.FALSIFIABLE, "Comparison", 0.9)

    def _check_bool_op(self, node: ast.BoolOp) -> MatchResult:
        """ブール演算のチェック"""
        # 全てが Tautology なら Tautology
        # ひとつでも Falsifiable なら Falsifiable

        results = [self.match(val) for val in node.values]

        if isinstance(node.op, ast.And):
            # A and B: 両方真である必要がある
            # もし片方が False 定数なら常に False (Falsifiable)
            # 両方 Tautology なら Tautology
            if all(r.pattern_type == PatternType.TAUTOLOGY for r in results):
                return MatchResult(False, PatternType.TAUTOLOGY, "All AND conditions are tautologies", 1.0)
            return MatchResult(True, PatternType.FALSIFIABLE, "AND condition", 0.8)

        if isinstance(node.op, ast.Or):
            # A or B: どちらかが真なら真
            # ひとつでも Tautology があれば全体が Tautology
            if any(r.pattern_type == PatternType.TAUTOLOGY for r in results):
                return MatchResult(False, PatternType.TAUTOLOGY, "OR condition contains tautology", 1.0)
            return MatchResult(True, PatternType.FALSIFIABLE, "OR condition", 0.8)

        return MatchResult(True, PatternType.UNKNOWN, "Unknown BoolOp", 0.5)

    def _is_same_literal(self, left: ast.AST, right: ast.AST) -> bool:
        """リテラルが同一か判定"""
        if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
            return left.value == right.value
        return False
