# PROOF: [L2/品質] <- mekhane/dendron/ A2→反証パターン検出→matcher が担う
# PURPOSE: 反証パターンマッチャー (Falsification Matcher)
"""
Falsification Matcher — 反証パターンの検出

コードベース内の「誤りやすいパターン」や「既知のアンチパターン」を、
構造的解析により検出する。Basanos の一部として機能する。
"""

import ast
from dataclasses import dataclass
from typing import List, Optional

# PURPOSE: パターンマッチ結果
@dataclass
class MatchResult:
    pattern_name: str
    line: int
    message: str

# PURPOSE: ASTを用いたパターンマッチング
class FalsificationMatcher:
    PATTERNS = {
        "swallow_exception": "except Exception: pass",
        "mutable_default": "def f(x=[]): ...",
    }

    # PURPOSE: ASTツリーに対してマッチング実行
    def match(self, tree: ast.AST) -> List[MatchResult]:
        matches = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if isinstance(node.body[0], ast.Pass):
                    matches.append(MatchResult(
                        "swallow_exception",
                        node.lineno,
                        "Exception swallowed without logging"
                    ))
        return matches
