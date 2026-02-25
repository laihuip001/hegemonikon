# PROOF: [L2/Mekhane] <- mekhane/ccl/ A0->Auto->AddedByCI
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
from typing import List, Dict, Optional, Set
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

# PURPOSE: operator_loader から SSOT (operators.md) を動的ロード
from mekhane.ccl.operator_loader import load_operators, to_definitions_dict, get_operators_hash

# CCL 式の文字パースで検出するコア演算子シンボル
# (operators.md は全演算子を定義するが、parse_operators は式中の文字マッチのみ)
_CORE_SINGLE_SYMBOLS = {"+", "-", "^", "/", "?", "\\", "*", "~", "_", "!", "'"}
_CORE_COMPOUND_SYMBOLS = {"*^", "~*", ">>"}

# operators.md からロードし、互換辞書を構築
_all_loaded = load_operators()
_compound_loaded, _single_loaded, _ = to_definitions_dict(_all_loaded)
_LOADED_HASH = get_operators_hash()  # G5: ロード時のハッシュを記録

# コアセットでフィルタ (parse_operators 用)
COMPOUND_OPERATORS: Dict[str, Dict[str, str]] = {
    k: v for k, v in _compound_loaded.items() if k in _CORE_COMPOUND_SYMBOLS
}
OPERATOR_DEFINITIONS: Dict[str, Dict[str, str]] = {
    k: v for k, v in _single_loaded.items() if k in _CORE_SINGLE_SYMBOLS
}

# 全演算子 (lookup 用 — コアセットのみ)
ALL_OPERATORS: Dict[str, Dict[str, str]] = {**COMPOUND_OPERATORS, **OPERATOR_DEFINITIONS}


# PURPOSE: CCL 仕様強制注入器
class SpecInjector:
    """CCL 仕様強制注入器"""

    # PURPOSE: SpecInjector の構成と依存関係の初期化
    def __init__(self, operators_path: Optional[Path] = None):
        self.operators_path = (
            operators_path
            or Path(__file__).parent.parent.parent / "ccl" / "operators.md"
        )
        self._operators_content: Optional[str] = None

        # G5: operators.md 変更検知 — モジュールロード時のハッシュと比較
        from mekhane.ccl.operator_loader import get_operators_hash
        current_hash = get_operators_hash(self.operators_path)
        if current_hash and current_hash != _LOADED_HASH:
            import warnings as _w
            _w.warn(
                f"operators.md が変更されました (hash: {_LOADED_HASH} → {current_hash})。"
                " モジュールを再ロードしてください。",
                stacklevel=2,
            )

    # PURPOSE: spec_injector の operators content 処理を実行する
    @property
    # PURPOSE: operators.md の内容をキャッシュ付きで読み込み
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

    # PURPOSE: CCL 式から演算子を抽出 (複合演算子対応)
    def parse_operators(self, ccl_expr: str) -> Set[str]:
        """CCL 式から演算子を抽出 (2文字→1文字の貪欲マッチ)"""
        operators = set()
        i = 0
        while i < len(ccl_expr):
            # 2文字の複合演算子を先にチェック
            if i + 1 < len(ccl_expr):
                bigram = ccl_expr[i:i+2]
                if bigram in COMPOUND_OPERATORS:
                    operators.add(bigram)
                    i += 2
                    continue
            # 1文字演算子
            if ccl_expr[i] in OPERATOR_DEFINITIONS:
                operators.add(ccl_expr[i])
            i += 1
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
                lines.append(f"**Q{i}**: 演算子 `{op}` の名称と作用は？ (回答してから実行せよ)")
                lines.append("")

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

    if "\\" in ccl_expr:
        warnings.append(
            "⚠️ 演算子 `\\` は「反転 (Antistrophē)」です。エスケープ文字ではありません。"
        )

    return warnings


# PURPOSE: spec_injector が警告した演算子のセットを返す (dispatch の重複排除用)
def get_warned_operators(ccl_expr: str) -> set:
    """警告対象となった演算子のセットを返す"""
    warned = set()
    if "!" in ccl_expr:
        warned.add("!")
    if "*^" in ccl_expr:
        warned.add("*^")
    if "\\" in ccl_expr:
        warned.add("\\")
    return warned


# テスト用
if __name__ == "__main__":
    injector = SpecInjector()

    test_expr = "@repeat(/noe!~/u+_/s!*^/mek+, x2)"
    result = injector.inject(test_expr)
    print(result)

    warnings = get_warnings_for_expr(test_expr)
    for w in warnings:
        print(w)
