# PROOF: [L2/進化基盤] <- .agent/projects/aristos/
"""
PROOF: [L2/進化基盤] このファイルは存在しなければならない

A0 → 認知活動は Explore/Exploit のバランスで最適化される (Function 公理)
   → 進化的探索がそのバランスを機械化する
   → Evolution Engine が担う

Q.E.D.

設計根拠:
- /ccl-nous による問い直し (2026-02-14)
- GA は手段。本質は「フィードバックループの形式化」
- Chromosome[T] を汎用に設計し、L3/L4 で拡張可能にする
- CostVector (L1) との双対構造
"""

from __future__ import annotations

import copy
import json
import logging
import random
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
)

logger = logging.getLogger(__name__)

# =============================================================================
# Scale — 階層的 GA のスケール
# =============================================================================

# PURPOSE: 進化のスケールを定義。スケールごとに変異率が異なる。
#   小さいものほど早く激しく、大きいものほど遅く小さく変化する。


class Scale(Enum):
    """進化のスケール (= FEP 階層的生成モデルの層)"""

    MICRO = "micro"   # 派生重みの進化 (高変異率)
    MESO = "meso"     # マクロ構成の進化 (中変異率) — L3
    MACRO = "macro"   # WF 構造の進化 (低変異率) — L4


# Scale → 変異率のデフォルトマッピング
SCALE_MUTATION_RATES: Dict[Scale, float] = {
    Scale.MICRO: 0.30,   # 30% — 頻繁に微調整
    Scale.MESO: 0.10,    # 10% — 時々構造変更
    Scale.MACRO: 0.03,   #  3% — 滅多に変えない
}

# Scale → 変異幅 (σ)
SCALE_MUTATION_SIGMA: Dict[Scale, float] = {
    Scale.MICRO: 0.20,
    Scale.MESO: 0.10,
    Scale.MACRO: 0.05,
}


# =============================================================================
# FitnessVector — 多軸適合度 (CostVector の双対)
# =============================================================================

# PURPOSE: CostVector がコストの多軸表現なら、
#   FitnessVector は適合度の多軸表現。方向が逆なだけで構造は同一。


@dataclass
class FitnessVector:
    """多軸適合度ベクトル (CostVector の双対)

    CostVector: 小さいほど良い (コスト最小化)
    FitnessVector: 大きいほど良い (適合度最大化)
    """

    depth: float = 0.0       # 認知深度到達 (0.0 ~ 4.0)
    precision: float = 0.0   # 選択精度 (0.0 ~ 1.0)
    efficiency: float = 0.0  # pt 効率 (成果 / コスト)
    novelty: float = 0.0     # 新規性 (0.0 ~ 1.0)

    def scalar(self, weights: Optional[Dict[str, float]] = None) -> float:
        """加重スカラー適合度を算出"""
        w = weights or {
            "depth": 1.0,
            "precision": 2.0,
            "efficiency": 0.5,
            "novelty": 0.3,
        }
        return (
            self.depth * w.get("depth", 1.0)
            + self.precision * w.get("precision", 2.0)
            + self.efficiency * w.get("efficiency", 0.5)
            + self.novelty * w.get("novelty", 0.3)
        )

    def __repr__(self) -> str:
        return (
            f"Fitness(depth={self.depth:.2f}, prec={self.precision:.2f}, "
            f"eff={self.efficiency:.2f}, nov={self.novelty:.2f}, "
            f"scalar={self.scalar():.3f})"
        )


# =============================================================================
# Chromosome[T] — 汎用個体
# =============================================================================

# PURPOSE: GA の個体を型パラメータで汎用化。
#   L2: T = dict[str, float] (キーワード重み)
#   L3: T = MacroConfig (マクロ構成)
#   L4: T = WFInstruction (WF 定義)

T = TypeVar("T")


@dataclass
class Chromosome(Generic[T]):
    """GA の個体 — 汎用型パラメータ T で遺伝子を表現

    L2 では T = dict[str, float] (キーワードパターンの重み)。
    L3+ で MacroConfig | WFInstruction に拡張可能。
    """

    genes: T
    fitness: FitnessVector = field(default_factory=FitnessVector)
    generation: int = 0

    def __repr__(self) -> str:
        gene_preview = str(self.genes)
        if len(gene_preview) > 60:
            gene_preview = gene_preview[:57] + "..."
        return f"Chromosome(gen={self.generation}, {self.fitness}, genes={gene_preview})"


# =============================================================================
# FeedbackEntry — フィードバック1件
# =============================================================================


@dataclass
class FeedbackEntry:
    """Creator のフィードバック1件

    暗黙フィードバック: corrected_to = None (修正なし = 承認)
    明示フィードバック: corrected_to = "nous" (Creator が修正)
    """

    theorem: str           # O1, S2, etc.
    problem: str           # 入力テキスト
    selected: str          # AI が選んだ派生
    corrected_to: Optional[str] = None  # Creator 修正 (None = 承認)
    confidence: float = 0.0
    method: str = "keyword"  # "keyword" | "llm"

    @property
    def was_correct(self) -> bool:
        """選択が承認されたか (修正なし = 正解)"""
        return self.corrected_to is None


# =============================================================================
# FeedbackCollector — 暗黙 + 明示フィードバック収集
# =============================================================================


class FeedbackCollector:
    """フィードバックの収集・永続化・読み込み

    暗黙フィードバック: 修正なし = 承認 (重み 0.3)
    明示フィードバック: Creator が /u で修正 (重み 1.0)
    LLM フォールバック: キーワード不足のシグナル (重み 0.5)
    """

    SIGNAL_WEIGHTS = {
        "implicit_approve": 0.3,
        "explicit_correct": 1.0,
        "llm_fallback": 0.5,
    }

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or Path("data/feedback.json")
        self._entries: List[FeedbackEntry] = []

    def add(self, entry: FeedbackEntry) -> None:
        """フィードバックを追加"""
        self._entries.append(entry)

    def load(self) -> List[FeedbackEntry]:
        """永続化ファイルからフィードバックを読み込み"""
        if not self.path.exists():
            return []

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)

            entries = []
            for item in data.get("feedback", []):
                entries.append(
                    FeedbackEntry(
                        theorem=item["theorem"],
                        problem=item["problem"],
                        selected=item["selected"],
                        corrected_to=item.get("corrected_to"),
                        confidence=item.get("confidence", 0.0),
                        method=item.get("method", "keyword"),
                    )
                )
            self._entries = entries
            return entries
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to load feedback: {e}")
            return []

    def save(self) -> None:
        """フィードバックをファイルに永続化"""
        self.path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "feedback": [
                {
                    "theorem": e.theorem,
                    "problem": e.problem,
                    "selected": e.selected,
                    "corrected_to": e.corrected_to,
                    "confidence": e.confidence,
                    "method": e.method,
                }
                for e in self._entries[-1000:]  # 最新1000件
            ]
        }

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def for_theorem(self, theorem: str) -> List[FeedbackEntry]:
        """特定の定理に関するフィードバックを取得"""
        return [e for e in self._entries if e.theorem == theorem]

    def signal_weight(self, entry: FeedbackEntry) -> float:
        """フィードバックの重みを計算"""
        if entry.corrected_to is not None:
            return self.SIGNAL_WEIGHTS["explicit_correct"]
        elif entry.method == "llm":
            return self.SIGNAL_WEIGHTS["llm_fallback"]
        else:
            return self.SIGNAL_WEIGHTS["implicit_approve"]

    @property
    def entries(self) -> List[FeedbackEntry]:
        return list(self._entries)

    def __len__(self) -> int:
        return len(self._entries)


# =============================================================================
# EvolutionEngine — 階層的 GA
# =============================================================================


class EvolutionEngine:
    """遺伝的アルゴリズムによる進化エンジン

    Scale ごとに変異率が異なる階層的 GA:
    - Micro: 高変異率 (派生重み) — L2
    - Meso:  中変異率 (マクロ構成) — L3
    - Macro: 低変異率 (WF 構造) — L4

    FEP との対応:
    - 変異 = Explore (Function 公理)
    - 選択 = Exploit (Function 公理)
    - スケール別変異率 = 精度加重 (Precision 公理)
    """

    def __init__(
        self,
        scale: Scale = Scale.MICRO,
        fitness_fn: Optional[Callable[[Chromosome, List[FeedbackEntry]], float]] = None,
    ) -> None:
        self.scale = scale
        self.mutation_rate = SCALE_MUTATION_RATES[scale]
        self.mutation_sigma = SCALE_MUTATION_SIGMA[scale]
        self._fitness_fn = fitness_fn or self._default_fitness

    # -------------------------------------------------------------------------
    # Population
    # -------------------------------------------------------------------------

    def create_population(
        self,
        gene_keys: List[str],
        pop_size: int = 20,
        init_range: tuple[float, float] = (0.5, 1.5),
    ) -> List[Chromosome[Dict[str, float]]]:
        """初期個体群を生成 (dict[str, float] 型の遺伝子)"""
        population = []
        for _ in range(pop_size):
            genes = {
                key: random.uniform(init_range[0], init_range[1])
                for key in gene_keys
            }
            population.append(Chromosome(genes=genes))
        return population

    # -------------------------------------------------------------------------
    # Fitness evaluation
    # -------------------------------------------------------------------------

    def evaluate(
        self,
        chromosome: Chromosome[Dict[str, float]],
        feedback: List[FeedbackEntry],
    ) -> float:
        """個体の適合度を評価し、FitnessVector に記録"""
        score = self._fitness_fn(chromosome, feedback)
        chromosome.fitness = FitnessVector(precision=score)
        return score

    @staticmethod
    def _default_fitness(
        chromosome: Chromosome[Dict[str, float]],
        feedback: List[FeedbackEntry],
    ) -> float:
        """デフォルト適合度: 重みベクトルでの選択が正解と一致する率

        フィードバックの各エントリに対し:
        - was_correct (修正なし) → 選択した派生の重みが最大なら +1
        - not was_correct → 修正先の派生の重みが最大なら +1

        NOTE: gene keys は "O1:nous" 形式、feedback.selected は "nous" 形式。
        比較時に prefix を strip する。
        """
        if not feedback:
            return 0.0

        correct = 0
        total = 0

        for entry in feedback:
            # 正解の派生を決定
            target = entry.selected if entry.was_correct else entry.corrected_to
            if target is None:
                continue

            # この定理の遺伝子だけ抽出
            prefix = f"{entry.theorem}:"
            relevant = {k: v for k, v in chromosome.genes.items()
                        if k.startswith(prefix)}
            if not relevant:
                continue

            # 重みが最大の gene key を選び、prefix を strip して比較
            predicted_key = max(relevant, key=lambda k: relevant[k])
            predicted = predicted_key.split(":", 1)[1] if ":" in predicted_key else predicted_key
            if predicted == target:
                correct += 1
            total += 1

        return correct / total if total > 0 else 0.0

    def evaluate_population(
        self,
        population: List[Chromosome[Dict[str, float]]],
        feedback: List[FeedbackEntry],
    ) -> None:
        """個体群全体の適合度を評価"""
        for chromosome in population:
            self.evaluate(chromosome, feedback)

    # -------------------------------------------------------------------------
    # Selection
    # -------------------------------------------------------------------------

    def tournament_select(
        self,
        population: List[Chromosome[Dict[str, float]]],
        k: int = 3,
    ) -> Chromosome[Dict[str, float]]:
        """トーナメント選択 — k 個体からベストを選ぶ"""
        if len(population) <= k:
            candidates = list(population)
        else:
            candidates = random.sample(population, k)

        return max(candidates, key=lambda c: c.fitness.scalar())

    # -------------------------------------------------------------------------
    # Crossover
    # -------------------------------------------------------------------------

    def crossover(
        self,
        parent1: Chromosome[Dict[str, float]],
        parent2: Chromosome[Dict[str, float]],
        alpha: float = 0.5,
    ) -> Chromosome[Dict[str, float]]:
        """BLX-α 交叉 — 2 親の加重平均で子を生成"""
        child_genes: Dict[str, float] = {}
        all_keys = set(parent1.genes) | set(parent2.genes)

        for key in all_keys:
            v1 = parent1.genes.get(key, 1.0)
            v2 = parent2.genes.get(key, 1.0)
            # BLX-α: 範囲を少し広げた区間からランダムサンプリング
            lo = min(v1, v2)
            hi = max(v1, v2)
            span = hi - lo
            child_genes[key] = random.uniform(
                max(0.0, lo - alpha * span),
                min(2.0, hi + alpha * span),
            )

        return Chromosome(
            genes=child_genes,
            generation=max(parent1.generation, parent2.generation) + 1,
        )

    # -------------------------------------------------------------------------
    # Mutation
    # -------------------------------------------------------------------------

    def mutate(
        self,
        chromosome: Chromosome[Dict[str, float]],
    ) -> Chromosome[Dict[str, float]]:
        """Gaussian 突然変異 — スケール依存の変異率と変異幅"""
        mutated = copy.deepcopy(chromosome)

        for key in mutated.genes:
            if random.random() < self.mutation_rate:
                delta = random.gauss(0, self.mutation_sigma)
                mutated.genes[key] = max(0.0, min(2.0, mutated.genes[key] + delta))

        return mutated

    # -------------------------------------------------------------------------
    # Evolution loop
    # -------------------------------------------------------------------------

    def evolve(
        self,
        population: List[Chromosome[Dict[str, float]]],
        feedback: List[FeedbackEntry],
        generations: int = 50,
        elitism: int = 2,
    ) -> List[Chromosome[Dict[str, float]]]:
        """世代進化ループ

        Args:
            population: 初期個体群
            feedback: フィードバックデータ
            generations: 世代数
            elitism: エリート保存数

        Returns:
            最終世代の個体群 (適合度順ソート済み)
        """
        pop = list(population)
        pop_size = len(pop)

        for gen in range(generations):
            # 適合度評価
            self.evaluate_population(pop, feedback)

            # ソート (適合度降順)
            pop.sort(key=lambda c: c.fitness.scalar(), reverse=True)

            # エリート保存
            next_gen = pop[:elitism]

            # 残りを交叉 + 突然変異で生成
            while len(next_gen) < pop_size:
                p1 = self.tournament_select(pop)
                p2 = self.tournament_select(pop)
                child = self.crossover(p1, p2)
                child = self.mutate(child)
                child.generation = gen + 1
                next_gen.append(child)

            pop = next_gen

        # 最終評価
        self.evaluate_population(pop, feedback)
        pop.sort(key=lambda c: c.fitness.scalar(), reverse=True)

        return pop

    def best(
        self, population: List[Chromosome[Dict[str, float]]]
    ) -> Chromosome[Dict[str, float]]:
        """個体群から最良個体を返す"""
        return max(population, key=lambda c: c.fitness.scalar())

    # -------------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------------

    @staticmethod
    def save_weights(
        chromosome: Chromosome[Dict[str, float]],
        path: Path,
    ) -> None:
        """最良個体の重みを JSON に永続化"""
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "generation": chromosome.generation,
            "fitness": {
                "depth": chromosome.fitness.depth,
                "precision": chromosome.fitness.precision,
                "efficiency": chromosome.fitness.efficiency,
                "novelty": chromosome.fitness.novelty,
                "scalar": chromosome.fitness.scalar(),
            },
            "weights": chromosome.genes,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load_weights(path: Path) -> Optional[Chromosome[Dict[str, float]]]:
        """永続化された重みを読み込み"""
        if not path.exists():
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            fitness_data = data.get("fitness", {})
            return Chromosome(
                genes=data["weights"],
                fitness=FitnessVector(
                    depth=fitness_data.get("depth", 0.0),
                    precision=fitness_data.get("precision", 0.0),
                    efficiency=fitness_data.get("efficiency", 0.0),
                    novelty=fitness_data.get("novelty", 0.0),
                ),
                generation=data.get("generation", 0),
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to load weights: {e}")
            return None

    # -------------------------------------------------------------------------
    # Suggest
    # -------------------------------------------------------------------------

    def suggest_weights(
        self,
        theorem: str,
        weights_dir: Optional[Path] = None,
    ) -> Optional[Dict[str, float]]:
        """定理に対する進化済み重みを提案

        weights/<theorem>.json から読み込む
        """
        base = weights_dir or Path("data/weights")
        path = base / f"{theorem}.json"
        chromosome = self.load_weights(path)
        if chromosome is None:
            return None
        return chromosome.genes
