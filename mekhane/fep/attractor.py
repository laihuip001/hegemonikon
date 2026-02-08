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

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# PURPOSE: 各 Series の本質を捉える定義テキスト（embedding の prototype）
# NOTE: bilingual (英語+日本語) で prototype を定義し、bge-small-en-v1.5 でも
#       日本語入力との類似度が向上するようにする。
#       keywords も embedding テキストに連結して使用する。
SERIES_DEFINITIONS: dict[str, dict] = {
    "O": {
        "name": "Ousia (本質)",
        "definition": (
            "Essence, existence, ontology, purpose, will, intention. "
            "Why does this exist? What is the fundamental nature? "
            "Root cause analysis. Existential meaning. First principles thinking. "
            "Ontology, teleology, raison d'etre. Philosophical inquiry. "
            "Paradigm shift, worldview, assumption, premise, foundation. "
            "Questioning the question itself. Meta-inquiry. "
            "The meaning of existence. What are we not seeing? Blind spots."
        ),
        "definition_ja": (
            "本質、存在、深い認識。なぜこれは存在するのか。"
            "根本的な性質と目的は何か。直観、意志、再帰的自己証明。"
            "根本原因分析。存在の意味。第一原理思考。"
            "価値観、哲学、信条、ミッション、ビジョン。"
            "FEP、自由エネルギー原理、存在論、目的論。"
            "本質的な問い。なぜ必要なのか。存在理由。意味。"
        ),
        "keywords": ["なぜ", "本質", "目的", "意志", "存在", "根本", "問い", "探求"],
        "exemplars": [
            "なぜこれが存在するのか、根本から考えたい",
            "前提を疑い、ゼロから再構築する",
            "パラダイムを転換しなければならない",
            "問いの答えではなく、問い自体を問う",
            "私たちが見落としている盲点は何か",
        ],
        "workflows": ["/noe", "/bou", "/zet", "/ene"],
    },
    "S": {
        "name": "Schema (様態)",
        "definition": (
            "Structure, design, architecture, methodology. How to build and construct. "
            "System design, framework, blueprint, engineering approach. "
            "Scale determination, method arrangement, implementation plan. "
            "Software architecture. Design patterns. Technical blueprint. "
            "Code structure, module organization, directory layout. Refactoring. "
            "Step-by-step procedure. How to implement. Construction plan. "
            "Test strategy design. Data model design. CI/CD pipeline design. "
            "Configuration, optimization of systems and pipelines."
        ),
        "definition_ja": (
            "構造、設計、アーキテクチャ、方法論。どう作るか。"
            "システム設計、フレームワーク、BluePrint、エンジニアリング。"
            "スケール決定、手法配置、実装計画。"
            "コード、プログラミング、API、モジュール、リファクタリング。"
        ),
        "keywords": ["設計", "構造", "方法", "手順", "アーキテクチャ", "フレームワーク", "実装", "コード"],
        "exemplars": [
            "アーキテクチャを設計して構造を決める",
            "実装手順をステップバイステップで進める",
            "モジュール構成とディレクトリ配置を整理する",
            "リファクタリングしてコードを改善する",
            "CI/CDパイプラインを構築してデプロイ自動化",
        ],
        "workflows": ["/met", "/mek", "/sta", "/pra"],
    },
    "H": {
        "name": "Hormē (動機)",
        "definition": (
            "Motivation, emotion, conviction, belief. What drives you. "
            "Gut feeling, intuition, confidence level, desire, passion. "
            "Emotional response, sentiment, fear, hope, anxiety, excitement. "
            "Trust, faith, doubt, morale, burnout, frustration, joy. "
            "How do you feel about this? Inner drive and emotional state. "
            "Personal feeling, subjective experience, mood, worry."
        ),
        "definition_ja": (
            "動機、感情、確信、信念。何が駆動するか。"
            "直感、信頼度、欲求。感情的反応、情熱、恐怖、希望。"
            "信頼、信仰、疑い、不安、興奮。"
            "どう感じるか。内なる衝動とモラール。やる気。"
        ),
        "keywords": ["感情", "直感", "確信", "信念", "モチベーション", "不安", "期待", "やる気"],
        "exemplars": [
            "不安で仕方がない、大丈夫だろうか",
            "モチベーションが下がって疲れた",
            "直感的にこの方向は間違っている気がする",
            "ワクワクする、この機能を作りたい",
            "何かが引っかかる、違和感がある",
        ],
        "workflows": ["/pro", "/pis", "/ore", "/dox"],
    },
    "P": {
        "name": "Perigraphē (条件)",
        "definition": (
            "Boundaries, scope, spatial context. Where and within what limits. "
            "Nested Markov blankets defining system boundaries. "
            "Domain definition, perimeter, containment, territory, region. "
            "What is in scope and out of scope. Target audience, coverage. "
            "Deployment region, supported platforms, browser compatibility. "
            "Responsibility boundary, module ownership, access control. "
            "Constraints, limitations, requirements, preconditions. "
            "Geographic, logical, or organizational boundaries."
        ),
        "definition_ja": (
            "境界、スコープ、空間的文脈。どこまでが範囲か。"
            "システム境界を定義するマルコフブランケット。"
            "ドメイン定義、境界線、含有範囲、テリトリー。"
            "対象範囲と対象外。制約条件、前提条件、環境設定。"
        ),
        "keywords": ["境界", "スコープ", "範囲", "制約", "領域", "環境", "コンテキスト", "対象"],
        "exemplars": [
            "スコープと対象範囲を明確に定義する",
            "この機能は対象外にすべきか判断する",
            "どのリージョンにデプロイするか決める",
            "サポート対象のブラウザと環境を整理する",
            "セキュリティの境界と制約条件を設定する",
        ],
        "workflows": ["/kho", "/hod", "/tro", "/tek"],
    },
    "K": {
        "name": "Kairos (文脈)",
        "definition": (
            "Timing, opportunity, wisdom, research. When is the right moment. "
            "Temporal context, deadline, schedule, urgency. "
            "Knowledge acquisition through investigation and study. "
            "Academic research, literature review, scholarly inquiry. "
            "Latest trends, current state of the art, state of technology. "
            "Is now the right time? Chronological assessment. "
            "Release timing, scheduling decisions, milestone planning."
        ),
        "definition_ja": (
            "タイミング、好機、知恵、調査。いつが適切か。"
            "時間的文脈、期限、スケジュール、緊急度。"
            "調査と学習による知識獲得。"
            "学術研究、文献レビュー、優先順位、いつまでに。"
        ),
        "keywords": ["タイミング", "いつ", "期限", "調査", "論文", "知識", "知恵", "優先順位"],
        "exemplars": [
            "今がこの機能を開発する適切なタイミングか",
            "締め切りまでのスケジュールを確認する",
            "関連する論文や先行研究を調査する",
            "この技術の最新動向を調べたい",
            "リリース時期をいつにするか決める",
        ],
        "workflows": ["/euk", "/chr", "/tel", "/sop"],
    },
    "A": {
        "name": "Akribeia (精度)",
        "definition": (
            "Precision, evaluation, quality control, verification. "
            "Critical assessment, comparison, accuracy checking. "
            "Review, inspection, validation, checking correctness. "
            "Code review, bug detection, quality assurance, testing. "
            "Is this correct? Is this good enough? Pass or fail. "
            "Grading, scoring, benchmarking, performance measurement. "
            "Identifying errors, finding flaws, detecting problems."
        ),
        "definition_ja": (
            "精度、判断、意思決定、評価。どれほど正確か。"
            "批判的評価、比較、品質管理。"
            "選択肢間の選択、トレードオフ分析。"
            "判断基準、判定、検証、レビュー、テスト。"
        ),
        "keywords": ["判断", "評価", "選択", "比較", "品質", "基準", "正確", "レビュー"],
        "exemplars": [
            "この実装は正しいか検証してレビューする",
            "テスト結果を確認して品質が基準を満たすか調べる",
            "コードレビューでバグがないか精査する",
            "出力が期待値と一致しているか検証する",
            "性能ベンチマークを実行して精度を測る",
        ],
        "workflows": ["/pat", "/dia", "/gno", "/epi"],
    },
}

# Attractor 引力の閾値
DEFAULT_THRESHOLD = 0.15
# 複数 Series を返す際の、最大との差分閾値
OSCILLATION_MARGIN = 0.05
# Temperature for softmax sharpening (higher = sharper basin boundaries)
# Raw cosine sims are compressed (0.35-0.55 range), temperature amplifies gaps
DEFAULT_TEMPERATURE = 5.0


# ---------------------------------------------------------------------------
# Enums & Data Classes
# ---------------------------------------------------------------------------

# PURPOSE: Attractor 収束パターンの分類 (Spisak 2025 からの理論的導出)
class OscillationType(Enum):
    """Attractor 収束パターンの分類 (Spisak 2025 からの理論的導出)"""
    CLEAR = "clear"         # 明確な単一 attractor 収束
    POSITIVE = "positive"   # 入力の多面性を反映した正の oscillation
    NEGATIVE = "negative"   # basin 未分化による負の oscillation
    WEAK = "weak"           # 全 attractor への引力が弱い


# PURPOSE: Oscillation の理論的意味と推薦行動 (Problem B)
@dataclass
class OscillationDiagnosis:
    """Oscillation パターンの理論的解釈 (Spisak & Friston 2025 準拠)

    FEP 的解釈:
    - CLEAR:    自由エネルギー最小化が完了。単一 attractor basin で安定
    - POSITIVE: 入力が複数 basin の交差領域にある。多面性は情報量が豊か
    - NEGATIVE: 全 basin への距離が近似的に等しい。入力の抽象度が高すぎる
    - WEAK:     生成モデルの外側。既存 Series では捉えられない新規領域
    """
    oscillation: OscillationType
    theory: str              # FEP 理論的解釈
    action: str              # 推薦される行動
    morphisms: list[str]     # 推薦 X-series 射 (POSITIVE 時)
    confidence_modifier: float  # 確信度への補正 (-1.0 ~ +1.0)

    # PURPOSE: デバッグ時にoscillation状態を即座に確認するための表示
    def __repr__(self) -> str:
        return f"⟨OscDiag: {self.oscillation.value} | {self.action[:40]}⟩"


# PURPOSE: OscillationType → 理論的解釈のマッピング
def _build_diagnosis(
    oscillation: OscillationType,
    attractors: list,  # list[AttractorResult]
    gap: float,
    top_sim: float,
) -> OscillationDiagnosis:
    """OscillationType と文脈から OscillationDiagnosis を生成する。"""
    if oscillation == OscillationType.CLEAR:
        return OscillationDiagnosis(
            oscillation=oscillation,
            theory=(
                "自由エネルギー最小化完了。入力は単一 basin に安定的に収束。"
                f"gap={gap:.3f} は十分な分離を示す。"
            ),
            action="推薦 WF を直接実行。追加確認不要。",
            morphisms=[],
            confidence_modifier=0.1,
        )
    elif oscillation == OscillationType.POSITIVE:
        # 複数 Series が関与 → X-series morphism を提案
        series_pairs = []
        if len(attractors) >= 2:
            for i, a in enumerate(attractors):
                for b in attractors[i + 1:]:
                    pair = tuple(sorted([a.series, b.series]))
                    series_pairs.append(f"X-{pair[0]}{pair[1]}")
        return OscillationDiagnosis(
            oscillation=oscillation,
            theory=(
                "入力は複数 basin の交差領域に位置。"
                "Spisak (2025): 健全な oscillation は情報統合の証拠。"
                f"関与 Series: {'+'.join(a.series for a in attractors)}"
            ),
            action=(
                "複数 WF を順次実行、または Peras (極限) で統合。"
                "X-series 射を通じた Series 間接続を推薦。"
            ),
            morphisms=series_pairs,
            confidence_modifier=0.0,  # 多面性は信頼性を下げない
        )
    elif oscillation == OscillationType.NEGATIVE:
        return OscillationDiagnosis(
            oscillation=oscillation,
            theory=(
                "全 basin への距離が近似的に等しい (basin 未分化)。"
                "FEP 的にはサプライズが高く、生成モデルの予測精度が低い状態。"
                f"top_sim={top_sim:.3f} は閾値付近。"
            ),
            action=(
                "入力をより具体的に再構成。"
                "/zet (探求) で問いを分解するか、/met (尺度) でスコープを絞る。"
            ),
            morphisms=[],
            confidence_modifier=-0.2,
        )
    else:  # WEAK
        return OscillationDiagnosis(
            oscillation=oscillation,
            theory=(
                "全 attractor への引力が閾値未満。"
                "入力は既存 6 Series の生成モデルでは捉えられない。"
                "新規カテゴリの可能性、またはノイズ。"
            ),
            action=(
                "入力の意図を明確化。"
                "6 Series のいずれにも該当しない場合は /noe (深い認識) で再評価。"
            ),
            morphisms=[],
            confidence_modifier=-0.5,
        )


@dataclass
# PURPOSE: Attractor への収束結果
class AttractorResult:
    """Attractor への収束結果"""
    series: str
    name: str
    similarity: float
    workflows: list[str] = field(default_factory=list)

    # PURPOSE: Series名と類似度をデバッグ出力で即確認
    def __repr__(self) -> str:
        return f"⟨{self.series}: {self.name} | sim={self.similarity:.3f}⟩"


# PURPOSE: suggest() の完全な結果（oscillation 診断付き）
@dataclass
class SuggestResult:
    """suggest() の完全な結果（oscillation 診断付き）"""
    attractors: list[AttractorResult]
    oscillation: OscillationType
    top_similarity: float
    gap: float  # 1位と2位の差

    @property
    # PURPOSE: 最も引力の強い単一Seriesを返す（WF自動選択用）
    def primary(self) -> AttractorResult | None:
        return self.attractors[0] if self.attractors else None

    @property
    # PURPOSE: 検証: is_clear
    def is_clear(self) -> bool:
        return self.oscillation == OscillationType.CLEAR

    @property
    # PURPOSE: Problem B: oscillation の理論的解釈を返す
    def interpretation(self) -> OscillationDiagnosis:
        """Oscillation の理論的意味と推薦行動を返す (Problem B)"""
        return _build_diagnosis(
            self.oscillation, self.attractors, self.gap, self.top_similarity
        )

    # PURPOSE: 収束結果サマリの表示（Series+oscillation+top_sim）
    def __repr__(self) -> str:
        names = "+".join(r.series for r in self.attractors)
        return f"⟨{names} | {self.oscillation.value} | top={self.top_similarity:.3f}⟩"


# PURPOSE: 分解された各セグメントの結果
@dataclass
class SegmentResult:
    """分解された各セグメントの結果"""
    text: str
    diagnosis: SuggestResult

    # PURPOSE: 分解セグメントの表示（text先頭+収束先Series）
    def __repr__(self) -> str:
# PURPOSE: decompose() の結果: 各セグメント + マージされた結果
        series = "+".join(r.series for r in self.diagnosis.attractors) or "?"
        return f"⟨'{self.text[:30]}...' → {series}⟩"


# PURPOSE: decompose() の結果: 各セグメント + マージされた結果
@dataclass
class DecomposeResult:
    """decompose() の結果: 各セグメント + マージされた結果"""
    segments: list[SegmentResult]
    merged_series: list[str]
    merged_workflows: list[str]

    @property
    # PURPOSE: 複数の Series に分解されたか
    def is_multi(self) -> bool:
        """複数の Series に分解されたか"""
        return len(self.merged_series) > 1

    # PURPOSE: 分解結果全体の表示（統合Series+セグメント数）
    def __repr__(self) -> str:
# PURPOSE: 6 Series の Attractor Engine
        return f"⟨Decompose: {'+'.join(self.merged_series)} ({len(self.segments)} segments)⟩"


# ---------------------------------------------------------------------------
# SeriesAttractor
# ---------------------------------------------------------------------------

# PURPOSE: 6 Series の Attractor Engine
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

    # PURPOSE: 6 Seriesの attractorプロトタイプを遅延初期化可能に構成
    def __init__(
        self,
        threshold: float = DEFAULT_THRESHOLD,
        oscillation_margin: float = OSCILLATION_MARGIN,
        force_cpu: bool = False,
        temperature: float = DEFAULT_TEMPERATURE,
    ):
        self.threshold = threshold
        self.oscillation_margin = oscillation_margin
        self.temperature = temperature
        self._embedder = None
        self._prototypes: dict[str, np.ndarray] = {}
        # GPU tensor: (6, D) — 全 Series の prototype を 1 つの行列に
        self._proto_tensor = None  # torch.Tensor or None
        self._proto_keys: list[str] = []  # Series keys in tensor order
        self._device = None  # torch.device
        self._force_cpu = force_cpu
        # Problem C: per-series similarity adjustment from basin bias
        self._bias_adjustments: dict[str, float] = {}
        # Multi-prototype: per-series exemplar embeddings
        self._exemplar_embeddings: dict[str, list[np.ndarray]] = {}
        self._exemplar_tensors: dict = {}  # {series: torch.Tensor(N, D)}

    # PURPOSE: Problem C — BasinBias から per-series の similarity 補正を適用
    def apply_bias(self, biases: dict[str, "BasinBias"]) -> None:
        """BasinBias データから per-series の similarity 補正係数を計算・適用する。

        too_wide → similarity を下げる (より厳しく)
        too_narrow → similarity を上げる (より寛容に)

        Args:
            biases: {series_name: BasinBias} dict from BasinLogger._biases
        """
        for series, bias in biases.items():
            if bias.total_count < 5:
                continue  # データ不足はスキップ
            direction = bias.bias_direction
            if direction == "too_wide":
                # Over-predict → この Series の similarity を下げる
                # 最大 -0.05 の補正 (precision が低いほど大きく)
                penalty = min(0.05, (1.0 - bias.precision) * 0.1)
                self._bias_adjustments[series] = -penalty
            elif direction == "too_narrow":
                # Under-predict → この Series の similarity を上げる
                # 最大 +0.05 の補正 (recall が低いほど大きく)
                bonus = min(0.05, (1.0 - bias.recall) * 0.1)
                self._bias_adjustments[series] = bonus
            else:
                self._bias_adjustments[series] = 0.0

    # --- Lazy initialization ---

    # PURPOSE: 遅延初期化: 初回 suggest() 呼び出し時に embedding を GPU tensor 化
    def _ensure_initialized(self) -> None:
        """遅延初期化: 初回 suggest() 呼び出し時に embedding を GPU tensor 化"""
        if self._prototypes:
            return

        # Embedder をインポート (mekhane.anamnesis.index から)
        from mekhane.anamnesis.index import Embedder

        self._embedder = Embedder(force_cpu=self._force_cpu)

        # 各 Series の prototype embedding を計算
        # Bilingual: English + Japanese + keywords を連結して embedding
        series_keys = list(SERIES_DEFINITIONS.keys())
        texts = []
        for k in series_keys:
            defn = SERIES_DEFINITIONS[k]
            parts = [defn["definition"]]
            if "definition_ja" in defn:
                parts.append(defn["definition_ja"])
            if "keywords" in defn:
                parts.append(" ".join(defn["keywords"]))
            texts.append(" ".join(parts))
        embeddings = self._embedder.embed_batch(texts)

        for key, emb in zip(series_keys, embeddings):
            self._prototypes[key] = np.array(emb, dtype=np.float32)

        # GPU tensor 化: (6, D) 行列
        if TORCH_AVAILABLE:
            from mekhane.fep.gpu import get_device, to_tensor
            self._device = get_device(force_cpu=self._force_cpu)
            proto_matrix = np.stack([self._prototypes[k] for k in series_keys])
            self._proto_tensor = to_tensor(proto_matrix, self._device)
            self._proto_keys = series_keys
            print(f"[Attractor] GPU mode ({self._device})", flush=True)
        else:
            print("[Attractor] CPU mode (torch unavailable)", flush=True)

        # Multi-prototype: exemplar embeddings
        for k in series_keys:
            exemplar_texts = SERIES_DEFINITIONS[k].get("exemplars", [])
            if exemplar_texts:
                embs = self._embedder.embed_batch(exemplar_texts)
                self._exemplar_embeddings[k] = [
                    np.array(e, dtype=np.float32) for e in embs
                ]
                if TORCH_AVAILABLE:
                    matrix = np.stack(self._exemplar_embeddings[k])
                    self._exemplar_tensors[k] = to_tensor(matrix, self._device)
            else:
                self._exemplar_embeddings[k] = []

    # --- Core API ---

    # PURPOSE: 入力を Series attractor に射影し、引力の強い順に返す。
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

        # 全 Series の similarity を一括計算
        similarities = self._compute_similarities(user_input)

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

    # PURPOSE: suggest() + oscillation 診断を返す。
    def diagnose(
        self,
        user_input: str,
        top_k: int = 3,
    ) -> SuggestResult:
        """
        suggest() + oscillation 診断を返す。

        OscillationType の判定基準 (temperature-sharpened similarities):
        - CLEAR:    top > 0.5 かつ gap > 0.1  → 明確な単一収束
        - POSITIVE: top > 0.4 かつ gap < 0.05 → 多面的入力
        - NEGATIVE: top < 0.4 かつ 複数拮抗    → basin 未分化
        - WEAK:     top < threshold             → 引力不足
        """
        self._ensure_initialized()

        similarities = self._compute_similarities(user_input)

        # Problem C: bias 補正を適用
        if self._bias_adjustments:
            similarities = [
                (key, sim + self._bias_adjustments.get(key, 0.0))
                for key, sim in similarities
            ]

        similarities.sort(key=lambda x: x[1], reverse=True)

        top_sim = similarities[0][1] if similarities else 0.0
        second_sim = similarities[1][1] if len(similarities) > 1 else 0.0
        gap = top_sim - second_sim

        # Oscillation 判定 (thresholds adjusted for temperature-sharpened sims)
        if top_sim < self.threshold:
            oscillation = OscillationType.WEAK
        elif top_sim >= 0.5 and gap >= 0.1:
            oscillation = OscillationType.CLEAR
        elif top_sim >= 0.4 and gap < 0.05:
            oscillation = OscillationType.POSITIVE
        elif top_sim < 0.4:
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

    # PURPOSE: 全 6 Series の引力を返す（デバッグ/可視化用）
    def suggest_all(
        self,
        user_input: str,
    ) -> list[AttractorResult]:
        """全 6 Series の引力を返す（デバッグ/可視化用）"""
        self._ensure_initialized()

        similarities = self._compute_similarities(user_input)

        results: list[AttractorResult] = []
        for key, sim in similarities:
            defn = SERIES_DEFINITIONS[key]
            results.append(AttractorResult(
                series=key,
                name=defn["name"],
                similarity=sim,
                workflows=defn["workflows"],
            ))

        results.sort(key=lambda x: x.similarity, reverse=True)
        return results

    # PURPOSE: 入力を文に分解し、各文ごとに attractor を診断する。
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
    # PURPOSE: 簡易文分割: 句読点・ピリオド・改行で分割
    def _split_sentences(text: str) -> list[str]:
        """簡易文分割: 句読点・ピリオド・改行で分割"""
        import re
        # 日本語: 。！？  英語: . ! ?  共通: 改行
        parts = re.split(r'[。！？.!?\n]+', text)
        return [p.strip() for p in parts if p.strip()]

    @staticmethod
    # PURPOSE: ワークフローを重複排除してマージ
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

    # PURPOSE: 全 Series の similarity を一括計算 (GPU バッチ or CPU fallback)
    def _compute_similarities(self, user_input: str) -> list[tuple[str, float]]:
        """全 Series の similarity を一括計算.

        GPU 利用可能時: batch_cosine_similarity で 1 回の行列演算
        CPU fallback: numpy の cosine similarity

        Temperature sharpening:
            raw cosine similarities (0.35-0.55 range) are compressed.
            Softmax(sim * temperature) amplifies differences, making
            basin boundaries sharper and reducing O1-concentration.
        """
        input_emb = np.array(
            self._embedder.embed(user_input), dtype=np.float32
        )

        if self._proto_tensor is not None:
            # GPU バッチ: (1, D) @ (D, 6) → (6,)
            from mekhane.fep.gpu import to_tensor, batch_cosine_similarity
            query_tensor = to_tensor(input_emb, self._device)
            sims = batch_cosine_similarity(query_tensor, self._proto_tensor)
            raw_sims = sims.cpu().numpy()
            pairs = [(key, float(raw_sims[i])) for i, key in enumerate(self._proto_keys)]

            # Multi-prototype: blend definition sim with exemplar max
            # α = 0.7 (definition dominates, exemplars are supplementary)
            _EXEMPLAR_WEIGHT = 0.3
            boosted = []
            for key, def_sim in pairs:
                best_sim = def_sim
                if key in self._exemplar_tensors:
                    ex_sims = batch_cosine_similarity(
                        query_tensor, self._exemplar_tensors[key]
                    )
                    ex_max = float(ex_sims.max().cpu())
                    if ex_max > def_sim:
                        # Blend: exemplar boosts but doesn't dominate
                        best_sim = (1 - _EXEMPLAR_WEIGHT) * def_sim + _EXEMPLAR_WEIGHT * ex_max
                boosted.append((key, best_sim))
            pairs = boosted
        else:
            # CPU fallback
            pairs = []
            _EXEMPLAR_WEIGHT = 0.3
            for key, proto in self._prototypes.items():
                def_sim = float(self._cosine_similarity_np(input_emb, proto))
                # Multi-prototype: check exemplars
                best_sim = def_sim
                ex_max = def_sim
                for ex_emb in self._exemplar_embeddings.get(key, []):
                    ex_sim = float(self._cosine_similarity_np(input_emb, ex_emb))
                    ex_max = max(ex_max, ex_sim)
                if ex_max > def_sim:
                    best_sim = (1 - _EXEMPLAR_WEIGHT) * def_sim + _EXEMPLAR_WEIGHT * ex_max
                pairs.append((key, best_sim))

        # Temperature sharpening: amplify separation between basins
        if self.temperature > 1.0:
            pairs = self._apply_temperature(pairs)

        return pairs

    def _apply_temperature(self, pairs: list[tuple[str, float]]) -> list[tuple[str, float]]:
        """Apply softmax temperature scaling to sharpen basin boundaries.

        Softmax(sim_i * T) redistributes similarities so that the
        top-scoring series gets amplified while close competitors
        are suppressed. The output is rescaled to preserve
        the original similarity range for threshold compatibility.
        """
        keys = [k for k, _ in pairs]
        sims = np.array([s for _, s in pairs], dtype=np.float64)

        # Softmax with temperature
        scaled = sims * self.temperature
        scaled -= scaled.max()  # numerical stability
        exp_scaled = np.exp(scaled)
        softmax = exp_scaled / exp_scaled.sum()

        # Rescale to [min_raw, max_raw] range to preserve threshold semantics
        min_raw, max_raw = float(sims.min()), float(sims.max())
        if max_raw > min_raw:
            sharpened = min_raw + (max_raw - min_raw) * (softmax / softmax.max())
        else:
            sharpened = sims  # all equal, no sharpening needed

        return list(zip(keys, [float(s) for s in sharpened]))

    # PURPOSE: Inter-prototype 類似度を測定し、basin分離度を診断
    def calibrate_prototypes(self) -> dict[str, float]:
        """Measure inter-prototype cosine similarities (basin separation).

        Returns dict of "X-Y": similarity for all series pairs.
        High values (> 0.8) indicate insufficient separation.
        """
        self._ensure_initialized()
        pairs: dict[str, float] = {}
        keys = list(self._prototypes.keys())
        for i, k1 in enumerate(keys):
            for k2 in keys[i + 1:]:
                sim = self._cosine_similarity_np(
                    self._prototypes[k1], self._prototypes[k2]
                )
                pairs[f"{k1}-{k2}"] = float(sim)
        return pairs

    @staticmethod
    # PURPOSE: Cosine similarity (numpy fallback)
    def _cosine_similarity_np(a: np.ndarray, b: np.ndarray) -> float:
        """Cosine similarity between two vectors (numpy fallback)"""
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

# PURPOSE: CLI: python -m mekhane.fep.attractor "入力テキスト"
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
