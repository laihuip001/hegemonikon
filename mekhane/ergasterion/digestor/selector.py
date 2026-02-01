# PROOF: [L2/インフラ] <- mekhane/ergasterion/digestor/ A0→消化処理が必要→selector が担う
"""
Digestor Selector - 消化候補選定ロジック

Gnosis から収集した論文を、消化すべき候補として選定する。
トピックベースフィルタリング、優先度スコアリングを行う。
"""

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
import yaml

# Paper モデルのインポート
try:
    from mekhane.anamnesis.models.paper import Paper
except ImportError:
    # フォールバック: 簡易 Paper dataclass
    @dataclass
    class Paper:
        id: str
        title: str
        abstract: str = ""
        source: str = ""
        categories: list[str] = field(default_factory=list)
        published: Optional[str] = None
        url: Optional[str] = None


@dataclass
class DigestCandidate:
    """消化候補"""

    paper: Paper
    score: float  # 優先度スコア (0.0 - 1.0)
    matched_topics: list[str]  # マッチしたトピック
    rationale: str  # 選定理由


class DigestorSelector:
    """消化候補選定ロジック"""

    def __init__(self, topics_file: Optional[Path] = None):
        """
        Args:
            topics_file: トピック定義 YAML ファイルのパス
        """
        self.topics_file = topics_file or self._default_topics_file()
        self.topics = self._load_topics()

    def _default_topics_file(self) -> Path:
        """デフォルトのトピックファイルパス"""
        return Path(__file__).parent / "topics.yaml"

    def _load_topics(self) -> dict:
        """トピック定義を読み込む"""
        if self.topics_file.exists():
            with open(self.topics_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def _calculate_score(self, paper: Paper, matched_topics: list[str]) -> float:
        """
        優先度スコアを計算

        スコア要素:
        - トピックマッチ数
        - 新鮮さ（published date）
        - 将来: citation count, relevance to Hegemonikón
        """
        score = 0.0

        # トピックマッチ (0.0 - 0.6)
        max_topics = len(self.topics.get("topics", []))
        if max_topics > 0:
            score += min(len(matched_topics) / max_topics, 1.0) * 0.6

        # Abstract 長さボーナス (長い = 消化しやすい)
        if paper.abstract and len(paper.abstract) > 500:
            score += 0.2
        elif paper.abstract and len(paper.abstract) > 200:
            score += 0.1

        # ソースボーナス
        if paper.source == "arxiv":
            score += 0.1  # arXiv は最新プレプリント
        elif paper.source == "semantic_scholar":
            score += 0.1  # 被引用情報あり

        return min(score, 1.0)

    def _match_topics(self, paper: Paper) -> list[str]:
        """論文がマッチするトピックを検出"""
        matched = []

        topics_list = self.topics.get("topics", [])
        text_to_match = f"{paper.title} {paper.abstract}".lower()

        for topic in topics_list:
            query = topic.get("query", "").lower()
            topic_id = topic.get("id", "")

            # 簡易マッチング: クエリ内の単語が title/abstract に含まれるか
            query_words = query.split()
            match_count = sum(1 for w in query_words if w in text_to_match)

            # 60% 以上の単語がマッチすればトピックマッチとみなす
            if len(query_words) > 0 and match_count / len(query_words) >= 0.6:
                matched.append(topic_id)

        return matched

    def select_candidates(
        self,
        papers: list[Paper],
        max_candidates: int = 10,
        min_score: float = 0.3,
        topic_filter: Optional[list[str]] = None,
    ) -> list[DigestCandidate]:
        """
        消化候補を選定

        Args:
            papers: Gnosis から収集した論文リスト
            max_candidates: 最大候補数
            min_score: 最小スコア閾値
            topic_filter: 特定トピックのみ選定（None = 全トピック）

        Returns:
            DigestCandidate のリスト（スコア降順）
        """
        candidates = []

        for paper in papers:
            # トピックマッチング
            matched_topics = self._match_topics(paper)

            # トピックフィルタリング
            if topic_filter:
                matched_topics = [t for t in matched_topics if t in topic_filter]

            # マッチなしはスキップ
            if not matched_topics:
                continue

            # スコア計算
            score = self._calculate_score(paper, matched_topics)

            # 閾値チェック
            if score < min_score:
                continue

            # 選定理由生成
            rationale = f"Topics: {', '.join(matched_topics)} | Score: {score:.2f}"

            candidates.append(
                DigestCandidate(
                    paper=paper,
                    score=score,
                    matched_topics=matched_topics,
                    # NOTE: Removed self-assignment: rationale = rationale
                )
            )

        # スコア降順でソート
        candidates.sort(key=lambda c: c.score, reverse=True)

        return candidates[:max_candidates]

    def get_topics(self) -> list[dict]:
        """定義済みトピックを取得"""
        return self.topics.get("topics", [])
