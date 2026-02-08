#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/pks/ A0→Attractor+PKS接続が必要→attractor_context が担う
"""
Attractor → PKS コンテキスト変換ブリッジ

SeriesAttractor の Series 判定を PKS SessionContext に変換し、
手動 set_context を不要にする。

Usage:
    bridge = AttractorContextBridge()
    ctx = bridge.infer_context("FEPの理論的基盤を調査したい")
    print(ctx.topics)  # → ['調査', '論文', '知識', ...]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from mekhane.pks.pks_engine import SessionContext


# Series → 関連トピックマッピング
SERIES_TOPICS: dict[str, list[str]] = {
    "O": ["認識", "本質", "前提", "FEP", "哲学", "存在", "直観"],
    "S": ["設計", "構造", "パターン", "実装", "アーキテクチャ", "手順"],
    "H": ["感情", "信頼", "不安", "動機", "確信", "欲求"],
    "P": ["スコープ", "範囲", "環境", "リソース", "場所", "領域"],
    "K": ["調査", "論文", "知識", "時機", "タイミング", "研究"],
    "A": ["評価", "判断", "比較", "品質", "批判", "検証"],
}

# Series → 推奨ワークフロー
SERIES_WORKFLOWS: dict[str, list[str]] = {
    "O": ["/noe", "/zet"],
    "S": ["/mek", "/ene"],
    "H": ["/pro", "/pis", "/pat"],
    "P": ["/kho", "/hod"],
    "K": ["/sop", "/epi", "/chr"],
    "A": ["/dia", "/gno", "/sta"],
}


# PURPOSE: Attractor 推論結果をまとめたコンテキスト
@dataclass
class AttractorContext:
    """Attractor 推論結果をまとめたコンテキスト"""
    series: str
    similarity: float
    oscillation: str
    topics: list[str] = field(default_factory=list)
    workflows: list[str] = field(default_factory=list)
    secondary_series: Optional[str] = None
    secondary_topics: list[str] = field(default_factory=list)


# PURPOSE: Attractor → PKS コンテキスト変換
class AttractorContextBridge:
    """Attractor → PKS コンテキスト変換

    ユーザー入力に対して:
    1. SeriesAttractor.diagnose() で Series 判定
    2. Series → トピック/WF マッピング
    3. oscillation=positive 時は 2nd series のトピックも結合
    4. SessionContext を生成
    """

    def __init__(self, force_cpu: bool = False):
        self._attractor = None
        self._force_cpu = force_cpu

    def _get_attractor(self):
        if self._attractor is None:
            from mekhane.fep.attractor import SeriesAttractor
            self._attractor = SeriesAttractor(force_cpu=self._force_cpu)
        return self._attractor

    # PURPOSE: ユーザー入力 → AttractorContext 推論
    def infer_context(self, user_input: str) -> AttractorContext:
        """ユーザー入力 → AttractorContext 推論

        Returns:
            AttractorContext with series, topics, workflows
        """
        attractor = self._get_attractor()
        result = attractor.diagnose(user_input)

        # Primary series
        top = result.attractors[0]
        series = top.series
        similarity = top.similarity
        oscillation = result.oscillation.value

        topics = list(SERIES_TOPICS.get(series, []))
        workflows = list(SERIES_WORKFLOWS.get(series, []))

        # Secondary series (for oscillation)
        secondary_series = None
        secondary_topics: list[str] = []
        if len(result.attractors) > 1 and oscillation in ("positive", "negative"):
            second = result.attractors[1]
            secondary_series = second.series
            secondary_topics = list(SERIES_TOPICS.get(second.series, []))

        return AttractorContext(
            series=series,
            similarity=similarity,
            oscillation=oscillation,
            topics=topics,
            workflows=workflows,
            secondary_series=secondary_series,
            secondary_topics=secondary_topics,
        )

    # PURPOSE: AttractorContext → SessionContext 変換
    def to_session_context(self, attractor_ctx: AttractorContext) -> SessionContext:
        """AttractorContext → SessionContext 変換

        oscillation 時は primary + secondary topics を結合
        """
        topics = list(attractor_ctx.topics)

        # oscillation 時: secondary topics を追加
        if attractor_ctx.secondary_topics:
            for t in attractor_ctx.secondary_topics:
                if t not in topics:
                    topics.append(t)

        return SessionContext(
            topics=topics,
            active_workflows=attractor_ctx.workflows,
        )

    # PURPOSE: ワンショット: user_input → SessionContext
    def infer_session_context(self, user_input: str) -> SessionContext:
        """ワンショット: user_input → SessionContext"""
        attractor_ctx = self.infer_context(user_input)
        return self.to_session_context(attractor_ctx)
