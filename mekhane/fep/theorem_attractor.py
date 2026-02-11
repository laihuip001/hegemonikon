# PROOF: [L1/FEP] <- mekhane/fep/
# PURPOSE: 96 要素体系の Theorem-Level Attractor — 認知シミュレータ
"""
Theorem-Level Attractor Engine

24 定理をセマンティック空間上の attractor として定義し、
72 X-series morphism を遷移行列として GPU 上でシミュレートする。

理論的根拠:
- Spisak & Friston 2025: FEP → 自己直交化する attractor network
- Hegemonikón v3.3: 7公理 + 24定理 + 72関係 = 96要素体系

Usage:
    from mekhane.fep.theorem_attractor import TheoremAttractor
    ta = TheoremAttractor()
    result = ta.diagnose("なぜこの設計が今必要なのか")
    flow = ta.simulate_flow("なぜこの設計が今必要なのか", steps=10)
    basins = ta.detect_basins(n_samples=10000)
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


# ---------------------------------------------------------------------------
# 24 Theorem Definitions
# ---------------------------------------------------------------------------

# PURPOSE: 各定理の本質を捉える定義テキスト (bge embedding 用、英語)
# NOTE: WF の description から抽出 + 本質を英語で記述
THEOREM_DEFINITIONS: dict[str, dict] = {
    # O-series: Ousia (本質)
    "O1": {
        "name": "Noēsis (深い認識)",
        "series": "O",
        "command": "/noe",
        "definition": (
            "Deep cognition, intuitive insight. Recursive self-evidencing. "
            "Premise destruction. Zero-point design. Graph-of-Thought analysis. "
            "The deepest layer of understanding. Why does this truly exist?"
        ),
    },
    "O2": {
        "name": "Boulēsis (意志)",
        "series": "O",
        "command": "/bou",
        "definition": (
            "Will, purpose, goal clarification. What do you truly want? "
            "From pure ideal to practical objective. Desire, volition, akrasia. "
            "Priority setting and trade-off analysis."
        ),
    },
    "O3": {
        "name": "Zētēsis (探求)",
        "series": "O",
        "command": "/zet",
        "definition": (
            "Inquiry, question discovery. What should be asked? "
            "Finding the seed of the question. Five Whys. Root cause exploration. "
            "Spike and proof-of-concept investigation."
        ),
    },
    "O4": {
        "name": "Energeia (行為)",
        "series": "O",
        "command": "/ene",
        "definition": (
            "Action, actualization. Turning will into reality. "
            "6-stage execution framework. Feature flags. Staged deployment. "
            "Making things happen. Implementation and delivery."
        ),
    },
    # S-series: Schema (様態)
    "S1": {
        "name": "Metron (尺度)",
        "series": "S",
        "command": "/met",
        "definition": (
            "Scale, granularity, measurement. How large or small? "
            "Scope determination. Level of abstraction. Resolution setting. "
            "Zoom in or zoom out decision."
        ),
    },
    "S2": {
        "name": "Mekhanē (方法)",
        "series": "S",
        "command": "/mek",
        "definition": (
            "Method, mechanism, skill arrangement. How to build? "
            "Workflow generation and diagnosis. Tool selection. "
            "Architecture design. Blueprint creation."
        ),
    },
    "S3": {
        "name": "Stathmos (基準)",
        "series": "S",
        "command": "/sta",
        "definition": (
            "Standard, benchmark, evaluation criteria. What defines quality? "
            "Acceptance criteria. Performance metrics. Quality gate. "
            "Success criteria definition."
        ),
    },
    "S4": {
        "name": "Praxis (実践)",
        "series": "S",
        "command": "/pra",
        "definition": (
            "Practice, value realization. How to deliver value? "
            "Method selection for implementation. Hands-on execution. "
            "Turning design into working system."
        ),
    },
    # H-series: Hormē (動機)
    "H1": {
        "name": "Propatheia (前感情)",
        "series": "H",
        "command": "/pro",
        "definition": (
            "Pre-emotion, initial impulse, gut feeling. First reaction. "
            "Intuitive tendency. Instinctive response before rational evaluation. "
            "What is your immediate feeling about this?"
        ),
    },
    "H2": {
        "name": "Pistis (確信)",
        "series": "H",
        "command": "/pis",
        "definition": (
            "Conviction, confidence level. How sure are you? "
            "Trust assessment. Reliability evaluation. Epistemic humility. "
            "Certainty vs uncertainty measurement."
        ),
    },
    "H3": {
        "name": "Orexis (欲求)",
        "series": "H",
        "command": "/ore",
        "definition": (
            "Desire, value tendency. What do you value? "
            "Appetite for change. Motivation assessment. "
            "Passion and drive evaluation. Value alignment check."
        ),
    },
    "H4": {
        "name": "Doxa (信念)",
        "series": "H",
        "command": "/dox",
        "definition": (
            "Belief, opinion, conviction record. What do you believe? "
            "Belief persistence and recording. Worldview documentation. "
            "Assumption tracking and updating."
        ),
    },
    # P-series: Perigraphē (条件)
    "P1": {
        "name": "Khōra (場)",
        "series": "P",
        "command": "/kho",
        "definition": (
            "Space, field, domain. Where does this apply? "
            "Scope definition. Boundary setting. Markov blanket delineation. "
            "Context and environment specification."
        ),
    },
    "P2": {
        "name": "Hodos (道)",
        "series": "P",
        "command": "/hod",
        "definition": (
            "Path, route, trajectory. Which way to go? "
            "Route planning. Step sequence. Roadmap creation. "
            "Migration path and transition strategy."
        ),
    },
    "P3": {
        "name": "Trokhia (軌道)",
        "series": "P",
        "command": "/tro",
        "definition": (
            "Orbit, cycle, iteration scope. How does this repeat? "
            "Application range. Feedback loop. Sprint cycle. "
            "Iterative refinement pattern."
        ),
    },
    "P4": {
        "name": "Tekhnē (技法)",
        "series": "P",
        "command": "/tek",
        "definition": (
            "Technique, craft, specific tool choice. Which technique? "
            "Tool selection. Technology choice. Implementation technique. "
            "Craft and artisanship in execution."
        ),
    },
    # K-series: Kairos (文脈)
    "K1": {
        "name": "Eukairia (好機)",
        "series": "K",
        "command": "/euk",
        "definition": (
            "Opportunity, right timing. Is now the right moment? "
            "Window of opportunity detection. Timing assessment. "
            "Readiness evaluation. Strategic timing."
        ),
    },
    "K2": {
        "name": "Chronos (時間)",
        "series": "K",
        "command": "/chr",
        "definition": (
            "Time, deadline, temporal constraint. How much time? "
            "Schedule evaluation. Time pressure assessment. "
            "Duration estimation. Calendar awareness."
        ),
    },
    "K3": {
        "name": "Telos (目的)",
        "series": "K",
        "command": "/tel",
        "definition": (
            "Purpose, end goal, teleological check. Why this goal? "
            "Means-end inversion prevention. Purpose validation. "
            "Are you solving the right problem?"
        ),
    },
    "K4": {
        "name": "Sophia (知恵)",
        "series": "K",
        "command": "/sop",
        "definition": (
            "Wisdom, research, deep investigation. What does the evidence say? "
            "Literature review. Academic inquiry. Expert consultation. "
            "Evidence-based decision making."
        ),
    },
    # A-series: Akribeia (精度)
    "A1": {
        "name": "Pathos (情念)",
        "series": "A",
        "command": "/pat",
        "definition": (
            "Meta-emotion, emotional evaluation. What are you feeling about your feelings? "
            "Dual tendency assessment. Emotional bias detection. "
            "Sentiment meta-analysis."
        ),
    },
    "A2": {
        "name": "Krisis (判定)",
        "series": "A",
        "command": "/dia",
        "definition": (
            "Judgment, critical assessment, decision. Is this correct? "
            "Adversarial review. Devil's advocate. Quality verification. "
            "Pass/fail determination. Accuracy validation."
        ),
    },
    "A3": {
        "name": "Gnōmē (格言)",
        "series": "A",
        "command": "/gno",
        "definition": (
            "Maxim, principle extraction, lesson learned. What is the rule? "
            "Pattern recognition. Law derivation. Wisdom distillation. "
            "Converting experience into reusable principles."
        ),
    },
    "A4": {
        "name": "Epistēmē (知識)",
        "series": "A",
        "command": "/epi",
        "definition": (
            "Knowledge, belief-to-knowledge promotion. Is this proven? "
            "Evidence-based knowledge establishment. Verification and validation. "
            "Transforming opinion into established fact."
        ),
    },
}

# PURPOSE: X-series morphism 定義 — 24 定理間の遷移関係
# WF frontmatter の morphisms から機械的に構築
# 各定理は 2 つの Series (8 theorems) への射を持つ = 定理あたり最大 8 射
MORPHISM_MAP: dict[str, list[str]] = {
    # O-series >>S, >>H (Pure, anchor_via=[])
    "O1": ["S1", "S2", "S3", "S4", "H1", "H2", "H3", "H4"],
    "O2": ["S1", "S2", "S3", "S4", "H1", "H2", "H3", "H4"],
    "O3": ["S1", "S2", "S3", "S4", "H1", "H2", "H3", "H4"],
    "O4": ["S1", "S2", "S3", "S4", "H1", "H2", "H3", "H4"],
    # S-series >>H, >>K (anchor_via=[O, P])
    "S1": ["H1", "H2", "H3", "H4", "K1", "K2", "K3", "K4"],
    "S2": ["H1", "H2", "H3", "H4", "K1", "K2", "K3", "K4"],
    "S3": ["H1", "H2", "H3", "H4", "K1", "K2", "K3", "K4"],
    "S4": ["H1", "H2", "H3", "H4", "K1", "K2", "K3", "K4"],
    # H-series >>S, >>K (anchor_via=[O, A])
    "H1": ["S1", "S2", "S3", "S4", "K1", "K2", "K3", "K4"],
    "H2": ["S1", "S2", "S3", "S4", "K1", "K2", "K3", "K4"],
    "H3": ["S1", "S2", "S3", "S4", "K1", "K2", "K3", "K4"],
    "H4": ["S1", "S2", "S3", "S4", "K1", "K2", "K3", "K4"],
    # P-series >>S, >>K (anchor_via=[S, K])
    "P1": ["S1", "S2", "S3", "S4", "K1", "K2", "K3", "K4"],
    "P2": ["S1", "S2", "S3", "S4", "K1", "K2", "K3", "K4"],
    "P3": ["S1", "S2", "S3", "S4", "K1", "K2", "K3", "K4"],
    "P4": ["S1", "S2", "S3", "S4", "K1", "K2", "K3", "K4"],
    # K-series >>S, >>H (anchor_via=[P, A])
    "K1": ["S1", "S2", "S3", "S4", "H1", "H2", "H3", "H4"],
    "K2": ["S1", "S2", "S3", "S4", "H1", "H2", "H3", "H4"],
    "K3": ["S1", "S2", "S3", "S4", "H1", "H2", "H3", "H4"],
    "K4": ["S1", "S2", "S3", "S4", "H1", "H2", "H3", "H4"],
    # A-series >>H, >>K (anchor_via=[H, K])
    "A1": ["H1", "H2", "H3", "H4", "K1", "K2", "K3", "K4"],
    "A2": ["H1", "H2", "H3", "H4", "K1", "K2", "K3", "K4"],
    "A3": ["H1", "H2", "H3", "H4", "K1", "K2", "K3", "K4"],
    "A4": ["H1", "H2", "H3", "H4", "K1", "K2", "K3", "K4"],
}

# Theorem keys in canonical order
THEOREM_KEYS = [
    "O1", "O2", "O3", "O4",
    "S1", "S2", "S3", "S4",
    "H1", "H2", "H3", "H4",
    "P1", "P2", "P3", "P4",
    "K1", "K2", "K3", "K4",
    "A1", "A2", "A3", "A4",
]
assert len(THEOREM_KEYS) == 24


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

# PURPOSE: 定理レベルの attractor 収束結果
@dataclass
class TheoremResult:
    """定理レベルの attractor 収束結果"""
    theorem: str
    name: str
    series: str
    similarity: float
    command: str

    def __repr__(self) -> str:
        return f"⟨{self.theorem}: {self.name} | sim={self.similarity:.3f}⟩"


# PURPOSE: X-series flow simulation の各ステップ
@dataclass
class FlowState:
    """X-series flow simulation の各ステップ"""
    step: int
    activation: np.ndarray  # (24,)
    top_theorems: list[tuple[str, float]]  # [(theorem, activation), ...]

    def __repr__(self) -> str:
        tops = ", ".join(f"{t}={v:.3f}" for t, v in self.top_theorems[:3])
        return f"⟨Step {self.step}: {tops}⟩"


# PURPOSE: Flow simulation の完全な結果
@dataclass
class FlowResult:
    """Flow simulation の完全な結果"""
    initial_similarities: list[tuple[str, float]]
    states: list[FlowState]
    converged_at: int  # 収束ステップ (-1 = 未収束)
    final_theorems: list[tuple[str, float]]

    def __repr__(self) -> str:
        tops = "+".join(t for t, _ in self.final_theorems[:3])
        return f"⟨Flow: {tops} | converged={self.converged_at}⟩"


# PURPOSE: Monte Carlo basin detection の結果
@dataclass
class BasinResult:
    """Monte Carlo basin detection の結果"""
    n_samples: int
    basin_sizes: dict[str, int]  # {theorem: count}
    basin_fractions: dict[str, float]  # {theorem: fraction}
    elapsed: float

    def __repr__(self) -> str:
        top = sorted(self.basin_fractions.items(), key=lambda x: x[1], reverse=True)[:5]
        tops = ", ".join(f"{t}={v:.1%}" for t, v in top)
        return f"⟨Basins({self.n_samples}): {tops}⟩"


# PURPOSE: Q2 — 24 定理の確率分布 (認知の配合)
@dataclass
class TheoremMixture:
    """24 定理の確率分布 (配合).

    argmax 的な「1つの答え」ではなく、
    入力がどの定理にどれだけ引かれているかの全体像を提供する。
    """
    distribution: dict[str, float]      # {theorem: probability}, 合計≈1.0
    top_theorems: list[TheoremResult]   # top-K (suggest と同じ)
    entropy: float                      # 正規化 entropy (0=支配的, 1=完全均一)
    dominant_series: str                # 最も支配的な Series
    series_distribution: dict[str, float]  # Series 別集約 {O: 0.3, S: 0.2, ...}
    temperature: float                  # 使用された temperature

    def __repr__(self) -> str:
        top = sorted(self.distribution.items(), key=lambda x: x[1], reverse=True)[:3]
        tops = " + ".join(f"{t}({v:.0%})" for t, v in top)
        return f"⟨Mixture: {tops} | H={self.entropy:.2f} | dom={self.dominant_series}⟩"


# ---------------------------------------------------------------------------
# Q3: TheoremLogger — 定理レベル記憶
# ---------------------------------------------------------------------------

# PURPOSE: Q3 — 定理の使用履歴追跡 + セッション内減衰
class TheoremLogger:
    """定理の使用履歴追跡.

    JSONL 形式で使用ログを保存し、過少使用定理のブーストと
    セッション内の既使用定理の減衰を提供する。
    """
    LOG_DIR = Path.home() / "oikos" / "mneme" / ".hegemonikon" / "logs"

    def __init__(self):
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)

    def _log_path(self) -> Path:
        """今日のログファイルパス."""
        from datetime import date
        return self.LOG_DIR / f"theorem_log_{date.today().isoformat()}.jsonl"

    # PURPOSE: theorem_attractor の log 処理を実行する
    def log(self, theorem: str, input_text: str, similarity: float) -> None:
        """使用を記録."""
        entry = {
            "ts": time.time(),
            "theorem": theorem,
            "input": input_text[:100],
            "sim": round(similarity, 4),
        }
        try:
            with open(self._log_path(), "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass  # Logging failure should not break attractor

    # PURPOSE: usage counts を取得する
    def get_usage_counts(self, days: int = 7) -> dict[str, int]:
        """直近 N 日間の定理別使用回数."""
        counts: dict[str, int] = {k: 0 for k in THEOREM_KEYS}
        from datetime import date, timedelta
        for d in range(days):
            day = date.today() - timedelta(days=d)
            path = self.LOG_DIR / f"theorem_log_{day.isoformat()}.jsonl"
            if not path.exists():
                continue
            try:
                for line in path.read_text(encoding="utf-8").strip().split("\n"):
                    if not line:
                        continue
                    entry = json.loads(line)
                    t = entry.get("theorem", "")
                    if t in counts:
                        counts[t] += 1
            except Exception:
                continue
        return counts

    # PURPOSE: novelty boost を計算する
    def compute_novelty_boost(self, days: int = 7) -> dict[str, float]:
        """過少使用定理のブースト係数 (1.0 = 平均, >1.0 = 過少使用)."""
        counts = self.get_usage_counts(days)
        total = sum(counts.values())
        if total == 0:
            return {k: 1.0 for k in THEOREM_KEYS}
        avg = total / 24
        boost = {}
        for k in THEOREM_KEYS:
            if counts[k] == 0:
                boost[k] = 1.5  # 未使用 → 50% ブースト
            elif counts[k] < avg:
                boost[k] = 1.0 + 0.5 * (1 - counts[k] / avg)  # 1.0-1.5
            else:
                boost[k] = 1.0  # 十分使用済み → ブーストなし
        return boost


# ---------------------------------------------------------------------------
# TheoremAttractor
# ---------------------------------------------------------------------------

# PURPOSE: 24 定理レベルの Attractor Engine + X-series Flow Simulator
class TheoremAttractor:
    """24 定理レベルの Attractor Engine + X-series Flow Simulator

    Usage:
        ta = TheoremAttractor()

        # 1. 定理レベル引力計算
        results = ta.suggest("なぜこの設計が今必要なのか")
        # → [⟨O1: Noēsis | sim=0.42⟩, ⟨S2: Mekhanē | sim=0.41⟩, ...]

        # 2. X-series flow simulation
        flow = ta.simulate_flow("なぜこの設計が今必要なのか", steps=10)
        # → 認知の軌道: O1 → S2 (via X-OS) → ...

        # 3. Monte Carlo basin detection (GPU)
        basins = ta.detect_basins(n_samples=10000)
        # → 各定理の basin サイズ分布
    """

    def __init__(self, force_cpu: bool = False, enable_memory: bool = True):
        self._embedder = None
        self._proto_tensor = None  # (24, D) GPU tensor
        self._transition_matrix = None  # (24, 24) GPU tensor
        self._device = None
        self._force_cpu = force_cpu
        self._initialized = False
        # Q3: 定理レベル記憶
        self._logger = TheoremLogger() if enable_memory else None
        self._session_used: list[str] = []  # セッション内で使用した定理
        self._decay_factor = 0.7  # 使用済み定理の similarity 減衰率
        # Q4: multiview prototype
        self._multiview_proto = None  # (24, D) definition+WF
        # Q7: inhibition matrix
        self._inhibition_matrix = None  # (24, 24)

    # --- Initialization ---

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return

        from mekhane.anamnesis.index import Embedder
        self._embedder = Embedder(force_cpu=self._force_cpu)

        # 24 定理の prototype embedding
        texts = [THEOREM_DEFINITIONS[k]["definition"] for k in THEOREM_KEYS]
        embeddings = self._embedder.embed_batch(texts)
        proto_matrix = np.array(embeddings, dtype=np.float32)

        # X-series 遷移行列 (24×24) — Q5: cosine sim based weighting
        T = np.zeros((24, 24), dtype=np.float32)
        key_to_idx = {k: i for i, k in enumerate(THEOREM_KEYS)}

        # Prototype 間の cosine similarity → 遷移の重み
        proto_norms = np.linalg.norm(proto_matrix, axis=1, keepdims=True)
        proto_norms[proto_norms == 0] = 1
        proto_normed = proto_matrix / proto_norms

        for src, targets in MORPHISM_MAP.items():
            src_idx = key_to_idx[src]
            for tgt in targets:
                tgt_idx = key_to_idx[tgt]
                # cosine sim → clamp [0.1, 1.0]
                weight = float(proto_normed[src_idx] @ proto_normed[tgt_idx])
                T[src_idx, tgt_idx] = max(0.1, weight)

        # Row-normalize (確率遷移行列にする)
        row_sums = T.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        T = T / row_sums

        # Sinkhorn 正規化: doubly stochastic に近似
        # (in-degree の偏りによる S/H への過集中を緩和)
        for _ in range(10):
            col_sums = T.sum(axis=0, keepdims=True)
            col_sums[col_sums == 0] = 1
            T = T / col_sums  # column normalize
            row_sums = T.sum(axis=1, keepdims=True)
            row_sums[row_sums == 0] = 1
            T = T / row_sums  # row normalize

        # 自己ループの追加 (安定化)
        alpha = 0.3  # 30% 自己保持
        T = (1 - alpha) * T + alpha * np.eye(24, dtype=np.float32)

        # GPU tensor 化
        if TORCH_AVAILABLE:
            from mekhane.fep.gpu import get_device, to_tensor
            self._device = get_device(force_cpu=self._force_cpu)
            self._proto_tensor = to_tensor(proto_matrix, self._device)
            self._transition_matrix = to_tensor(T, self._device)
            print(f"[TheoremAttractor] GPU mode ({self._device}), "
                  f"{len(THEOREM_KEYS)} theorems, "
                  f"{sum(len(v) for v in MORPHISM_MAP.values())} morphisms",
                  flush=True)
        else:
            self._proto_tensor = proto_matrix
            self._transition_matrix = T
            print("[TheoremAttractor] CPU mode", flush=True)

        self._initialized = True

        # Q4: Multiview prototype (definition 0.7 + WF description 0.3)
        self._multiview_proto = self._build_multiview_proto(proto_matrix)

        # Q7: Inhibition matrix (cosine distance based)
        self._inhibition_matrix = self._build_inhibition_matrix(proto_normed)

    # --- Private Builders (Q4, Q7) ---

    # PURPOSE: Q4 — Definition + WF description の multiview prototype 構築
    def _build_multiview_proto(self, def_matrix: np.ndarray) -> Optional[np.ndarray]:
        """Definition (0.7) + WF description (0.3) の加重平均 embedding.

        WF ファイルが見つからない定理は definition のみ (weight=1.0)。
        """
        wf_dir = Path(__file__).parent.parent.parent / ".agent" / "workflows"
        if not wf_dir.exists():
            return None

        # 各定理の WF description を収集
        wf_texts = []
        for k in THEOREM_KEYS:
            cmd = THEOREM_DEFINITIONS[k]["command"].lstrip("/")
            wf_path = wf_dir / f"{cmd}.md"
            desc = ""
            if wf_path.exists():
                try:
                    content = wf_path.read_text(encoding="utf-8")
                    # YAML frontmatter の description を抽出
                    if content.startswith("---"):
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            for line in parts[1].strip().split("\n"):
                                if line.startswith("description:"):
                                    desc = line.split(":", 1)[1].strip().strip('"').strip("'")
                                    break
                    if not desc:
                        # Fallback: 最初の非空行 (h1 以降)
                        for line in content.split("\n"):
                            stripped = line.strip()
                            if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
                                desc = stripped[:200]
                                break
                except Exception:
                    pass
            wf_texts.append(desc if desc else THEOREM_DEFINITIONS[k]["definition"])

        # WF embedding
        wf_embeddings = self._embedder.embed_batch(wf_texts)
        wf_matrix = np.array(wf_embeddings, dtype=np.float32)

        # Multiview: weighted average
        alpha = 0.7  # definition weight
        multiview = alpha * def_matrix + (1 - alpha) * wf_matrix

        print(f"[TheoremAttractor] Q4: multiview proto built "
              f"(def={alpha:.0%} + wf={1-alpha:.0%})", flush=True)
        return multiview

    # PURPOSE: Q7 — 抑制行列構築 (cosine distance → inhibition strength)
    def _build_inhibition_matrix(self, proto_normed: np.ndarray) -> np.ndarray:
        """Cosine distance → 行正規化された inhibition strength.

        距離が大きいほど抑制が強い。同一 theorem は 0。
        行正規化: transition matrix と同スケール (行和≈1) にする。
        """
        sim_matrix = proto_normed @ proto_normed.T
        dist_matrix = 1.0 - sim_matrix
        np.fill_diagonal(dist_matrix, 0)
        # 行正規化: transition matrix と同スケールにする
        row_sums = dist_matrix.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        dist_matrix = dist_matrix / row_sums
        return dist_matrix.astype(np.float32)

    # --- 1. Theorem-Level Attractor ---

    # PURPOSE: 入力に最も引力の強い定理を返す (Q3: セッション内減衰付き)
    def suggest(self, user_input: str, top_k: int = 5) -> list[TheoremResult]:
        """入力に最も引力の強い定理を返す.

        Q3: セッション内で既に使用した定理は similarity を decay_factor (0.7x) で減衰。
        これにより同一セッション内で異なる定理への探索を促す。
        """
        self._ensure_initialized()
        sims = self._compute_similarities(user_input)

        # Q3: セッション内減衰
        if self._session_used:
            sims = [
                (t, s * self._decay_factor if t in self._session_used else s)
                for t, s in sims
            ]

        results = []
        for theorem, sim in sorted(sims, key=lambda x: x[1], reverse=True)[:top_k]:
            defn = THEOREM_DEFINITIONS[theorem]
            results.append(TheoremResult(
                theorem=theorem,
                name=defn["name"],
                series=defn["series"],
                similarity=sim,
                command=defn["command"],
            ))

        # Q3: top-1 をログ + セッション使用済みに追加
        if results and self._logger:
            top = results[0]
            self._logger.log(top.theorem, user_input, top.similarity)
            if top.theorem not in self._session_used:
                self._session_used.append(top.theorem)

        return results

    # --- 1b. Mixture Diagnosis (Q2) ---

    # PURPOSE: Q2 — 24 定理の配合を確率分布として出力
    def diagnose_mixture(
        self, user_input: str, temperature: float = 0.05, top_k: int = 5,
    ) -> TheoremMixture:
        """24 定理の配合を確率分布として出力.

        argmax (suggest) が「何」を返すのに対し、
        mixture は「どれくらいの強さで」を返す。

        Args:
            temperature: 低い=尖った分布, 高い=平坦。
                0.05 default — similarity range が狭い (0.35-0.48) ため
                高い T では均一分布になり情報量ゼロになる。
            top_k: top_theorems に含める数。
        """
        self._ensure_initialized()
        sims = self._compute_similarities(user_input)

        # similarity → probability distribution (softmax)
        sim_values = np.array(
            [s for _, s in sorted(sims, key=lambda x: THEOREM_KEYS.index(x[0]))],
            dtype=np.float32,
        )
        probs = self._softmax(sim_values, temperature=temperature)

        # distribution dict
        distribution = {k: float(probs[i]) for i, k in enumerate(THEOREM_KEYS)}

        # Series 集約
        series_dist: dict[str, float] = {}
        for k, p in distribution.items():
            s = THEOREM_DEFINITIONS[k]["series"]
            series_dist[s] = series_dist.get(s, 0.0) + p
        dominant_series = max(series_dist, key=series_dist.get)  # type: ignore

        # Shannon entropy (正規化: 0=支配的, 1=完全均一)
        max_entropy = math.log(24)
        entropy = -sum(p * math.log(p + 1e-12) for p in probs)
        norm_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        # top-K TheoremResults
        top_results = self.suggest(user_input, top_k=top_k)

        return TheoremMixture(
            distribution=distribution,
            top_theorems=top_results,
            entropy=round(norm_entropy, 4),
            dominant_series=dominant_series,
            series_distribution={s: round(v, 4) for s, v in series_dist.items()},
            temperature=temperature,
        )

    # --- 1c. Basin Separation (Q1) ---

    # PURPOSE: Q1 — 24 定理間の分離度メトリクス
    def basin_separation(self) -> dict:
        """24 定理間の embedding 距離行列 + 分離度の低いペアを報告.

        Returns:
            distance_matrix: (24, 24) cosine distance
            closest_pairs: 最も近い 5 ペア
            avg_separation: 平均分離度
            min_separation: 最小分離度
        """
        self._ensure_initialized()
        proto = self._proto_tensor
        if hasattr(proto, 'cpu'):
            proto = proto.cpu().numpy()

        # L2 正規化
        norms = np.linalg.norm(proto, axis=1, keepdims=True)
        norms[norms == 0] = 1
        normed = proto / norms

        # Cosine distance matrix: 1 - cosine_sim
        sim_matrix = normed @ normed.T
        dist_matrix = 1.0 - sim_matrix

        # 上三角の distance を収集 (自分自身を除く)
        pairs = []
        for i in range(24):
            for j in range(i + 1, 24):
                pairs.append((THEOREM_KEYS[i], THEOREM_KEYS[j], float(dist_matrix[i, j])))

        pairs.sort(key=lambda x: x[2])
        dists = [p[2] for p in pairs]

        return {
            "distance_matrix": dist_matrix,
            "closest_pairs": pairs[:5],
            "farthest_pairs": pairs[-5:],
            "avg_separation": float(np.mean(dists)),
            "min_separation": float(min(dists)) if dists else 0,
            "max_separation": float(max(dists)) if dists else 0,
        }

    # --- 1d. Multiview Suggest (Q4) ---

    # PURPOSE: Q4 — WF 全文を加味した multiview prototype で suggest
    def suggest_multiview(self, user_input: str, top_k: int = 5) -> list[TheoremResult]:
        """Q4: Definition + WF description の multiview prototype で suggest.

        通常の suggest() が definition のみを見るのに対し、
        こちらは WF の description も加味した広い視野で判定する。
        """
        self._ensure_initialized()
        if self._multiview_proto is None:
            return self.suggest(user_input, top_k=top_k)  # fallback

        input_emb = self._embedder.embed_batch([user_input])
        input_vec = np.array(input_emb[0], dtype=np.float32)

        # multiview proto との cosine similarity
        mv_proto = self._multiview_proto
        if hasattr(mv_proto, 'cpu'):
            mv_proto = mv_proto.cpu().numpy()

        proto_norms = np.linalg.norm(mv_proto, axis=1)
        input_norm = np.linalg.norm(input_vec)
        if input_norm == 0:
            input_norm = 1
        proto_norms[proto_norms == 0] = 1
        sims = (mv_proto @ input_vec) / (proto_norms * input_norm)

        results = []
        indexed_sims = [(THEOREM_KEYS[i], float(sims[i])) for i in range(24)]
        for theorem, sim in sorted(indexed_sims, key=lambda x: x[1], reverse=True)[:top_k]:
            defn = THEOREM_DEFINITIONS[theorem]
            results.append(TheoremResult(
                theorem=theorem,
                name=defn["name"],
                series=defn["series"],
                similarity=sim,
                command=defn["command"],
            ))
        return results

    # --- 1e. Inhibition Query (Q7) ---

    # PURPOSE: Q7 — ある定理の“抑制対象”を返す
    def get_inhibited(self, theorem: str, threshold: float = 0.5) -> list[tuple[str, float]]:
        """Q7: 指定定理が抑制する定理を返す.

        抑制 = cosine distance > threshold の定理。
        「この定理が活性化するとき、どの定理が押されるか」。

        Args:
            theorem: e.g. "O1"
            threshold: inhibition threshold (default 0.5)

        Returns:
            [(theorem, inhibition_strength), ...] sorted by strength
        """
        self._ensure_initialized()
        if self._inhibition_matrix is None or theorem not in THEOREM_KEYS:
            return []

        idx = THEOREM_KEYS.index(theorem)
        inhib = self._inhibition_matrix
        if hasattr(inhib, 'cpu'):
            inhib = inhib.cpu().numpy()

        row = inhib[idx]
        pairs = []
        for i, strength in enumerate(row):
            if i != idx and strength > threshold:
                pairs.append((THEOREM_KEYS[i], float(strength)))
        return sorted(pairs, key=lambda x: x[1], reverse=True)

    # --- 1f. Keyword Decomposition (Q6) ---

    # PURPOSE: Q6 — 入力をキーワード分解し、各要素で suggest
    def suggest_decomposed(self, user_input: str, top_k: int = 3) -> dict:
        """Q6: 入力をキーワード分解し、各要素で別々に suggest.

        LLM-free: 単純なトークン分割で「何を」「どう」「なぜ」を抽出。
        完全な分解はせず、「N-gram 窓」で入力の部分ごとに Attractor を通す。

        Returns:
            {
                "full": [TheoremResult, ...],  # 全文での suggest
                "segments": [
                    {"text": str, "theorems": [TheoremResult, ...]},
                    ...
                ],
                "divergence": float,  # segment 間の不一致度
            }
        """
        self._ensure_initialized()

        # 全文 suggest
        full_results = self.suggest(user_input, top_k=top_k)

        # セグメント分割: 句点、「、」「。」「、」「。」 で分割
        import re
        segments_text = re.split(r'[、。,.　]+', user_input)
        segments_text = [s.strip() for s in segments_text if len(s.strip()) > 3]

        if len(segments_text) <= 1:
            # 分解できない (1 segment)
            return {
                "full": full_results,
                "segments": [{"text": user_input, "theorems": full_results}],
                "divergence": 0.0,
            }

        segments = []
        all_top1 = set()
        for seg in segments_text:
            seg_results = self.suggest(seg, top_k=top_k)
            segments.append({"text": seg, "theorems": seg_results})
            if seg_results:
                all_top1.add(seg_results[0].theorem)

        # divergence: 何個の異なる top-1 theorem があるか
        # 1 = 全 segment が同じ theorem, n/n = 全 segment が異なる theorem
        n_seg = len(segments)
        divergence = (len(all_top1) - 1) / max(n_seg - 1, 1) if n_seg > 1 else 0.0

        return {
            "full": full_results,
            "segments": segments,
            "divergence": round(divergence, 3),
        }

    # --- 2. X-series Flow Simulation ---

    # PURPOSE: 入力の初期 activation を X-series 遷移行列で伝播シミュレーション
    def simulate_flow(
        self,
        user_input: str,
        steps: int = 10,
        convergence_threshold: float = 0.001,
        temperature: float = 0.3,
    ) -> FlowResult:
        """入力の初期 activation を X-series 遷移行列で伝播シミュレーション.

        Args:
            temperature: softmax 温度。低い=鋭い初期分布、高い=均一な初期分布。
                         simulate_flow_ei() と同一デフォルト値で統一。
        """
        self._ensure_initialized()

        # 初期 activation = cosine similarity
        sims = self._compute_similarities(user_input)
        initial = np.array([s for _, s in sorted(sims, key=lambda x: THEOREM_KEYS.index(x[0]))],
                           dtype=np.float32)

        # Softmax で確率分布化
        initial = self._softmax(initial, temperature=temperature)

        if TORCH_AVAILABLE and self._device is not None and self._device.type == "cuda":
            states = self._simulate_gpu(initial, steps, convergence_threshold)
        else:
            states = self._simulate_cpu(initial, steps, convergence_threshold)

        # 収束判定
        converged_at = -1
        for i in range(1, len(states)):
            diff = np.abs(states[i].activation - states[i-1].activation).max()
            if diff < convergence_threshold:
                converged_at = i
                break

        final_tops = states[-1].top_theorems

        return FlowResult(
            initial_similarities=sorted(sims, key=lambda x: x[1], reverse=True),
            states=states,
            converged_at=converged_at,
            final_theorems=final_tops,
        )

    def _simulate_gpu(self, initial: np.ndarray, steps: int, threshold: float) -> list[FlowState]:
        """GPU 行列積でフロー伝播."""
        from mekhane.fep.gpu import to_tensor
        state = to_tensor(initial, self._device)
        T = self._transition_matrix
        states = [self._make_flow_state(0, initial)]

        for step in range(1, steps + 1):
            state = state @ T
            # Re-normalize
            state = state / state.sum()
            state_np = state.cpu().numpy()
            states.append(self._make_flow_state(step, state_np))

            # Early convergence check
            if step > 1:
                diff = np.abs(state_np - states[-2].activation).max()
                if diff < threshold:
                    break

        return states

    def _simulate_cpu(self, initial: np.ndarray, steps: int, threshold: float) -> list[FlowState]:
        """CPU 行列積でフロー伝播."""
        state = initial.copy()
        T = self._transition_matrix if isinstance(self._transition_matrix, np.ndarray) \
            else self._transition_matrix.cpu().numpy()
        states = [self._make_flow_state(0, state)]

        for step in range(1, steps + 1):
            state = state @ T
            state = state / state.sum()
            states.append(self._make_flow_state(step, state.copy()))

            if step > 1:
                diff = np.abs(state - states[-2].activation).max()
                if diff < threshold:
                    break

        return states

    # --- 2b. Excitation-Inhibition Flow (E/I) ---

    # PURPOSE: 興奮-抑制統合の flow simulation
    def simulate_flow_ei(
        self,
        user_input: str,
        steps: int = 15,
        beta: float = 0.3,
        convergence_threshold: float = 0.001,
        temperature: float = 0.3,
    ) -> FlowResult:
        """興奮-抑制統合の flow simulation.

        通常の simulate_flow() が興奮射のみで伝播するのに対し、
        こちらは各ステップで抑制を同時に適用する。

        各ステップ:
            excitation = state @ T           (興奮: 遷移行列)
            inhibition = state @ I           (抑制: distance 行列)
            next_state = ReLU(excitation - β * inhibition)
            next_state = normalize(next_state)

        Args:
            beta: 抑制の強さ (0=抑制なし=通常flow, 1=最大抑制)
            steps: シミュレーションステップ数
            temperature: softmax 温度。simulate_flow() と同一デフォルト値。

        Note:
            inhibition matrix と precision_weighting (PW) の関係:
            - PW は各定理の「信頼度」を重み付けする (prior modulation)
            - inhibition は定理間の「排他的競合」をモデル化 (lateral inhibition)
            - 両者は直交する操作: PW=縦方向スケール、I=横方向抑制
        """
        self._ensure_initialized()

        # 初期 activation
        sims = self._compute_similarities(user_input)
        initial = np.array(
            [s for _, s in sorted(sims, key=lambda x: THEOREM_KEYS.index(x[0]))],
            dtype=np.float32,
        )
        initial = self._softmax(initial, temperature=temperature)

        # Inhibition matrix
        inhib = self._inhibition_matrix
        if inhib is None:
            # Fallback to excitation-only
            return self.simulate_flow(user_input, steps=steps,
                                      convergence_threshold=convergence_threshold)

        if TORCH_AVAILABLE and self._device is not None and self._device.type == "cuda":
            states = self._simulate_ei_gpu(initial, inhib, steps, beta, convergence_threshold)
        else:
            states = self._simulate_ei_cpu(initial, inhib, steps, beta, convergence_threshold)

        # 収束判定
        converged_at = -1
        for i in range(1, len(states)):
            diff = np.abs(states[i].activation - states[i - 1].activation).max()
            if diff < convergence_threshold:
                converged_at = i
                break

        return FlowResult(
            initial_similarities=sorted(sims, key=lambda x: x[1], reverse=True),
            states=states,
            converged_at=converged_at,
            final_theorems=states[-1].top_theorems,
        )

    def _simulate_ei_gpu(
        self,
        initial: np.ndarray,
        inhib: np.ndarray,
        steps: int,
        beta: float,
        threshold: float,
    ) -> list[FlowState]:
        """GPU E/I flow."""
        from mekhane.fep.gpu import to_tensor
        state = to_tensor(initial, self._device)
        T = self._transition_matrix
        I = to_tensor(inhib if isinstance(inhib, np.ndarray) else inhib.cpu().numpy(),
                      self._device)
        states = [self._make_flow_state(0, initial)]

        for step in range(1, steps + 1):
            excitation = state @ T
            inhibition = state @ I
            state = torch.clamp(excitation - beta * inhibition, min=0)
            # Re-normalize
            s = state.sum()
            if s > 0:
                state = state / s
            else:
                state = torch.ones_like(state) / 24  # 全抑制 → uniform fallback
            state_np = state.cpu().numpy()
            states.append(self._make_flow_state(step, state_np))

            if step > 1:
                diff = np.abs(state_np - states[-2].activation).max()
                if diff < threshold:
                    break

        return states

    def _simulate_ei_cpu(
        self,
        initial: np.ndarray,
        inhib: np.ndarray,
        steps: int,
        beta: float,
        threshold: float,
    ) -> list[FlowState]:
        """CPU E/I flow."""
        state = initial.copy()
        T = self._transition_matrix if isinstance(self._transition_matrix, np.ndarray) \
            else self._transition_matrix.cpu().numpy()
        I = inhib if isinstance(inhib, np.ndarray) else inhib.cpu().numpy()
        states = [self._make_flow_state(0, state)]

        for step in range(1, steps + 1):
            excitation = state @ T
            inhibition = state @ I
            state = np.maximum(excitation - beta * inhibition, 0)
            # Re-normalize
            s = state.sum()
            if s > 0:
                state = state / s
            else:
                state = np.ones(24, dtype=np.float32) / 24
            states.append(self._make_flow_state(step, state.copy()))

            if step > 1:
                diff = np.abs(state - states[-2].activation).max()
                if diff < threshold:
                    break

        return states

    # --- 3. Monte Carlo Basin Detection ---

    # PURPOSE: ランダム embedding でバッチ basin detection — GPU の真の居場所
    def detect_basins(self, n_samples: int = 10000) -> BasinResult:
        """ランダム embedding でバッチ basin detection — GPU の真の居場所.

        各ランダムベクトルの最も近い定理 (argmax of cosine similarity) を計算。
        flow は適用しない: これは semantic space 上の「影響圏」を測定する。
        """
        self._ensure_initialized()
        t0 = time.time()

        if TORCH_AVAILABLE and self._device is not None and self._device.type == "cuda":
            result = self._detect_basins_gpu(n_samples)
        else:
            result = self._detect_basins_cpu(n_samples)

        result.elapsed = time.time() - t0
        return result

    def _detect_basins_gpu(self, n_samples: int) -> BasinResult:
        """GPU バッチ Monte Carlo: (N, D) @ (D, 24) → argmax."""
        import torch
        from mekhane.fep.gpu import batch_cosine_similarity

        D = self._proto_tensor.shape[1]

        # ランダム embedding 生成 (unit sphere 上)
        random_vecs = torch.randn(n_samples, D, device=self._device, dtype=torch.float32)
        random_vecs = torch.nn.functional.normalize(random_vecs, p=2, dim=-1)

        # バッチ cosine similarity: (N, D) @ (D, 24) → (N, 24)
        sims = batch_cosine_similarity(random_vecs, self._proto_tensor)

        # Argmax: 各サンプルの最近接定理
        basin_indices = sims.argmax(dim=-1).cpu().numpy()

        basin_sizes = {}
        for idx in basin_indices:
            theorem = THEOREM_KEYS[idx]
            basin_sizes[theorem] = basin_sizes.get(theorem, 0) + 1

        basin_fractions = {k: v / n_samples for k, v in basin_sizes.items()}

        return BasinResult(
            n_samples=n_samples,
            basin_sizes=basin_sizes,
            basin_fractions=basin_fractions,
            elapsed=0,
        )

    def _detect_basins_cpu(self, n_samples: int) -> BasinResult:
        """CPU fallback."""
        proto = self._proto_tensor if isinstance(self._proto_tensor, np.ndarray) \
            else self._proto_tensor.cpu().numpy()
        D = proto.shape[1]

        random_vecs = np.random.randn(n_samples, D).astype(np.float32)
        norms = np.linalg.norm(random_vecs, axis=1, keepdims=True)
        random_vecs = random_vecs / norms

        proto_norm = proto / np.linalg.norm(proto, axis=1, keepdims=True)
        sims = random_vecs @ proto_norm.T  # (N, 24)

        basin_indices = sims.argmax(axis=1)

        basin_sizes = {}
        for idx in basin_indices:
            theorem = THEOREM_KEYS[idx]
            basin_sizes[theorem] = basin_sizes.get(theorem, 0) + 1

        basin_fractions = {k: v / n_samples for k, v in basin_sizes.items()}

        return BasinResult(
            n_samples=n_samples,
            basin_sizes=basin_sizes,
            basin_fractions=basin_fractions,
            elapsed=0,
        )

    # --- Internal ---

    def _compute_similarities(self, user_input: str) -> list[tuple[str, float]]:
        """全 24 定理の similarity を計算."""
        input_emb = np.array(self._embedder.embed(user_input), dtype=np.float32)

        if TORCH_AVAILABLE and self._device is not None and self._device.type == "cuda":
            from mekhane.fep.gpu import to_tensor, batch_cosine_similarity
            query = to_tensor(input_emb, self._device)
            sims = batch_cosine_similarity(query, self._proto_tensor)
            sims_np = sims.cpu().numpy()
            return [(k, float(sims_np[i])) for i, k in enumerate(THEOREM_KEYS)]
        else:
            proto = self._proto_tensor if isinstance(self._proto_tensor, np.ndarray) \
                else self._proto_tensor.cpu().numpy()
            proto_norm = proto / np.linalg.norm(proto, axis=1, keepdims=True)
            input_norm = input_emb / np.linalg.norm(input_emb)
            sims = input_norm @ proto_norm.T
            return [(k, float(sims[i])) for i, k in enumerate(THEOREM_KEYS)]

    @staticmethod
    def _softmax(x: np.ndarray, temperature: float = 1.0) -> np.ndarray:
        e = np.exp((x - x.max()) / temperature)
        return e / e.sum()

    @staticmethod
    def _softmax_batch(x: np.ndarray, temperature: float = 1.0) -> np.ndarray:
        e = np.exp((x - x.max(axis=1, keepdims=True)) / temperature)
        return e / e.sum(axis=1, keepdims=True)

    @staticmethod
    def _make_flow_state(step: int, activation: np.ndarray) -> FlowState:
        top_indices = np.argsort(activation)[::-1][:5]
        top_theorems = [(THEOREM_KEYS[i], float(activation[i])) for i in top_indices]
        return FlowState(step=step, activation=activation.copy(), top_theorems=top_theorems)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

# PURPOSE: CLI: python -m mekhane.fep.theorem_attractor "入力テキスト"
def main() -> None:
    """CLI: python -m mekhane.fep.theorem_attractor \"入力テキスト\" """
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m mekhane.fep.theorem_attractor <input_text>")
        print("       python -m mekhane.fep.theorem_attractor --basins [N]")
        sys.exit(1)

    if sys.argv[1] == "--basins":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
        ta = TheoremAttractor()
        print(f"\n🎲 Basin Detection (n={n:,})...")
        result = ta.detect_basins(n_samples=n)
        print(f"\n{'='*60}")
        print(f"Basin Map ({result.elapsed:.2f}s)")
        print(f"{'='*60}")
        for theorem in THEOREM_KEYS:
            frac = result.basin_fractions.get(theorem, 0)
            bar = "█" * int(frac * 100)
            name = THEOREM_DEFINITIONS[theorem]["name"]
            print(f"  {theorem} {name:20s} {frac:6.1%} {bar}")
        return

    user_input = " ".join(sys.argv[1:])
    ta = TheoremAttractor()

    print(f"\n入力: {user_input}")
    print("=" * 60)

    # 1. Theorem-level suggest
    results = ta.suggest(user_input, top_k=24)
    print("\n📊 全 24 定理の引力マップ:")
    for r in results:
        bar = "█" * int(r.similarity * 40)
        print(f"  {r.theorem} {r.name:20s} {r.similarity:.3f} {bar}")

    # 2. Flow simulation
    print("\n🌊 X-series Flow Simulation (10 steps):")
    flow = ta.simulate_flow(user_input, steps=10)
    for state in flow.states:
        tops = ", ".join(f"{t}={v:.3f}" for t, v in state.top_theorems[:3])
        print(f"  Step {state.step:2d}: {tops}")

    if flow.converged_at >= 0:
        print(f"  ✅ Converged at step {flow.converged_at}")
    else:
        print("  ⏳ Not converged in 10 steps")

    print(f"\n🎯 Final: {' + '.join(t for t, _ in flow.final_theorems[:3])}")


if __name__ == "__main__":
    main()
