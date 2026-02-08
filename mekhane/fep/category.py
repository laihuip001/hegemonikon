# PROOF: [L2/インフラ] <- mekhane/fep/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 → 圏 Cog の構造を Python 型で表現する必要がある
   → WF の圏論的基盤（随伴・モナド・米田）を計算可能にする
   → category.py が担う

Q.E.D.

---

Category Theory Types for Hegemonikón

Provides Python dataclass representations for:
- Cog category: 24 objects (theorems), 78 morphisms (72 X-series + 6 identity)
- Adjunction: L ⊣ R (/boot ⊣ /bye)
- Monad: T, η, μ (/zet)
- Cone: @converge C1-C3 (Hub Peras)

References:
- ccl/operators.md §13 (圏論的意味論マップ)
- .agent/workflows/*.md (categorical frontmatter)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, FrozenSet, List, Optional, Tuple


# =============================================================================
# Series (6 layers of Cog category)
# =============================================================================


class Series(Enum):
    """The 6 series of Hegemonikón, each containing 4 theorems."""

    O = "Ousia"  # Pure cognition
    S = "Schema"  # Strategic design
    H = "Hormē"  # Motivation
    P = "Perigraphē"  # Environmental configuration
    K = "Kairos"  # Context
    A = "Akribeia"  # Accuracy assurance


# =============================================================================
# Theorem (Object in Cog)
# =============================================================================


@dataclass(frozen=True)
class Theorem:
    """An object in the category Cog.

    Each theorem is one of 24 cognitive faculties.
    By the Yoneda lemma, a theorem is fully determined by
    its hom-set: Hom(-, T) ≅ F(T).
    """

    id: str  # e.g. "O1", "S2", "K4"
    name: str  # e.g. "Noēsis", "Mekhanē", "Sophia"
    series: Series
    greek: str  # Original Greek name
    generation: Tuple[str, str]  # Cognitive algebra axes

    @property
    def series_index(self) -> int:
        """Position within series (1-4)."""
        return int(self.id[1])


# =============================================================================
# Morphism (Arrow in Cog = X-series relation)
# =============================================================================


@dataclass(frozen=True)
class Morphism:
    """An arrow in the category Cog.

    X-series relations between theorems.
    72 named morphisms + 6 identity morphisms (one per series).
    """

    id: str  # e.g. "X-OS1", "X-HA1"
    source: str  # Source theorem id, e.g. "O1"
    target: str  # Target theorem id, e.g. "S1"
    strength: float = 1.0  # Morphism weight (0.0-1.0)

    @property
    def is_identity(self) -> bool:
        """Whether this is an identity morphism."""
        return self.source == self.target

    def compose(self, other: Morphism) -> Optional[Morphism]:
        """Compose two morphisms g ∘ f (self = f, other = g).

        Returns None if morphisms are not composable.
        """
        if self.target != other.source:
            return None
        return Morphism(
            id=f"{self.id}∘{other.id}",
            source=self.source,
            target=other.target,
            strength=self.strength * other.strength,
        )


# =============================================================================
# Cone (@converge structure)
# =============================================================================


@dataclass
class ConeProjection:
    """A single projection from the apex to a diagram object.

    In @converge, each projection is Hom(X, Tn) — the morphism
    from the apex (integrated judgment) to one theorem's output.
    """

    theorem_id: str  # Which theorem this projects to
    output: str  # The theorem's output (1-line summary)
    hom_label: str  # e.g. "認識の射", "意志の射"


@dataclass
class Cone:
    """A cone over a diagram in Cog.

    @converge constructs a Cone over the 4-theorem diagram.
    C1 = enumerate projections
    C2 = find mediating morphism (apex)
    C3 = verify universality

    The Limit is the universal Cone — every other Cone
    factors through it uniquely.
    """

    series: Series
    projections: List[ConeProjection]  # C1: the 4 projections
    dispersion: float = 0.0  # V[outputs]: 0.0-1.0
    apex: str = ""  # C2 result: the integrated judgment
    resolution_method: str = ""  # root / weighted / simple
    confidence: float = 0.0  # C3: universality strength (0-100)
    is_universal: bool = False  # Whether this is the Limit

    @property
    def is_consistent(self) -> bool:
        """V[outputs] ≤ 0.1 means projections are nearly consistent."""
        return self.dispersion <= 0.1

    @property
    def needs_devil(self) -> bool:
        """V[outputs] > 0.3 means serious contradiction."""
        return self.dispersion > 0.3


# =============================================================================
# Adjunction (/boot ⊣ /bye)
# =============================================================================


@dataclass
class Adjunction:
    """An adjunction L ⊣ R between two categories.

    In Hegemonikón:
    - L (left adjoint) = /boot: Mem → Ses (expand memory to session)
    - R (right adjoint) = /bye: Ses → Mem (compress session to memory)
    - η (unit): Id_Mem → R∘L (boot→bye preservation rate)
    - ε (counit): L∘R → Id_Ses (bye→boot restoration rate)
    - Drift = 1 - ε (lost context)
    """

    left_name: str = "boot"  # L: free functor
    right_name: str = "bye"  # R: forgetful functor
    source_category: str = "Mem"  # Memory category
    target_category: str = "Ses"  # Session category
    eta_quality: float = 0.0  # η: preservation rate (0-1)
    epsilon_precision: float = 0.0  # ε: restoration rate (0-1)

    @property
    def drift(self) -> float:
        """Context lost in the boot→bye→boot cycle.

        Drift = 1 - ε. If ε = 1, perfect restoration.
        """
        return 1.0 - self.epsilon_precision

    @property
    def is_faithful(self) -> bool:
        """R is faithful if η quality > 0.8."""
        return self.eta_quality > 0.8


# =============================================================================
# Monad (/zet)
# =============================================================================


@dataclass
class Monad:
    """A monad T: Cog → Cog.

    In Hegemonikón:
    - T = question generation endofunctor
    - η (unit): X → T(X) — concept generates questions (Phase 1)
    - μ (join): T(T(X)) → T(X) — flatten meta-questions (Phase 2)
    - Kleisli: anom >=> hypo >=> eval — derivative chaining

    Monad laws:
    - Left unit: μ ∘ ηT = id (generate then flatten = identity)
    - Right unit: μ ∘ Tη = id (meta then flatten = identity)
    - Associativity: μ ∘ μT = μ ∘ Tμ (flatten order doesn't matter)
    """

    name: str = "Zētēsis"
    functor_name: str = "T"  # T: Cog → Cog

    # Phase 1 output: T(X)
    raw_questions: List[str] = field(default_factory=list)

    # Phase 2 output: μ(T(T(X))) = T(X) flattened
    filtered_questions: List[str] = field(default_factory=list)

    # Kleisli chain record
    kleisli_chain: List[str] = field(default_factory=list)

    def unit(self, concept: str) -> List[str]:
        """η: X → T(X) — generate questions from a concept.

        This is the abstract interface. Actual question generation
        is done by the LLM via /zet Phase 1.
        """
        # Placeholder: actual implementation would call LLM
        return [f"Why does {concept} work this way?"]

    def join(self, meta_questions: List[List[str]]) -> List[str]:
        """μ: T(T(X)) → T(X) — flatten questions-of-questions.

        Removes meta-questions and produces concrete questions.
        """
        return [q for qs in meta_questions for q in qs]


# =============================================================================
# Cog Category (the whole thing)
# =============================================================================


# All 24 theorems
THEOREMS: Dict[str, Theorem] = {
    # O-series (Ousia)
    "O1": Theorem("O1", "Noēsis", Series.O, "Νόησις", ("I", "E")),
    "O2": Theorem("O2", "Boulēsis", Series.O, "Βούλησις", ("I", "P")),
    "O3": Theorem("O3", "Zētēsis", Series.O, "Ζήτησις", ("A", "E")),
    "O4": Theorem("O4", "Energeia", Series.O, "Ἐνέργεια", ("A", "P")),
    # S-series (Schema)
    "S1": Theorem("S1", "Metron", Series.S, "Μέτρον", ("Flow", "Scale")),
    "S2": Theorem("S2", "Mekhanē", Series.S, "Μηχανή", ("Flow", "Function")),
    "S3": Theorem("S3", "Stathmos", Series.S, "Σταθμός", ("Value", "Scale")),
    "S4": Theorem("S4", "Praxis", Series.S, "Πρᾶξις", ("Value", "Function")),
    # H-series (Hormē)
    "H1": Theorem("H1", "Propatheia", Series.H, "Προπάθεια", ("Flow", "Valence")),
    "H2": Theorem("H2", "Pistis", Series.H, "Πίστις", ("Flow", "Precision")),
    "H3": Theorem("H3", "Orexis", Series.H, "Ὄρεξις", ("Value", "Valence")),
    "H4": Theorem("H4", "Doxa", Series.H, "Δόξα", ("Value", "Precision")),
    # P-series (Perigraphē)
    "P1": Theorem("P1", "Khōra", Series.P, "Χώρα", ("Scale", "Scale")),
    "P2": Theorem("P2", "Hodos", Series.P, "Ὁδός", ("Scale", "Function")),
    "P3": Theorem("P3", "Trokhia", Series.P, "Τροχιά", ("Function", "Scale")),
    "P4": Theorem("P4", "Tekhnē", Series.P, "Τέχνη", ("Function", "Function")),
    # K-series (Kairos)
    "K1": Theorem("K1", "Eukairia", Series.K, "Εὐκαιρία", ("Scale", "Valence")),
    "K2": Theorem("K2", "Chronos", Series.K, "Χρόνος", ("Scale", "Precision")),
    "K3": Theorem("K3", "Telos", Series.K, "Τέλος", ("Function", "Valence")),
    "K4": Theorem("K4", "Sophia", Series.K, "Σοφία", ("Function", "Precision")),
    # A-series (Akribeia)
    "A1": Theorem("A1", "Pathos", Series.A, "Πάθος", ("Valence", "Valence")),
    "A2": Theorem("A2", "Krisis", Series.A, "Κρίσις", ("Valence", "Precision")),
    "A3": Theorem("A3", "Gnōmē", Series.A, "Γνώμη", ("Precision", "Valence")),
    "A4": Theorem("A4", "Epistēmē", Series.A, "Ἐπιστήμη", ("Precision", "Precision")),
}


def hom_set(target: str) -> FrozenSet[str]:
    """Compute Hom(-, T) — all morphisms targeting theorem T.

    By the Yoneda lemma, this set completely determines T.
    This is a simplified version that returns X-series morphism IDs.
    """
    # In practice, this would query the X-series registry.
    # For now, return the set of theorems that have morphisms to target.
    series_order = ["O", "S", "H", "P", "K", "A"]
    target_series = target[0]
    target_idx = series_order.index(target_series)

    sources: set[str] = set()
    if target_idx > 0:
        prev_series = series_order[target_idx - 1]
        for i in range(1, 5):
            sources.add(f"{prev_series}{i}")

    return frozenset(sources)


def build_cone(series: Series, outputs: Dict[str, str]) -> Cone:
    """Build a Cone from theorem outputs.

    This is the @converge C1 step: enumerate projections.

    Args:
        series: Which series to build the cone for
        outputs: Dict mapping theorem_id -> output string

    Returns:
        Cone with projections populated
    """
    series_prefix = series.name[0]
    hom_labels = {
        Series.O: ["認識の射", "意志の射", "探求の射", "行動の射"],
        Series.S: ["スケールの射", "手法の射", "基準の射", "実践の射"],
        Series.H: ["傾向の射", "確信の射", "欲求の射", "信念の射"],
        Series.P: ["空間の射", "経路の射", "軌道の射", "技術の射"],
        Series.K: ["好機の射", "時間の射", "目的の射", "知恵の射"],
        Series.A: ["感情の射", "判断の射", "見識の射", "知識の射"],
    }

    projections = []
    for i in range(1, 5):
        tid = f"{series_prefix}{i}"
        projections.append(
            ConeProjection(
                theorem_id=tid,
                output=outputs.get(tid, ""),
                hom_label=hom_labels[series][i - 1],
            )
        )

    return Cone(series=series, projections=projections)
