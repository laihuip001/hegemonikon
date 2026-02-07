# noqa: AI-ALL
# PROOF: [L2/インフラ] <- mekhane/pks/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 (FEP) → 知識の比較には構造化された多軸評価が必要
→ Elicit 風の横断比較表
→ matrix_view.py が担う

# PURPOSE: 複数の知識を構造化された比較表で表面化する
"""

from __future__ import annotations

from dataclasses import dataclass, field

from mekhane.pks.pks_engine import KnowledgeNugget


@dataclass
class MatrixColumn:
    """比較表の列定義"""

    name: str
    extractor: str = ""  # Phase 2: LLM 抽出キー


@dataclass
class MatrixRow:
    """比較表の行（1 nugget = 1 行）"""

    nugget: KnowledgeNugget
    cells: dict[str, str] = field(default_factory=dict)


class PKSMatrixView:
    """Elicit 風の構造化比較表生成

    複数論文/記事を共通軸で比較し、Markdown テーブルとして出力する。

    Phase 1: メタデータベース（タイトル, ソース, スコア, 要約）
    Phase 2: LLM による軸抽出（methodology, findings, limitations）
    """

    DEFAULT_COLUMNS = [
        MatrixColumn(name="Title"),
        MatrixColumn(name="Source"),
        MatrixColumn(name="Score"),
        MatrixColumn(name="Key Insight"),
    ]

    def __init__(self, columns: list[MatrixColumn] | None = None):
        self.columns = columns or self.DEFAULT_COLUMNS

    def generate(self, nuggets: list[KnowledgeNugget]) -> str:
        """比較表を Markdown テーブルとして生成"""
        if not nuggets:
            return "📭 比較対象なし"

        rows = [self._nugget_to_row(n) for n in nuggets]
        return self._render_markdown(rows)

    def _nugget_to_row(self, nugget: KnowledgeNugget) -> MatrixRow:
        """KnowledgeNugget をテーブル行に変換"""
        cells = {
            "Title": nugget.title[:50],
            "Source": nugget.source,
            "Score": f"{nugget.relevance_score:.2f}",
            "Key Insight": (nugget.abstract[:80] + "...") if nugget.abstract else "-",
        }
        return MatrixRow(nugget=nugget, cells=cells)

    def _render_markdown(self, rows: list[MatrixRow]) -> str:
        """Markdown テーブルをレンダリング"""
        col_names = [c.name for c in self.columns]

        lines = [
            "## 📊 PKS Matrix View",
            "",
            "| " + " | ".join(col_names) + " |",
            "| " + " | ".join(["---"] * len(col_names)) + " |",
        ]

        for row in rows:
            cells = [row.cells.get(c, "-") for c in col_names]
            # パイプ文字をエスケープ
            cells = [c.replace("|", "\\|") for c in cells]
            lines.append("| " + " | ".join(cells) + " |")

        return "\n".join(lines)
