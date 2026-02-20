#!/usr/bin/env python3
# PROOF: [L2/品質] <- mekhane/dendron/ A2→反証可能性→FalsificationChecker
"""
Falsification Checker - 反証可能性チェッカー

BC-14 (FaR - Falsification and Refutation) を実装し、
アサーションが「反証可能性」を持っているか、
または「自明なトートロジー」に陥っていないかをチェックする。

Design:
  - Falsifiable (反証可能): 失敗する可能性のある条件 (例: status == 200)
  - Tautology (トートロジー): 常に真になる条件 (例: True is True)
  - Unfalsifiable (反証不可能): 定義上常に真 (例: x = 1; assert x == 1)
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from .falsification_matcher import FalsificationMatcher, PatternType


# PURPOSE: 反証可能性チェック結果
@dataclass
class FalsificationResult:
    """反証可能性チェック結果"""
    file_path: str
    line: int
    code: str
    is_falsifiable: bool
    pattern_type: PatternType
    reason: str
    confidence: float


# PURPOSE: 反証可能性チェッカー
class FalsificationChecker:
    """反証可能性チェッカー"""
    
    def __init__(self):
        self.matcher = FalsificationMatcher()
        self.results: List[FalsificationResult] = []
    
    # PURPOSE: ファイルをチェックする
    def check_file(self, file_path: str) -> List[FalsificationResult]:
        """ファイルをチェックする"""
        path = Path(file_path)
        if not path.exists():
            return []

        try:
            content = path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=file_path)
            self._visit(tree, file_path, content.splitlines())
            return self.results
        except Exception:
            # パースエラー等は無視
            return []

    # PURPOSE: ASTを走査する
    def _visit(self, node: ast.AST, file_path: str, lines: List[str]):
        """ASTを走査する"""
        for child in ast.walk(node):
            if isinstance(child, ast.Assert):
                self._check_assert(child, file_path, lines)

    # PURPOSE: assert文をチェックする
    def _check_assert(self, node: ast.Assert, file_path: str, lines: List[str]):
        """assert文をチェックする"""
        # ソースコード取得
        start_line = node.lineno - 1
        end_line = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else node.lineno
        code = "\n".join(lines[start_line:end_line]).strip()
        
        # マッチング
        match = self.matcher.match(node.test)
        
        result = FalsificationResult(
            file_path=file_path,
            line=node.lineno,
            code=code,
            is_falsifiable=match.is_falsifiable,
            pattern_type=match.pattern_type,
            reason=match.reason,
            confidence=match.confidence
        )
        self.results.append(result)


# PURPOSE: CLI エントリポイント
def main():
    """CLI エントリポイント"""
    if len(sys.argv) < 2:
        print("Usage: python -m mekhane.dendron.falsification_checker <file_or_dir>")
        sys.exit(1)

    target = Path(sys.argv[1])
    checker = FalsificationChecker()
    
    files = []
    if target.is_file():
        files.append(str(target))
    elif target.is_dir():
        files.extend(str(p) for p in target.glob("**/*.py"))

    for f in files:
        checker.check_file(f)

    # 結果表示
    falsifiable = [r for r in checker.results if r.is_falsifiable]
    tautology = [r for r in checker.results if r.pattern_type == PatternType.TAUTOLOGY]
    unfalsifiable = [r for r in checker.results if not r.is_falsifiable and r.pattern_type != PatternType.TAUTOLOGY]
    
    print(f"Checked {len(files)} files, found {len(checker.results)} assertions.")
    print(f"  ✅ Falsifiable: {len(falsifiable)}")
    print(f"  ❌ Tautology:   {len(tautology)}")
    print(f"  ⚠️ Unfalsifiable: {len(unfalsifiable)}")
    
    if tautology:
        print("\nTautologies found:")
        for r in tautology:
            print(f"  {r.file_path}:{r.line} - {r.code} ({r.reason})")

    sys.exit(1 if tautology else 0)


if __name__ == "__main__":
    main()
