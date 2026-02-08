# noqa: AI-ALL
# PROOF: [L2/インフラ] <- mekhane/pks/links/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 (FEP) → 引用関係の把握が知識の信頼性評価に必要
→ Scite 風の引用分類 (supports/contrasts/mentions)
→ citation_graph.py が担う

# PURPOSE: 論文間の引用関係を分類・管理する
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# PURPOSE: 引用の種類 — Scite 準拠
class CitationType(Enum):
    """引用の種類 — Scite 準拠"""

    SUPPORTS = "supports"  # 支持的引用
    CONTRASTS = "contrasts"  # 反論的引用
    MENTIONS = "mentions"  # 単なる言及


@dataclass
# PURPOSE: 引用リレーション
class Citation:
    """引用リレーション"""

    source_key: str  # 引用元の primary_key
    target_key: str  # 引用先の primary_key
    citation_type: CitationType = CitationType.MENTIONS
    context: str = ""  # 引用文脈のスニペット
    confidence: float = 0.5  # 分類の確信度


@dataclass
# PURPOSE: 論文の引用統計
class CitationStats:
    """論文の引用統計"""

    primary_key: str
    title: str = ""
    supporting_count: int = 0
    contrasting_count: int = 0
    mentioning_count: int = 0

    @property
    # PURPOSE: 関数: total
    def total(self) -> int:
        return self.supporting_count + self.contrasting_count + self.mentioning_count

    @property
    # PURPOSE: 支持率
    def support_ratio(self) -> float:
        """支持率"""
        if self.total == 0:
            return 0.0
        return self.supporting_count / self.total
# PURPOSE: 論文間の引用関係を管理


class CitationGraph:
    """論文間の引用関係を管理

    Phase 1: LanceDB メタデータから引用関係を抽出（基本的な mentions 分類）
    Phase 2: LLM による引用分類 (supports/contrasts 判定)

    Obsidian Graph View 互換のリンク生成も可能。
    """

    # PURPOSE: 内部処理: init__
    def __init__(self):
        self._citations: list[Citation] = []
        self._stats: dict[str, CitationStats] = defaultdict(
            lambda: CitationStats(primary_key="")
        )

    # PURPOSE: 引用を追加
    def add_citation(self, citation: Citation) -> None:
        """引用を追加"""
        self._citations.append(citation)
        self._update_stats(citation)

    # PURPOSE: LanceDB の論文メタデータから引用関係を抽出
    def add_citations_from_papers(self, papers: list[dict]) -> int:
        """LanceDB の論文メタデータから引用関係を抽出

        Phase 1: DOI/arXiv ID ベースの参照検出（mentions のみ）
        """
        added = 0

        # primary_key のセットを構築
        paper_keys = {p.get("primary_key", ""): p for p in papers if p.get("primary_key")}

        for paper in papers:
            source_key = paper.get("primary_key", "")
            if not source_key:
                continue

            # abstract 内での他論文への言及を検出
            abstract = paper.get("abstract", "").lower()
            for target_key, target_paper in paper_keys.items():
                if target_key == source_key:
                    continue

                # DOI or タイトルの一部が abstract に含まれるか
                target_title = target_paper.get("title", "").lower()
                if target_title and len(target_title) > 20:
                    # タイトルの最初の 30 文字でマッチ
                    title_fragment = target_title[:30]
                    if title_fragment in abstract:
                        citation = Citation(
                            source_key=source_key,
                            target_key=target_key,
                            citation_type=CitationType.MENTIONS,
                            context=f"Abstract mentions '{target_title[:50]}'",
                            confidence=0.6,
                        )
                        self.add_citation(citation)
                        added += 1

        return added

    # PURPOSE: 引用統計を更新
    def _update_stats(self, citation: Citation) -> None:
        """引用統計を更新"""
        stats = self._stats[citation.target_key]
        stats.primary_key = citation.target_key

        if citation.citation_type == CitationType.SUPPORTS:
            stats.supporting_count += 1
        elif citation.citation_type == CitationType.CONTRASTS:
            stats.contrasting_count += 1
        else:
            stats.mentioning_count += 1

    # PURPOSE: 論文の引用統計を取得
    def get_stats(self, primary_key: str) -> Optional[CitationStats]:
        """論文の引用統計を取得"""
        return self._stats.get(primary_key)

    # PURPOSE: 指定論文を引用している論文を取得
    def get_citing(self, primary_key: str) -> list[Citation]:
        """指定論文を引用している論文を取得"""
        return [c for c in self._citations if c.target_key == primary_key]

    # PURPOSE: 指定論文が引用している論文を取得
    def get_cited_by(self, primary_key: str) -> list[Citation]:
        """指定論文が引用している論文を取得"""
        return [c for c in self._citations if c.source_key == primary_key]

    # PURPOSE: 引用グラフを JSON 出力
    def export_json(self) -> str:
        """引用グラフを JSON 出力"""
        data = {
            "citations": [
                {
                    "source": c.source_key,
                    "target": c.target_key,
                    "type": c.citation_type.value,
                    "confidence": c.confidence,
                    "context": c.context,
                }
                for c in self._citations
            ],
            "stats": {
                key: {
                    "supporting": s.supporting_count,
                    "contrasting": s.contrasting_count,
                    "mentioning": s.mentioning_count,
                    "support_ratio": f"{s.support_ratio:.2f}",
                }
                for key, s in self._stats.items()
            },
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    # PURPOSE: 引用グラフのサマリーを Markdown で出力
    def summary_markdown(self) -> str:
        """引用グラフのサマリーを Markdown で出力"""
        lines = [
            "## 📚 Citation Graph Summary",
            "",
            f"| 項目 | 値 |",
            f"|:-----|:---|",
            f"| 総引用数 | {len(self._citations)} |",
            f"| 論文数 | {len(self._stats)} |",
        ]

        # 支持率の高い論文 Top 5
        sorted_stats = sorted(
            self._stats.values(),
            key=lambda s: s.total,
            reverse=True,
        )[:5]

        if sorted_stats:
            lines.append("")
            lines.append("### Most Cited (Top 5)")
            lines.append("| Key | Supports | Contrasts | Mentions |")
            lines.append("|:----|:---------|:----------|:---------|")
            for s in sorted_stats:
                lines.append(
                    f"| `{s.primary_key[:30]}` | {s.supporting_count} | "
                    f"{s.contrasting_count} | {s.mentioning_count} |"
                )

        return "\n".join(lines)
