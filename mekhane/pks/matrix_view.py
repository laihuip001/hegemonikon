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
import json
import re
from typing import Optional

from mekhane.pks.llm_client import PKSLLMClient

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

    Phase 1: メタデータベース（タイトル, ソース, スコア, 要約）
    Phase 2: LLM による横断軸抽出（methodology, findings, limitations）
    """

    DEFAULT_COLUMNS = [
        MatrixColumn(name="Title"),
        MatrixColumn(name="Source"),
        MatrixColumn(name="Score"),
        MatrixColumn(name="Key Insight"),
    ]

    _AXIS_PROMPT = (
        "以下の{count}件の知識を比較するための横断軸を抽出してください。\n\n"
        "{summaries}\n\n"
        "JSON形式で軸群を出力:"
        ' [{{"name": "軸名", "description": "説明"}}]\n'
        "軸は3-5個。日本語で。横断比較に有用なもののみ。"
    )

    _FILL_PROMPT = (
        "以下の知識について、指定された軸で評価してください。\n\n"
        "タイトル: {title}\n"
        "要約: {abstract}\n\n"
        "軸: {axes}\n\n"
        "JSON形式で各軸の値を出力 (各値は20文字以内):\n"
        ' {{"axis_name": "value", ...}}'
    )

    # PURPOSE: PKSMatrixView の初期化
    def __init__(
        self,
        columns: list[MatrixColumn] | None = None,
        use_llm: bool = False,
        model: str = "gemini-2.0-flash",
    ):
        self.columns = columns or self.DEFAULT_COLUMNS
        self._llm = PKSLLMClient(model=model, enabled=use_llm)

    # PURPOSE: llm_available の処理
    @property
    def llm_available(self) -> bool:
        return self._llm.available

    # PURPOSE: 比較表を Markdown テーブルとして生成
    def generate(self, nuggets: list[KnowledgeNugget]) -> str:
        """比較表を Markdown テーブルとして生成"""
        if not nuggets:
            return "📭 比較対象なし"

        rows = [self._nugget_to_row(n) for n in nuggets]
        return self._render_markdown(rows)

    # PURPOSE: Phase 2: LLM で動的比較軸を抽出して表を生成
    def generate_with_llm(
        self, nuggets: list[KnowledgeNugget]
    ) -> str:
        """LLM で比較軸を抽出し、動的比較表を生成

        LLM 不可時は Phase 1 フォールバック
        """
        if not nuggets:
            return "📭 比較対象なし"

        if not self.llm_available:
            return self.generate(nuggets)

        # Step 1: 軸抽出
        axes = self._extract_axes(nuggets)
        if not axes:
            return self.generate(nuggets)  # フォールバック

        # Step 2: 各 nugget を軸で評価
        llm_columns = [
            MatrixColumn(name="Title"),
            *[MatrixColumn(name=a["name"], extractor=a.get("description", "")) for a in axes],
            MatrixColumn(name="Score"),
        ]

        rows = []
        for nugget in nuggets:
            cells = self._fill_cells(nugget, axes)
            cells["Title"] = nugget.title[:50]
            cells["Score"] = f"{nugget.relevance_score:.2f}"
            rows.append(MatrixRow(nugget=nugget, cells=cells))

        # レンダリング
        old_columns = self.columns
        self.columns = llm_columns
        result = self._render_markdown(rows)
        self.columns = old_columns
        return result

    # PURPOSE: LLM で比較軸を抽出
    def _extract_axes(self, nuggets: list[KnowledgeNugget]) -> list[dict]:
        """複数 nugget から比較軸を抽出"""
        summaries = "\n".join(
            f"- {n.title}: {(n.abstract[:150] if n.abstract else '(none)')}"
            for n in nuggets[:8]  # 最大8件
        )
        prompt = self._AXIS_PROMPT.format(
            count=min(len(nuggets), 8), summaries=summaries
        )

        try:
            text = self._llm.generate(prompt)
            if text:
                match = re.search(r'\[.*\]', text, re.DOTALL)
                if match:
                    return json.loads(match.group())
        except Exception as e:
            print(f"[MatrixView] Axis extraction error: {e}")

        return []

    # PURPOSE: 各 nugget の軸値を LLM で埋める
    def _fill_cells(self, nugget: KnowledgeNugget, axes: list[dict]) -> dict[str, str]:
        """指定軸で nugget を評価"""
        axis_list = ", ".join(a["name"] for a in axes)
        prompt = self._FILL_PROMPT.format(
            title=nugget.title,
            abstract=nugget.abstract[:300] if nugget.abstract else "(none)",
            axes=axis_list,
        )

        try:
            text = self._llm.generate(prompt)
            if text:
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    return json.loads(match.group())
        except Exception as e:
            print(f"[MatrixView] Fill error: {e}")

        # フォールバック: 空セル
        return {a["name"]: "-" for a in axes}

    # PURPOSE: KnowledgeNugget をテーブル行に変換
    def _nugget_to_row(self, nugget: KnowledgeNugget) -> MatrixRow:
        """メタデータベースの行変換 (Phase 1)"""
        cells = {
            "Title": nugget.title[:50],
            "Source": nugget.source,
            "Score": f"{nugget.relevance_score:.2f}",
            "Key Insight": (nugget.abstract[:80] + "...") if nugget.abstract else "-",
        }
        return MatrixRow(nugget=nugget, cells=cells)

    # PURPOSE: Markdown テーブルをレンダリング
    def _render_markdown(self, rows: list[MatrixRow]) -> str:
        """テーブルを文字列でレンダリング"""
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

