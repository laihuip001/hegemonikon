# PROOF: [L2/インフラ] <- mekhane/ccl/
# Phase 0: CCL 実行前の仕様強制注入

"""
CCL Spec Injector - 仕様強制注入モジュール

CCL 式の実行前に:
1. 使用される演算子を抽出
2. operators.md から仕様を読み込み
3. 理解確認クイズを生成
4. プロンプトに注入
"""

from pathlib import Path
from typing import List, Dict, Set
import re

# 演算子と必須セクションのマッピング
OPERATOR_SECTIONS: Dict[str, str] = {
    "!": "## 全派生同時実行",
    "~": "## 振動",
    "*": "## 融合",
    "^": "## メタ分析",
    "+": "## 詳細展開",
    "-": "## 縮約",
    "_": "## シーケンス",
    "?": "## 照会",
    "\\": "## 反転",
}

# 演算子の正式定義 (operators.md から)
OPERATOR_DEFINITIONS: Dict[str, Dict[str, str]] = {
    "+": {"名称": "深化", "作用": "3-5倍出力、明示的根拠"},
    "-": {"名称": "縮約", "作用": "最小出力、要点のみ"},
    "^": {"名称": "上昇", "作用": "次元↑ メタ層へ"},
    "/": {"名称": "下降", "作用": "次元↓ 具体層へ"},
    "?": {"名称": "照会", "作用": "制約・確信度の確認"},
    "\\": {"名称": "反転", "作用": "視点を逆転（Antistrophē）"},
    "*": {"名称": "融合", "作用": "複数を統合して1出力"},
    "~": {"名称": "振動", "作用": "複数を往復して探索"},
    "_": {"名称": "シーケンス", "作用": "Aの後にBを実行"},
    "!": {"名称": "階乗", "作用": "全派生同時実行（⚠️ 高負荷）"},
}


# PURPOSE: CCL 仕様強制注入器
class SpecInjector:
    """CCL 仕様強制注入器"""

    # PURPOSE: SpecInjector の構成と依存関係の初期化
    def __init__(self, operators_path: Path = None):
        self.operators_path = (
            operators_path
            or Path(__file__).parent.parent.parent / "ccl" / "operators.md"
        )
        self._operators_content: str = None

    # PURPOSE: operators.md の内容をキャッシュ付きで読み込み
    @property
    def operators_content(self) -> str:
        """operators.md の内容をキャッシュ付きで読み込み"""
        if self._operators_content is None:
            if self.operators_path.exists():
                self._operators_content = self.operators_path.read_text(
                    encoding="utf-8"
                )
            else:
                self._operators_content = ""
        return self._operators_content

    # PURPOSE: CCL 式から演算子を抽出
    def parse_operators(self, ccl_expr: str) -> Set[str]:
        """CCL 式から演算子を抽出"""
        operators = set()
        for char in ccl_expr:
            if char in OPERATOR_DEFINITIONS:
                operators.add(char)
        return operators

    # PURPOSE: 演算子仕様ブロックを生成
    def generate_spec_block(self, operators: Set[str]) -> str:
        """演算子仕様ブロックを生成"""
        if not operators:
            return ""

        lines = ["## 使用する演算子の仕様 (必読)\n"]
        lines.append("| 記号 | 名称 | 作用 |")
        lines.append("|:-----|:-----|:-----|")

        for op in sorted(operators):
            if op in OPERATOR_DEFINITIONS:
                defn = OPERATOR_DEFINITIONS[op]
                lines.append(f"| `{op}` | {defn['名称']} | {defn['作用']} |")

        lines.append("")
        return "\n".join(lines)

    # PURPOSE: 理解確認クイズを生成
    def generate_quiz(self, operators: Set[str]) -> str:
        """理解確認クイズを生成"""
        if not operators:
            return ""

        lines = ["## 理解確認 (回答必須)\n"]
        lines.append("以下の質問に回答してから実行してください。\n")

        for i, op in enumerate(sorted(operators), 1):
            if op in OPERATOR_DEFINITIONS:
                defn = OPERATOR_DEFINITIONS[op]
                lines.append(f"**Q{i}**: 演算子 `{op}` の名称と作用は？")
                lines.append(
                    f"**A{i}**: [ここに回答: 名称={defn['名称']}, 作用={defn['作用']}]\n"
                )

        return "\n".join(lines)

    # PURPOSE: 必須出力セクションを生成
    def generate_required_sections(self, operators: Set[str]) -> str:
        """必須出力セクションを生成"""
        if not operators:
            return ""

        lines = ["## 必須出力セクション\n"]
        lines.append("以下のセクションを出力に含めること。\n")

        for op in sorted(operators):
            if op in OPERATOR_SECTIONS:
                lines.append(f"- 演算子 `{op}` → `{OPERATOR_SECTIONS[op]}`")

        lines.append("")
        return "\n".join(lines)

    # PURPOSE: CCL 式に仕様を注入
    def inject(self, ccl_expr: str) -> str:
        """CCL 式に仕様を注入"""
        operators = self.parse_operators(ccl_expr)

        spec_block = self.generate_spec_block(operators)
        quiz = self.generate_quiz(operators)
        required_sections = self.generate_required_sections(operators)

        return f"""# CCL 実行準備

> **CCL 式**: `{ccl_expr}`

---

{spec_block}
{quiz}
{required_sections}
---

## 実行開始
# PURPOSE: 過去の失敗パターンから警告を生成（Phase 4 連携用スタブ）

CCL: `{ccl_expr}`

以下に実行結果を出力してください。
"""


# PURPOSE: 過去の失敗パターンから警告を生成（Phase 4 連携用スタブ）
def get_warnings_for_expr(ccl_expr: str) -> List[str]:
    """過去の失敗パターンから警告を生成（Phase 4 連携用スタブ）"""
    warnings = []

    # ハードコードされた既知の失敗パターン
    if "!" in ccl_expr:
        warnings.append(
            "⚠️ 演算子 `!` は「階乗 = 全派生同時実行」です。「否定」ではありません。"
        )

    if "*^" in ccl_expr:
        warnings.append(
            "⚠️ `*^` は「融合 + メタ分析」です。両方のセクションが必要です。"
        )

    return warnings


# テスト用
if __name__ == "__main__":
    injector = SpecInjector()

    test_expr = "@repeat(/noe!~/u+_/s!*^/mek+, x2)"
    result = injector.inject(test_expr)
    print(result)

    warnings = get_warnings_for_expr(test_expr)
    for w in warnings:
        print(w)
