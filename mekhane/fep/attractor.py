# PROOF: [L2/FEP] <- mekhane/fep/
# PURPOSE: 6 Series を動的 Attractor として実現する
"""
Attractor Dispatch Engine

6 Series (O/S/H/P/K/A) をセマンティック空間上の attractor として定義し、
ユーザー入力を最も引力の強い Series に自然に収束させる。

理論的根拠:
- Spisak & Friston 2025: FEP → 自己直交化する attractor network
- Kirchhoff et al. 2018: adaptive active inference の temporal depth

Doxa DX-007: "6 Series は Attractor であるべき"
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# PURPOSE: 各 Series の本質を捉える定義テキスト（embedding の prototype）
# NOTE: embedding model は bge-small-en-v1.5 (英語) のため、定義は英語で記述
SERIES_DEFINITIONS: dict[str, dict] = {
    "O": {
        "name": "Ousia (本質)",
        "definition": (
            "Essence, existence, deep cognition. Why does this exist? "
            "What is the fundamental nature and purpose? "
            "Deep intuition, will, recursive self-evidencing. "
            "Root cause analysis. Existential meaning. First principles thinking. "
            "Ontology, teleology, raison d'être. Why. The meaning of existence."
        ),
        "keywords": ["なぜ", "本質", "目的", "意志", "存在", "根本", "問い", "探求"],
        "workflows": ["/noe", "/bou", "/zet", "/ene"],
    },
    "S": {
        "name": "Schema (様態)",
        "definition": (
            "Structure, design, architecture, methodology. How to build. "
            "System design, framework, blueprint, engineering. "
            "Scale determination, method arrangement, implementation plan. "
            "Software architecture. Design patterns. Technical approach. "
            "How to implement. Step-by-step procedure."
        ),
        "keywords": ["設計", "構造", "方法", "手順", "アーキテクチャ", "フレームワーク"],
        "workflows": ["/met", "/mek", "/sta", "/pra"],
    },
    "H": {
        "name": "Hormē (動機)",
        "definition": (
            "Motivation, emotion, conviction, belief. What drives you. "
            "Gut feeling, intuition, confidence level, desire. "
            "Emotional response, sentiment, passion, fear, hope. "
            "Trust, faith, doubt, anxiety, excitement. "
            "How do you feel about this? Inner drive and morale."
        ),
        "keywords": ["感情", "直感", "確信", "信念", "モチベーション", "不安", "期待"],
        "workflows": ["/pro", "/pis", "/ore", "/dox"],
    },
    "P": {
        "name": "Perigraphē (条件)",
        "definition": (
            "Boundaries, scope, spatial context. Where and within what limits. "
            "Nested Markov blankets defining system boundaries. "
            "Domain definition, perimeter, containment, territory. "
            "What is in scope and out of scope. Geographic or logical boundaries. "
            "Spatial arrangement, region, zone, area of operation."
        ),
        "keywords": ["境界", "スコープ", "範囲", "制約", "領域", "環境", "コンテキスト"],
        "workflows": ["/kho", "/hod", "/tro", "/tek"],
    },
    "K": {
        "name": "Kairos (文脈)",
        "definition": (
            "Timing, opportunity, wisdom, research. When is the right moment. "
            "Temporal context, deadline, schedule, urgency. "
            "Knowledge acquisition through investigation and study. "
            "Academic research, literature review, scholarly inquiry. "
            "Is now the right time? Chronological assessment."
        ),
        "keywords": ["タイミング", "いつ", "期限", "調査", "論文", "知識", "知恵"],
        "workflows": ["/euk", "/chr", "/tel", "/sop"],
    },
    "A": {
        "name": "Akribeia (精度)",
        "definition": (
            "Precision, judgment, decision-making, evaluation. How accurate. "
            "Critical assessment, comparison, quality control. "
            "Choosing between alternatives, trade-off analysis. "
            "Decision criteria, verdict, ruling, appraisal. "
            "Is this correct? Accuracy validation and verification."
        ),
        "keywords": ["判断", "評価", "選択", "比較", "品質", "基準", "正確"],
        "workflows": ["/pat", "/dia", "/gno", "/epi"],
    },
}

# Attractor 引力の閾値
DEFAULT_THRESHOLD = 0.15
# 複数 Series を返す際の、最大との差分閾値
OSCILLATION_MARGIN = 0.05


# ---------------------------------------------------------------------------
# Enums & Data Classes
# ---------------------------------------------------------------------------

class OscillationType(Enum):
    """Attractor 収束パターンの分類 (Spisak 2025 からの理論的導出)"""
    CLEAR = "clear"         # 明確な単一 attractor 収束
    POSITIVE = "positive"   # 入力の多面性を反映した正の oscillation
    NEGATIVE = "negative"   # basin 未分化による負の oscillation
    WEAK = "weak"           # 全 attractor への引力が弱い


@dataclass
class AttractorResult:
    """Attractor への収束結果"""
    series: str
    name: str
    similarity: float
    workflows: list[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return f"⟨{self.series}: {self.name} | sim={self.similarity:.3f}⟩"


@dataclass
class SuggestResult:
    """suggest() の完全な結果（oscillation 診断付き）"""
    attractors: list[AttractorResult]
    oscillation: OscillationType
    top_similarity: float
    gap: float  # 1位と2位の差

    @property
    def primary(self) -> AttractorResult | None:
        return self.attractors[0] if self.attractors else None

    @property
    def is_clear(self) -> bool:
        return self.oscillation == OscillationType.CLEAR

    def __repr__(self) -> str:
        names = "+".join(r.series for r in self.attractors)
        return f"⟨{names} | {self.oscillation.value} | top={self.top_similarity:.3f}⟩"


@dataclass
class SegmentResult:
    """分解された各セグメントの結果"""
    text: str
    diagnosis: SuggestResult

    def __repr__(self) -> str:
        series = "+".join(r.series for r in self.diagnosis.attractors) or "?"
        return f"⟨'{self.text[:30]}...' → {series}⟩"


@dataclass
class DecomposeResult:
    """decompose() の結果: 各セグメント + マージされた結果"""
    segments: list[SegmentResult]
    merged_series: list[str]
    merged_workflows: list[str]

    @property
    def is_multi(self) -> bool:
        """複数の Series に分解されたか"""
        return len(self.merged_series) > 1

    def __repr__(self) -> str:
        return f"⟨Decompose: {'+'.join(self.merged_series)} ({len(self.segments)} segments)⟩"


# ---------------------------------------------------------------------------
# SeriesAttractor
# ---------------------------------------------------------------------------

class SeriesAttractor:
    """
    6 Series の Attractor Engine

    各 Series の定義テキストを embedding 空間に射影し、
    ユーザー入力との cosine similarity で最も引力の強い Series を特定する。

    Usage:
        sa = SeriesAttractor()
        results = sa.suggest("なぜこのプロジェクトが必要なのか")
        # → [⟨O: Ousia (本質) | sim=0.742⟩, ...]
    """

    def __init__(
        self,
        threshold: float = DEFAULT_THRESHOLD,
        oscillation_margin: float = OSCILLATION_MARGIN,
        force_cpu: bool = False,
    ):
        self.threshold = threshold
        self.oscillation_margin = oscillation_margin
        self._embedder = None
        self._prototypes: dict[str, np.ndarray] = {}
        self._force_cpu = force_cpu

    # --- Lazy initialization ---

    def _ensure_initialized(self) -> None:
        """遅延初期化: 初回 suggest() 呼び出し時に embedding を計算"""
        if self._prototypes:
            return

        # Embedder をインポート (mekhane.anamnesis.index から)
        from mekhane.anamnesis.index import Embedder

        self._embedder = Embedder(force_cpu=self._force_cpu)

        # 各 Series の prototype embedding を計算
        series_keys = list(SERIES_DEFINITIONS.keys())
        texts = [SERIES_DEFINITIONS[k]["definition"] for k in series_keys]
        embeddings = self._embedder.embed_batch(texts)

        for key, emb in zip(series_keys, embeddings):
            self._prototypes[key] = np.array(emb, dtype=np.float32)

    # --- Core API ---

    def suggest(
        self,
        user_input: str,
        top_k: int = 3,
    ) -> list[AttractorResult]:
        """
        入力を Series attractor に射影し、引力の強い順に返す。

        Args:
            user_input: ユーザーの入力テキスト
            top_k: 返す最大 Series 数

        Returns:
            AttractorResult のリスト（引力順、閾値以上のもののみ）
            境界入力は複数 Series を返す (oscillatory activity)
        """
        self._ensure_initialized()

        # 入力を embedding
        input_emb = np.array(
            self._embedder.embed(user_input), dtype=np.float32
        )

        # 各 Series prototype との cosine similarity
        similarities: list[tuple[str, float]] = []
        for key, proto in self._prototypes.items():
            sim = self._cosine_similarity(input_emb, proto)
            similarities.append((key, float(sim)))

        # similarity 降順ソート
        similarities.sort(key=lambda x: x[1], reverse=True)

        # 閾値フィルタリング + oscillation margin
        results: list[AttractorResult] = []
        max_sim = similarities[0][1] if similarities else 0.0

        for key, sim in similarities[:top_k]:
            # 閾値以上かつ、最大との差がmargin以内
            if sim >= self.threshold and (max_sim - sim) <= self.oscillation_margin:
                defn = SERIES_DEFINITIONS[key]
                results.append(AttractorResult(
                    series=key,
                    name=defn["name"],
                    similarity=sim,
                    workflows=defn["workflows"],
                ))

        return results

    def diagnose(
        self,
        user_input: str,
        top_k: int = 3,
    ) -> SuggestResult:
        """
        suggest() + oscillation 診断を返す。

        OscillationType の判定基準:
        - CLEAR:    top > 0.6 かつ gap > 0.1  → 明確な単一収束
        - POSITIVE: top > 0.5 かつ gap < 0.05 → 多面的入力
        - NEGATIVE: top < 0.5 かつ 複数拮抗    → basin 未分化
        - WEAK:     top < threshold             → 引力不足
        """
        self._ensure_initialized()

        input_emb = np.array(
            self._embedder.embed(user_input), dtype=np.float32
        )

        similarities: list[tuple[str, float]] = []
        for key, proto in self._prototypes.items():
            sim = self._cosine_similarity(input_emb, proto)
            similarities.append((key, float(sim)))

        similarities.sort(key=lambda x: x[1], reverse=True)

        top_sim = similarities[0][1] if similarities else 0.0
        second_sim = similarities[1][1] if len(similarities) > 1 else 0.0
        gap = top_sim - second_sim

        # Oscillation 判定
        if top_sim < self.threshold:
            oscillation = OscillationType.WEAK
        elif top_sim >= 0.6 and gap >= 0.1:
            oscillation = OscillationType.CLEAR
        elif top_sim >= 0.5 and gap < 0.05:
            oscillation = OscillationType.POSITIVE
        elif top_sim < 0.5:
            oscillation = OscillationType.NEGATIVE
        else:
            # 中間領域: gap で判定
            oscillation = OscillationType.CLEAR if gap >= 0.08 else OscillationType.POSITIVE

        # Attractor 結果
        results: list[AttractorResult] = []
        for key, sim in similarities[:top_k]:
            if sim >= self.threshold and (top_sim - sim) <= self.oscillation_margin:
                defn = SERIES_DEFINITIONS[key]
                results.append(AttractorResult(
                    series=key,
                    name=defn["name"],
                    similarity=sim,
                    workflows=defn["workflows"],
                ))

        return SuggestResult(
            attractors=results,
            oscillation=oscillation,
            top_similarity=top_sim,
            gap=gap,
        )

    def suggest_all(
        self,
        user_input: str,
    ) -> list[AttractorResult]:
        """全 6 Series の引力を返す（デバッグ/可視化用）"""
        self._ensure_initialized()

        input_emb = np.array(
            self._embedder.embed(user_input), dtype=np.float32
        )

        results: list[AttractorResult] = []
        for key, proto in self._prototypes.items():
            sim = float(self._cosine_similarity(input_emb, proto))
            defn = SERIES_DEFINITIONS[key]
            results.append(AttractorResult(
                series=key,
                name=defn["name"],
                similarity=sim,
                workflows=defn["workflows"],
            ))

        results.sort(key=lambda x: x.similarity, reverse=True)
        return results

    def decompose(
        self,
        user_input: str,
    ) -> DecomposeResult:
        """
        入力を文に分解し、各文ごとに attractor を診断する。
        複合的な入力から複数の Series を自然に抽出する。

        例: "Why does this design need to be built now?"
        → "Why does this" → O
        → "design need to be built" → S
        → "now" → K

        Returns:
            DecomposeResult with per-segment diagnoses and merged attractors
        """
        segments = self._split_sentences(user_input)

        if len(segments) <= 1:
            # 単一文 → 通常の diagnose に委譲
            result = self.diagnose(user_input)
            return DecomposeResult(
                segments=[SegmentResult(text=user_input, diagnosis=result)],
                merged_series=list({r.series for r in result.attractors}),
                merged_workflows=self._merge_workflows(result.attractors),
            )

        segment_results: list[SegmentResult] = []
        all_attractors: list[AttractorResult] = []

        for seg in segments:
            seg_text = seg.strip()
            if not seg_text:
                continue
            diag = self.diagnose(seg_text)
            segment_results.append(SegmentResult(text=seg_text, diagnosis=diag))
            all_attractors.extend(diag.attractors)

        # 重複排除して Series を集約（similarity 最大のものを保持）
        best_per_series: dict[str, AttractorResult] = {}
        for ar in all_attractors:
            if ar.series not in best_per_series or ar.similarity > best_per_series[ar.series].similarity:
                best_per_series[ar.series] = ar

        # similarity 順でソート
        merged = sorted(best_per_series.values(), key=lambda x: x.similarity, reverse=True)
        merged_series = [r.series for r in merged]
        merged_workflows = self._merge_workflows(merged)

        return DecomposeResult(
            segments=segment_results,
            merged_series=merged_series,
            merged_workflows=merged_workflows,
        )

    # --- Internal ---

    @staticmethod
    def _split_sentences(text: str) -> list[str]:
        """簡易文分割: 句読点・ピリオド・改行で分割"""
        import re
        # 日本語: 。！？  英語: . ! ?  共通: 改行
        parts = re.split(r'[。！？.!?\n]+', text)
        return [p.strip() for p in parts if p.strip()]

    @staticmethod
    def _merge_workflows(attractors: list[AttractorResult]) -> list[str]:
        """ワークフローを重複排除してマージ"""
        seen: set[str] = set()
        result: list[str] = []
        for ar in attractors:
            for wf in ar.workflows:
                if wf not in seen:
                    seen.add(wf)
                    result.append(wf)
        return result

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Cosine similarity between two vectors"""
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """CLI: python -m mekhane.fep.attractor "入力テキスト" """
    if len(sys.argv) < 2:
        print("Usage: python -m mekhane.fep.attractor <input_text>")
        print('Example: python -m mekhane.fep.attractor "なぜこのプロジェクトが必要か"')
        sys.exit(1)

    user_input = " ".join(sys.argv[1:])
    sa = SeriesAttractor()

    print(f"\n入力: {user_input}")
    print("=" * 60)

    # 全 Series の引力を表示
    all_results = sa.suggest_all(user_input)
    print("\n全 Series 引力マップ:")
    for r in all_results:
        bar = "█" * int(r.similarity * 40)
        print(f"  {r.series} {r.name:20s} {r.similarity:.3f} {bar}")

    # Attractor 収束結果
    results = sa.suggest(user_input)
    print(f"\n収束先 ({len(results)} attractor):")
    for r in results:
        wf = ", ".join(r.workflows)
        print(f"  → {r.series} {r.name} (sim={r.similarity:.3f})")
        print(f"    workflows: {wf}")


if __name__ == "__main__":
    main()
