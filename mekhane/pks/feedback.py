#!/usr/bin/env python3
# PROOF: [L2/インフラ] <- mekhane/pks/ A0→プッシュ反応の学習が次回精度を上げる→feedback が担う
"""
PKS Feedback Loop — プッシュ知識への反応を収集・学習

Usage:
    collector = FeedbackCollector()
    collector.record(PushFeedback(
        nugget_title="Active Inference and FEP",
        reaction="used",
        series="K",
    ))
    # 次回プッシュ時に K-series の閾値を動的調整
    threshold = collector.adjust_threshold("K")
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


# PURPOSE: プッシュ知識への反応記録
@dataclass
class PushFeedback:
    """プッシュ知識への反応記録"""
    nugget_title: str
    reaction: str  # "used" | "dismissed" | "deepened" | "ignored"
    series: str    # Attractor series at push time
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


# 反応ごとのスコア重み
REACTION_WEIGHTS: dict[str, float] = {
    "used": 1.0,       # 活用された → 大幅ブースト
    "deepened": 1.5,   # さらに深掘りされた → 最大ブースト
    "engaged": 0.3,    # 関連知識を探索した → 軽いブースト
    "dismissed": -0.5, # 明示的に却下 → ペナルティ
    "ignored": -0.1,   # 無視 → 軽いペナルティ
}


# PURPOSE: プッシュ反応を収集し、次回の push 優先度を調整
class FeedbackCollector:
    """プッシュ反応を収集し、次回の push 優先度を調整

    シリーズごとに反応スコアを蓄積し、
    proactive_push の閾値を動的に調整する。
    """

    DEFAULT_PATH = Path.home() / "oikos/mneme/.hegemonikon/pks/feedback.json"

    def __init__(self, persist_path: Optional[Path] = None):
        self._path = persist_path or self.DEFAULT_PATH
        self._history: list[dict] = []
        # series → cumulative score
        self._series_scores: dict[str, float] = defaultdict(float)
        # series → count
        self._series_counts: dict[str, int] = defaultdict(int)
        self._load()

    # PURPOSE: 反応を記録
    def record(self, feedback: PushFeedback) -> None:
        """反応を記録"""
        self._history.append(asdict(feedback))
        weight = REACTION_WEIGHTS.get(feedback.reaction, 0.0)
        self._series_scores[feedback.series] += weight
        self._series_counts[feedback.series] += 1

    # PURPOSE: シリーズごとの閾値調整
    def adjust_threshold(self, series: str, base_threshold: float = 0.65) -> float:
        """シリーズごとの閾値調整

        positive feedback が多い series → 閾値を下げる (より多くプッシュ)
        negative feedback が多い series → 閾値を上げる (厳選)

        Returns:
            調整後の閾値 (0.3 〜 0.9 にクランプ)
        """
        count = self._series_counts.get(series, 0)
        if count == 0:
            return base_threshold

        avg_score = self._series_scores[series] / count
        # avg_score: -0.5 〜 1.5 の範囲
        # → 閾値調整: -0.1 〜 +0.15 の範囲
        adjustment = -avg_score * 0.1  # positive → lower threshold
        adjusted = base_threshold + adjustment
        return max(0.3, min(0.9, adjusted))

    # PURPOSE: シリーズごとの統計
    def get_stats(self) -> dict[str, dict]:
        """シリーズごとの統計"""
        stats = {}
        for series in set(list(self._series_scores.keys()) + list(self._series_counts.keys())):
            count = self._series_counts[series]
            score = self._series_scores[series]
            stats[series] = {
                "count": count,
                "total_score": score,
                "avg_score": score / count if count > 0 else 0,
                "threshold_adjustment": self.adjust_threshold(series) - 0.65,
            }
        return stats

    # PURPOSE: ディスクに保存
    def persist(self) -> Path:
        """ディスクに保存"""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "history": self._history[-200:],  # 直近200件のみ保持
            "series_scores": dict(self._series_scores),
            "series_counts": dict(self._series_counts),
        }
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return self._path

    def _load(self) -> None:
        """ディスクから復元"""
        if not self._path.exists():
            return
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._history = data.get("history", [])
            self._series_scores = defaultdict(float, data.get("series_scores", {}))
            self._series_counts = defaultdict(int, data.get("series_counts", {}))
        except (json.JSONDecodeError, KeyError):
            pass  # corrupted file, start fresh
