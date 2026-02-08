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
# PURPOSE: 比較表の列定義
class MatrixColumn:
    """比較表の列定義"""

    name: str
    extractor: str = ""  # Phase 2: LLM 抽出キー


@dataclass
# PURPOSE: 比較表の行（1 nugget = 1 行）
class MatrixRow:
    """比較表の行（1 nugget = 1 行）"""

    nugget: KnowledgeNugget
    cells: dict[str, str] = field(default_factory=dict)


# PURPOSE: Elicit 風の構造化比較表生成
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

    # PURPOSE: PKSMatrixView の初期化 — 比較表を Markdown テーブルとして生成
    def __init__(self, columns: list[MatrixColumn] | None = None):
        self.columns = columns or self.DEFAULT_COLUMNS

    # PURPOSE: 比較表を Markdown テーブルとして生成
    def generate(self, nuggets: list[KnowledgeNugget]) -> str:
        """比較表を Markdown テーブルとして生成"""
        if not nuggets:
            return "📭 比較対象なし"

        rows = [self._nugget_to_row(n) for n in nuggets]
        return self._render_markdown(rows)

    # PURPOSE: KnowledgeNugget をテーブル行に変換
    def _nugget_to_row(self, nugget: KnowledgeNugget) -> MatrixRow:
        """KnowledgeNugget をテーブル行に変換"""
        cells = {
            "Title": nugget.title[:50],
            "Source": nugget.source,
            "Score": f"{nugget.relevance_score:.2f}",
            "Key Insight": (nugget.abstract[:80] + "...") if nugget.abstract else "-",
        }
        return MatrixRow(nugget=nugget, cells=cells)

    # PURPOSE: Markdown テーブルをレンダリング
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


# PURPOSE: Obsidian 風の擬似バックリンク生成
class PKSBacklinks:
    """擬似 Backlinks — Obsidian Graph View のテキスト版

    ベクトル類似度に基づき、指定された知識を「参照している」
    他の知識を発見し、テキストベースの関連マップとして出力する。
    """

    # PURPOSE: 擬似バックリンクレポートを生成
    def generate(
        self,
        origin_query: str,
        related_nuggets: list[KnowledgeNugget],
        max_links: int = 10,
    ) -> str:
        """擬似バックリンクレポートを生成

        Args:
            origin_query: 起点となるクエリ/トピック
            related_nuggets: ベクトル検索で見つかった関連ナゲット
            max_links: 最大表示件数

        Returns:
            Markdown 形式のバックリンクレポート
        """
        if not related_nuggets:
            return f"📭 '{origin_query}' に関連するバックリンクはありません。"

        nuggets = related_nuggets[:max_links]

        lines = [
            f"## 🔗 擬似バックリンク: {origin_query}",
            "",
            f"_関連知識: {len(nuggets)} 件_",
            "",
        ]

        # テキストグラフ
        lines.append("```")
        lines.append(f"  [{origin_query}]")
        for nugget in nuggets:
            score_bar = "█" * int(nugget.relevance_score * 10)
            score_pad = "░" * (10 - int(nugget.relevance_score * 10))
            title_short = nugget.title[:40]
            lines.append(
                f"    ├── {score_bar}{score_pad} {nugget.relevance_score:.2f} │ {title_short}"
            )
        lines.append("```")
        lines.append("")

        # 詳細テーブル
        lines.append("| 知識 | 関連度 | ソース | 接続理由 |")
        lines.append("|:-----|:------:|:------:|:---------|")

        for nugget in nuggets:
            title = nugget.title[:50].replace("|", "\\|")
            reason = nugget.push_reason[:60].replace("|", "\\|") if nugget.push_reason else "セマンティック類似"
            lines.append(
                f"| {title} | {nugget.relevance_score:.2f} | {nugget.source} | {reason} |"
            )

        return "\n".join(lines)

