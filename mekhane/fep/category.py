# PROOF: [L2/インフラ] <- mekhane/fep/
"""
PROOF: [L2/インフラ] このファイルは存在しなければならない

A0 → 圏 Cog の構造を Python 型で表現する必要がある
   → WF の圏論的基盤（随伴・モナド・米田）を計算可能にする
   → category.py が担う

Q.E.D.

---

Category Theory Types for Hegemonikón

Type Layer Classification (Q16: /zet+ 2026-02-08):

    Layer A — Scaffold (思考足場)
        Monad, Functor, NaturalTransformation
        品質基準: docstring が正確であること
        消費者: Creator の認知 (コードで消費されなくてよい)
        乖離: 乖離＝正常。消費者ゼロでも正当
        判定: この型を削除してもコードは壊れない → Scaffold

    Layer B — Constraint (設計制約)
        Series, CognitiveType, Theorem
        品質基準: 型チェックが通り、消費者 ≥ 1
        消費者: cone_builder, attractor, pw_adapter
        乖離: 乖離＝中程度の問題。消費者を要求する
        判定: 削除するとコードは動くが型安全が失われる → Constraint

    Layer C — Operational (実装消費)
        Cone, ConeProjection, Morphism, Adjunction
        品質基準: テスト PASS + 実行時検証 + 消費者コード必須
        消費者: cone_builder, boot_integration, postcheck
        乖離: 乖離＝バグ。即修正
        判定: 削除するとコードが壊れる → Operational

Role of Category Theory (Q7: /zet+ 2026-02-08):

    圏論は「設計言語」でも「思考足場」でも「反射板」でもない。
    圏論は Hegemonikón の **感覚器 (sensory organ)** である。

    FEP の perception-action loop と同型:
        Perception — 圏論でコードを「見る」(「これは Cone だ」)
        Action     — 見えた構造に基づいてコードを書く (cone_builder)
        Prediction — 理論が「次はこうあるべき」と予測する
        Error      — 実装が予測とズレる → dirty adapter が生まれる

    目を閉じれば手は盲目になる (理論なき実装)。
    手を縛れば目は無意味になる (実装なき理論)。
    設計と理論は密に連動し、相補的に循環する。

Provides Python dataclass representations for:
- Cog category: 24 objects (theorems), 72 morphisms (X-series)
- Cone: @converge C0-C3 with Precision Weighting (Hub Peras)
- Adjunction: L ⊣ R (/boot ⊣ /bye)
- Monad: T, η, μ (/zet)
- Functor: F: C → D (e.g. /eat: Ext→Cog, /zet: Cog→Cog)
- NaturalTransformation: α: F ⇒ G (e.g. η, ε, WF version upgrade)
- EpsilonMixture: M = (1-ε)×structure + ε×uniform (ε-Architecture)

References:
- ccl/operators.md §13 (圏論的意味論マップ)
- .agent/workflows/*.md (categorical frontmatter)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, FrozenSet, List, Optional, Tuple


# =============================================================================
# Series (6 layers of Cog category)                          [Layer B: Constraint]
# =============================================================================


# PURPOSE: The 6 series of Hegemonikón, each containing 4 theorems
class Series(Enum):
    """The 6 series of Hegemonikón, each containing 4 theorems."""

    O = "Ousia"  # Pure cognition
    S = "Schema"  # Strategic design
    H = "Hormē"  # Motivation
    P = "Perigraphē"  # Environmental configuration
    K = "Kairos"  # Context
    A = "Akribeia"  # Accuracy assurance


# =============================================================================
# Enrichment (Typed Enrichment — Hom-set structure)          [Layer B: Constraint]
# =============================================================================


# PURPOSE: The type of enrichment for each series' Hom-set
class EnrichmentType(Enum):
    """Typed Enrichment — what structure the Hom-set carries.

    Discovered via /noe+ bottom-up analysis (2026-02-10).
    Each series enriches its Hom-set with a distinct mathematical structure.
    """

    END = "End"       # /o: Hom(O,O) self-endomorphisms (V→PW feedback, meta, /o*)
    MET = "Met"       # /s: Hom as metric space (tension = distance between theorems)
    PROB = "Prob"     # /h: Hom as probability (valence bias via entropy)
    SET = "Set"       # /p: Hom in Set (no enrichment — "container" series)
    TEMP = "Temp"     # /k: Hom with temporal weights (urgency, Eisenhower)
    FUZZY = "Fuzzy"   # /a: Hom in [0,1] (precision weighting, confidence grading)


# PURPOSE: Enrichment metadata for a series
@dataclass(frozen=True)
class Enrichment:
    """Enrichment metadata for a series.

    Describes what mathematical structure the Hom-set carries.
    Discovered via bottom-up /noe+ analysis, not top-down imposition.
    """

    type: EnrichmentType
    concept: str                    # One-line description
    kalon: Optional[float] = None   # Kalon score (None for Set = no enrichment)
    structures: Tuple[str, ...] = ()  # Evidence / structural basis


# PURPOSE: Map each series to its Typed Enrichment
SERIES_ENRICHMENTS: Dict[Series, Enrichment] = {
    Series.O: Enrichment(
        type=EnrichmentType.END,
        concept="V→PW feedback + meta cognition + /o* self-reference",
        kalon=0.75,
        structures=(
            "V[] > 0.5 → O3+: Cone internal state feeds back to PW",
            "O1.meta = cognition of cognition (endomorphism)",
            "/o* = cognition layer questioning itself",
        ),
    ),
    Series.S: Enrichment(
        type=EnrichmentType.MET,
        concept="6-pair tension as distance + Devil's Advocate",
        kalon=0.75,
        structures=(
            "S-series computes pairwise tension (metric) between 4 theorems",
            "V > 0.1 triggers Devil's Advocate (distance-based escalation)",
        ),
    ),
    Series.H: Enrichment(
        type=EnrichmentType.PROB,
        concept="V[/h] bias detection via entropy",
        kalon=0.85,
        structures=(
            "H-series bias mode detects valence skew (probability distribution)",
            "Entropy-based divergence measures motivational balance",
        ),
    ),
    Series.P: Enrichment(
        type=EnrichmentType.SET,
        concept="Container series — Hom in Set, no enrichment needed",
        kalon=None,
        structures=(
            "/p defines the stage where other WFs execute",
            "3 hypotheses tested and rejected: Top, Op, Presheaf",
        ),
    ),
    Series.K: Enrichment(
        type=EnrichmentType.TEMP,
        concept="Urgency weights + Eisenhower matrix + Q2 protection",
        kalon=0.85,
        structures=(
            "K-series pri mode applies temporal urgency weighting",
            "Eisenhower 2x2 prioritizes importance over urgency",
            "Q2 protection: important-not-urgent tasks get elevated weight",
        ),
    ),
    Series.A: Enrichment(
        type=EnrichmentType.FUZZY,
        concept="PW self-reference + confidence grading [0,1]",
        kalon=0.80,
        structures=(
            "A4 Epistēmē grades confidence: tentative/justified/certain",
            "A2 Krisis: binary PASS/FAIL judgment",
            "PW is both tool and research subject in A-series",
        ),
    ),
}


# PURPOSE: Understanding vs Reasoning classification for each theorem
class CognitiveType(Enum):
    """Understanding vs Reasoning classification for each theorem.

    Based on: Wang & Zhao (2023) "Metacognitive Prompting"
    - Understanding: grasping underlying semantics and broader contextual meanings
    - Reasoning: methodically connecting concepts
    - Bridge: transitions between U and R

    Mapping: O-series/H-series/K-series ≈ Understanding
             S-series/P-series ≈ Reasoning
             A-series = Bridge layer (A1: U→R, A3: R→U, A2/A4: Reasoning)
    """

    UNDERSTANDING = "understanding"  # 基底意味論の把握 (O/H/K)
    REASONING = "reasoning"          # 方法的概念接続 (S/P/A2/A4)
    BRIDGE_U_TO_R = "bridge_u_to_r"  # Understanding → Reasoning (A1 Pathos)
    BRIDGE_R_TO_U = "bridge_r_to_u"  # Reasoning → Understanding (A3 Gnōmē)
    MIXED = "mixed"                  # Both (K4 Sophia)


# =============================================================================
# Theorem (Object in Cog)                                    [Layer B: Constraint]
# =============================================================================


# PURPOSE: An object in the category Cog
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

    # PURPOSE: Position within series (1-4)
    @property
    def series_index(self) -> int:
        """Position within series (1-4)."""
        return int(self.id[1])


# =============================================================================
# Morphism (Arrow in Cog = X-series relation)               [Layer C: Operational]
# =============================================================================


# PURPOSE: An arrow in the category Cog
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

    # PURPOSE: Whether this is an identity morphism
    @property
    def is_identity(self) -> bool:
        """Whether this is an identity morphism."""
        return self.source == self.target

    # PURPOSE: Compose two morphisms g ∘ f (self = f, other = g)
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
# Cone (@converge structure)                                [Layer C: Operational]
# =============================================================================


# PURPOSE: A single projection from the apex to a diagram object
@dataclass
class ConeProjection:
    """A single projection from the apex to a diagram object.

    In @converge, each projection is Hom(X, Tn) — the morphism
    from the apex (integrated judgment) to one theorem's output.
    """

    theorem_id: str  # Which theorem this projects to
    output: str  # The theorem's output (1-line summary)
    hom_label: str  # e.g. "認識の射", "意志の射"


# PURPOSE: A cone over a diagram in Cog
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
    pw: Dict[str, float] = field(default_factory=dict)  # C0: Precision Weighting [-1, +1]
    enrichment: Optional[Enrichment] = None  # Typed Enrichment for this series

    # PURPOSE: V[outputs] ≤ 0.1 means projections are nearly consistent
    @property
    def is_consistent(self) -> bool:
        """V[outputs] ≤ 0.1 means projections are nearly consistent."""
        return self.dispersion <= 0.1

    # PURPOSE: V[outputs] > 0.3 means serious contradiction
    @property
    def needs_devil(self) -> bool:
        """V[outputs] > 0.3 means serious contradiction."""
        return self.dispersion > 0.3


# =============================================================================
# Adjunction (/boot ⊣ /bye)                                [Layer C: Operational]
# =============================================================================


# PURPOSE: An adjunction L ⊣ R between two categories
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

    # PURPOSE: Context lost in the boot→bye→boot cycle
    @property
    def drift(self) -> float:
        """Context lost in the boot→bye→boot cycle.

        Drift = 1 - ε. If ε = 1, perfect restoration.
        """
        return 1.0 - self.epsilon_precision

    # PURPOSE: R is faithful if η quality > 0.8
    @property
    def is_faithful(self) -> bool:
        """R is faithful if η quality > 0.8."""
        return self.eta_quality > 0.8


# =============================================================================
# EpsilonMixture (ε-Architecture)                            [Layer B: Constraint]
# =============================================================================


# PURPOSE: Convex combination M = (1-ε)×structure + ε×uniform
@dataclass
class EpsilonMixture:
    """Convex combination in the simplex of distributions.

    M = (1-ε) × structure + ε × uniform

    Category-theoretic interpretation:
    - Structure functor S: State → Dist (domain knowledge → distribution)
    - Uniform functor U: State → Dist (constant uniform distribution)
    - α_ε: S ⇒ U is a parametric natural transformation
    - ε ∈ [0.01, 0.50] indexes the transformation family

    Meta-ε learning makes ε itself a learned parameter:
    - Learning functor L: (ε, error) → ε' via EMA
    - L is a contraction mapping: ||L(ε₁) - L(ε₂)|| ≤ α||ε₁ - ε₂||
    - Fixed point ε* = argmin F(ε) where F is variational free energy

    The 4 ε parameters form a product object (independent tuple):
    ε = (ε_A, ε_B_obs, ε_B_act, ε_D)
    Each component governs one matrix of the generative model ABCD independently.
    """

    name: str  # e.g. "A", "B_observe", "B_act", "D"
    epsilon: float  # Current ε value
    eps_min: float = 0.01
    eps_max: float = 0.50
    description: str = ""

    # PURPOSE: ε within valid bounds
    @property
    def is_valid(self) -> bool:
        """ε within valid bounds."""
        return self.eps_min <= self.epsilon <= self.eps_max

    # PURPOSE: How much we trust domain structure vs uniform
    @property
    def structure_trust(self) -> float:
        """How much we trust domain structure (1-ε)."""
        return 1.0 - self.epsilon

    # PURPOSE: Apply the mixture law
    def apply(self, structure_val: float, uniform_val: float) -> float:
        """Apply M = (1-ε) × structure + ε × uniform."""
        return (1.0 - self.epsilon) * structure_val + self.epsilon * uniform_val


# The 4 ε parameters of the generative model
EPSILON_REGISTRY: Dict[str, EpsilonMixture] = {
    "A": EpsilonMixture(
        name="A",
        epsilon=0.25,
        description="Observation likelihood: categorical mapping + noise",
    ),
    "B_observe": EpsilonMixture(
        name="B_observe",
        epsilon=0.10,
        description="State persistence under observation",
    ),
    "B_act": EpsilonMixture(
        name="B_act",
        epsilon=0.15,
        description="Transition noise under action",
    ),
    "D": EpsilonMixture(
        name="D",
        epsilon=0.15,
        description="Prior uncertainty (Stoic prior + uniform)",
    ),
}


# =============================================================================
# Monad (/zet)                                               [Layer A: Scaffold]
# =============================================================================


# PURPOSE: A monad T: Cog → Cog
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

    # PURPOSE: η: X → T(X) — generate questions from a concept
    def unit(self, concept: str) -> List[str]:
        """η: X → T(X) — generate questions from a concept.

        This is the abstract interface. Actual question generation
        is done by the LLM via /zet Phase 1.
        """
        # Placeholder: actual implementation would call LLM
        return [f"Why does {concept} work this way?"]

    # PURPOSE: μ: T(T(X)) → T(X) — flatten questions-of-questions
    def join(self, meta_questions: List[List[str]]) -> List[str]:
        """μ: T(T(X)) → T(X) — flatten questions-of-questions.

        Removes meta-questions and produces concrete questions.
        """
        return [q for qs in meta_questions for q in qs]


# =============================================================================
# Functor (映射: Category → Category)                        [Layer A: Scaffold]
# =============================================================================


# PURPOSE: A functor F: C → D between categories
@dataclass
class Functor:
    """A functor F: C → D between categories.

    In Hegemonikón:
    - /eat: Ext → Cog (digest external content into theorems)
    - /zet: Cog → Cog (endofunctor: question generation)
    - L (/boot): Mem → Ses (left adjoint: expand)
    - R (/bye): Ses → Mem (right adjoint: compress)

    A functor maps:
    - Objects to objects: F(X) = Y
    - Morphisms to morphisms: F(f: X→Y) = F(f): F(X)→F(Y)
    Preserving composition and identity.
    """

    name: str  # e.g. "eat", "zet", "boot", "bye"
    source_cat: str  # Source category name, e.g. "Ext", "Cog", "Mem"
    target_cat: str  # Target category name, e.g. "Cog", "Ses"
    object_map: Dict[str, str] = field(default_factory=dict)  # X → F(X)
    morphism_map: Dict[str, str] = field(default_factory=dict)  # f → F(f)
    is_endofunctor: bool = False  # C == D

    # PURPOSE: Faithful = injective on morphisms (no information loss)
    @property
    def is_faithful(self) -> bool:
        """Faithful = injective on morphisms (no information loss)."""
        values = list(self.morphism_map.values())
        return len(values) == len(set(values))

    # PURPOSE: Full = surjective on morphisms (covers all arrows in target)
    @property
    def is_full(self) -> bool:
        """Full = surjective on morphisms (covers all arrows in target).

        Raises NotImplementedError: cannot compute without full category
        knowledge (all morphisms in target category).
        """
        raise NotImplementedError(
            "is_full requires full category knowledge (all target morphisms)"
        )

    # PURPOSE: Apply functor to an object
    def map_object(self, obj: str) -> Optional[str]:
        """Apply functor to an object."""
        return self.object_map.get(obj)

    # PURPOSE: Apply functor to a morphism
    def map_morphism(self, morphism_id: str) -> Optional[str]:
        """Apply functor to a morphism."""
        return self.morphism_map.get(morphism_id)

    # PURPOSE: Functor composition: G∘F (self=F, other=G)
    def compose(self, other: Functor) -> Functor:
        """Functor composition: G∘F (self=F, other=G).

        F: A→B, G: B→C  →  G∘F: A→C

        Object map: X ↦ G(F(X))
        Morphism map: f ↦ G(F(f))

        Raises:
            ValueError: if F.target_cat != G.source_cat (incompatible)
        """
        if self.target_cat != other.source_cat:
            raise ValueError(
                f"Cannot compose {other.name}∘{self.name}: "
                f"{self.name} target ({self.target_cat}) "
                f"≠ {other.name} source ({other.source_cat})"
            )

        # G∘F object map: X ↦ G(F(X))
        composed_obj = {}
        for x, fx in self.object_map.items():
            gfx = other.object_map.get(fx)
            if gfx is not None:
                composed_obj[x] = gfx

        # G∘F morphism map: f ↦ G(F(f))
        composed_mor = {}
        for f, ff in self.morphism_map.items():
            gff = other.morphism_map.get(ff)
            if gff is not None:
                composed_mor[f] = gff

        result_source = self.source_cat
        result_target = other.target_cat

        return Functor(
            name=f"{other.name}∘{self.name}",
            source_cat=result_source,
            target_cat=result_target,
            object_map=composed_obj,
            morphism_map=composed_mor,
            is_endofunctor=(result_source == result_target),
        )


# =============================================================================
# Natural Transformation (自然変換: Functor → Functor)       [Layer A: Scaffold]
# =============================================================================


# PURPOSE: A natural transformation α: F ⇒ G between functors
@dataclass
class NaturalTransformation:
    """A natural transformation α: F ⇒ G between functors.

    In Hegemonikón:
    - /eat v1 → /eat v2: WF version upgrade as natural transformation
    - @converge C0→C1: PW selection → shot enumeration as α
    - /boot η: Id_Mem ⇒ R∘L (unit of adjunction)
    - /bye ε: L∘R ⇒ Id_Ses (counit of adjunction)

    Naturality condition:
        G(f) ∘ α_X = α_Y ∘ F(f)
        "transforming then mapping = mapping then transforming"

    This guarantees structural consistency across all objects.
    """

    name: str  # e.g. "η", "ε", "eat_upgrade"
    source_functor: str  # F
    target_functor: str  # G
    components: Dict[str, str] = field(default_factory=dict)  # α_X for each object X

    # PURPOSE: Get the component α_X at object X
    def component_at(self, obj: str) -> Optional[str]:
        """Get the component α_X at object X."""
        return self.components.get(obj)

    # PURPOSE: Vertical composition: β ∘ α (self = α, other = β)
    def compose(self, other: NaturalTransformation, *, strict: bool = False) -> Optional[NaturalTransformation]:
        """Vertical composition: β ∘ α (self = α, other = β).

        α: F ⇒ G, β: G ⇒ H → β∘α: F ⇒ H

        Args:
            strict: if True, raise ValueError when objects mismatch
                    (some objects in α not in β or vice versa).
                    Default False for backward compatibility.
        """
        if self.target_functor != other.source_functor:
            return None

        # Detect object mismatch
        alpha_objs = set(self.components.keys())
        beta_objs = set(other.components.keys())
        missing_in_beta = alpha_objs - beta_objs
        missing_in_alpha = beta_objs - alpha_objs

        if strict and (missing_in_beta or missing_in_alpha):
            raise ValueError(
                f"Object mismatch in composition {other.name}∘{self.name}: "
                f"α has {missing_in_beta or '∅'} not in β, "
                f"β has {missing_in_alpha or '∅'} not in α"
            )

        if missing_in_beta or missing_in_alpha:
            import warnings
            dropped = missing_in_beta | missing_in_alpha
            warnings.warn(
                f"Partial composition {other.name}∘{self.name}: "
                f"objects {dropped} dropped (not in both transformations)",
                stacklevel=2,
            )

        # Component-wise composition (only shared objects)
        composed_components = {}
        for obj in self.components:
            if obj in other.components:
                composed_components[obj] = f"{other.components[obj]}∘{self.components[obj]}"
        return NaturalTransformation(
            name=f"{other.name}∘{self.name}",
            source_functor=self.source_functor,
            target_functor=other.target_functor,
            components=composed_components,
        )

    # PURPOSE: A natural isomorphism has invertible components
    @property
    def is_natural_isomorphism(self) -> bool:
        """A natural isomorphism has invertible components.

        Cannot fully verify without category structure;
        checks that all components are non-empty as proxy.
        """
        return bool(self.components) and all(
            v != "" for v in self.components.values()
        )


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


# =============================================================================
# Cognitive Type Classification (Understanding vs Reasoning)
# Source: MP Natural Transformation (2026-02-08)
# =============================================================================


COGNITIVE_TYPES: Dict[str, CognitiveType] = {
    # O-series: Understanding (本質の把握)
    "O1": CognitiveType.UNDERSTANDING,   # Noēsis — 意味の直観
    "O2": CognitiveType.UNDERSTANDING,   # Boulēsis — 意志の方向性
    "O3": CognitiveType.UNDERSTANDING,   # Zētēsis — 問いの発見
    "O4": CognitiveType.UNDERSTANDING,   # Energeia — 意味の行動化
    # S-series: Reasoning (方法的設計)
    "S1": CognitiveType.REASONING,       # Metron — スケール決定
    "S2": CognitiveType.REASONING,       # Mekhanē — 方法配置
    "S3": CognitiveType.REASONING,       # Stathmos — 基準設定
    "S4": CognitiveType.REASONING,       # Praxis — 実践選択
    # H-series: Understanding (動機の把握)
    "H1": CognitiveType.UNDERSTANDING,   # Propatheia — 直感
    "H2": CognitiveType.UNDERSTANDING,   # Pistis — 確信の深度
    "H3": CognitiveType.UNDERSTANDING,   # Orexis — 欲求の理解
    "H4": CognitiveType.UNDERSTANDING,   # Doxa — 信念の理解
    # P-series: Reasoning (環境の構造化)
    "P1": CognitiveType.REASONING,       # Khōra — 場の設定
    "P2": CognitiveType.REASONING,       # Hodos — 経路設計
    "P3": CognitiveType.REASONING,       # Trokhia — 軌道定義
    "P4": CognitiveType.REASONING,       # Tekhnē — 技法選択
    # K-series: Understanding (文脈の認識)
    "K1": CognitiveType.UNDERSTANDING,   # Eukairia — 好機の認識
    "K2": CognitiveType.REASONING,       # Chronos — 時間配分 (手続き的)
    "K3": CognitiveType.UNDERSTANDING,   # Telos — 目的の理解
    "K4": CognitiveType.MIXED,           # Sophia — 知恵 (U+R)
    # A-series: Bridge layer
    "A1": CognitiveType.BRIDGE_U_TO_R,   # Pathos — 感情→精度 (U→R)
    "A2": CognitiveType.REASONING,       # Krisis — 批判的評価
    "A3": CognitiveType.BRIDGE_R_TO_U,   # Gnōmē — 精度→見識 (R→U)
    "A4": CognitiveType.REASONING,       # Epistēmē — 知識確定
}


# PURPOSE: Compute Hom(-, T) — all morphisms targeting theorem T
def hom_set(target: str) -> FrozenSet[str]:
    """Compute Hom(-, T) — all morphisms targeting theorem T.

    By the Yoneda lemma, this set completely determines T.
    Uses the actual X-series morphism registry.
    """
    return frozenset(
        m.id for m in MORPHISMS.values() if m.target == target
    )


# PURPOSE: Compute source theorems targeting T
def hom_sources(target: str) -> FrozenSet[str]:
    """Compute source theorems targeting T."""
    return frozenset(
        m.source for m in MORPHISMS.values() if m.target == target
    )


# =============================================================================
# X-series Morphism Registry (72 morphisms)
# Source: kernel/taxis.md v3.0
# =============================================================================


def _m(xid: str, src: str, tgt: str) -> Morphism:
    """Shorthand for Morphism creation."""
    return Morphism(id=xid, source=src, target=tgt)


MORPHISMS: Dict[str, Morphism] = {
    # --- X-OS: Ousia → Schema (8) ---
    "X-OS1": _m("X-OS1", "O1", "S1"),  # Noēsis → Metron
    "X-OS2": _m("X-OS2", "O1", "S2"),  # Noēsis → Mekhanē
    "X-OS3": _m("X-OS3", "O2", "S1"),  # Boulēsis → Metron
    "X-OS4": _m("X-OS4", "O2", "S2"),  # Boulēsis → Mekhanē
    "X-OS5": _m("X-OS5", "O3", "S3"),  # Zētēsis → Stathmos
    "X-OS6": _m("X-OS6", "O3", "S4"),  # Zētēsis → Praxis
    "X-OS7": _m("X-OS7", "O4", "S3"),  # Energeia → Stathmos
    "X-OS8": _m("X-OS8", "O4", "S4"),  # Energeia → Praxis
    # --- X-OH: Ousia → Hormē (8) ---
    "X-OH1": _m("X-OH1", "O1", "H1"),  # Noēsis → Propatheia
    "X-OH2": _m("X-OH2", "O1", "H2"),  # Noēsis → Pistis
    "X-OH3": _m("X-OH3", "O2", "H1"),  # Boulēsis → Propatheia
    "X-OH4": _m("X-OH4", "O2", "H2"),  # Boulēsis → Pistis
    "X-OH5": _m("X-OH5", "O3", "H3"),  # Zētēsis → Orexis
    "X-OH6": _m("X-OH6", "O3", "H4"),  # Zētēsis → Doxa
    "X-OH7": _m("X-OH7", "O4", "H3"),  # Energeia → Orexis
    "X-OH8": _m("X-OH8", "O4", "H4"),  # Energeia → Doxa
    # --- X-SH: Schema → Hormē (8) ---
    "X-SH1": _m("X-SH1", "S1", "H1"),  # Metron → Propatheia
    "X-SH2": _m("X-SH2", "S1", "H2"),  # Metron → Pistis
    "X-SH3": _m("X-SH3", "S2", "H1"),  # Mekhanē → Propatheia
    "X-SH4": _m("X-SH4", "S2", "H2"),  # Mekhanē → Pistis
    "X-SH5": _m("X-SH5", "S3", "H3"),  # Stathmos → Orexis
    "X-SH6": _m("X-SH6", "S3", "H4"),  # Stathmos → Doxa
    "X-SH7": _m("X-SH7", "S4", "H3"),  # Praxis → Orexis
    "X-SH8": _m("X-SH8", "S4", "H4"),  # Praxis → Doxa
    # --- X-SP: Schema → Perigraphē (8) ---
    "X-SP1": _m("X-SP1", "S1", "P1"),  # Metron → Khōra
    "X-SP2": _m("X-SP2", "S1", "P2"),  # Metron → Hodos
    "X-SP3": _m("X-SP3", "S3", "P1"),  # Stathmos → Khōra
    "X-SP4": _m("X-SP4", "S3", "P2"),  # Stathmos → Hodos
    "X-SP5": _m("X-SP5", "S2", "P3"),  # Mekhanē → Trokhia
    "X-SP6": _m("X-SP6", "S2", "P4"),  # Mekhanē → Tekhnē
    "X-SP7": _m("X-SP7", "S4", "P3"),  # Praxis → Trokhia
    "X-SP8": _m("X-SP8", "S4", "P4"),  # Praxis → Tekhnē
    # --- X-SK: Schema → Kairos (8) ---
    "X-SK1": _m("X-SK1", "S1", "K1"),  # Metron → Eukairia
    "X-SK2": _m("X-SK2", "S1", "K2"),  # Metron → Chronos
    "X-SK3": _m("X-SK3", "S3", "K1"),  # Stathmos → Eukairia
    "X-SK4": _m("X-SK4", "S3", "K2"),  # Stathmos → Chronos
    "X-SK5": _m("X-SK5", "S2", "K3"),  # Mekhanē → Telos
    "X-SK6": _m("X-SK6", "S2", "K4"),  # Mekhanē → Sophia
    "X-SK7": _m("X-SK7", "S4", "K3"),  # Praxis → Telos
    "X-SK8": _m("X-SK8", "S4", "K4"),  # Praxis → Sophia
    # --- X-PK: Perigraphē → Kairos (8) ---
    "X-PK1": _m("X-PK1", "P1", "K1"),  # Khōra → Eukairia
    "X-PK2": _m("X-PK2", "P1", "K2"),  # Khōra → Chronos
    "X-PK3": _m("X-PK3", "P2", "K1"),  # Hodos → Eukairia
    "X-PK4": _m("X-PK4", "P2", "K2"),  # Hodos → Chronos
    "X-PK5": _m("X-PK5", "P3", "K3"),  # Trokhia → Telos
    "X-PK6": _m("X-PK6", "P3", "K4"),  # Trokhia → Sophia
    "X-PK7": _m("X-PK7", "P4", "K3"),  # Tekhnē → Telos
    "X-PK8": _m("X-PK8", "P4", "K4"),  # Tekhnē → Sophia
    # --- X-HA: Hormē → Akribeia (8) ---
    "X-HA1": _m("X-HA1", "H1", "A1"),  # Propatheia → Pathos
    "X-HA2": _m("X-HA2", "H1", "A2"),  # Propatheia → Krisis
    "X-HA3": _m("X-HA3", "H3", "A1"),  # Orexis → Pathos
    "X-HA4": _m("X-HA4", "H3", "A2"),  # Orexis → Krisis
    "X-HA5": _m("X-HA5", "H2", "A3"),  # Pistis → Gnōmē
    "X-HA6": _m("X-HA6", "H2", "A4"),  # Pistis → Epistēmē
    "X-HA7": _m("X-HA7", "H4", "A3"),  # Doxa → Gnōmē
    "X-HA8": _m("X-HA8", "H4", "A4"),  # Doxa → Epistēmē
    # --- X-HK: Hormē → Kairos (8) ---
    "X-HK1": _m("X-HK1", "H1", "K1"),  # Propatheia → Eukairia
    "X-HK2": _m("X-HK2", "H1", "K3"),  # Propatheia → Telos
    "X-HK3": _m("X-HK3", "H3", "K1"),  # Orexis → Eukairia
    "X-HK4": _m("X-HK4", "H3", "K3"),  # Orexis → Telos
    "X-HK5": _m("X-HK5", "H2", "K2"),  # Pistis → Chronos
    "X-HK6": _m("X-HK6", "H2", "K4"),  # Pistis → Sophia
    "X-HK7": _m("X-HK7", "H4", "K2"),  # Doxa → Chronos
    "X-HK8": _m("X-HK8", "H4", "K4"),  # Doxa → Sophia
    # --- X-KA: Kairos → Akribeia (8) ---
    "X-KA1": _m("X-KA1", "K1", "A1"),  # Eukairia → Pathos
    "X-KA2": _m("X-KA2", "K1", "A2"),  # Eukairia → Krisis
    "X-KA3": _m("X-KA3", "K2", "A1"),  # Chronos → Pathos
    "X-KA4": _m("X-KA4", "K2", "A2"),  # Chronos → Krisis
    "X-KA5": _m("X-KA5", "K3", "A3"),  # Telos → Gnōmē
    "X-KA6": _m("X-KA6", "K3", "A4"),  # Telos → Epistēmē
    "X-KA7": _m("X-KA7", "K4", "A3"),  # Sophia → Gnōmē
    "X-KA8": _m("X-KA8", "K4", "A4"),  # Sophia → Epistēmē
}


# PURPOSE: Build a Cone from theorem outputs
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


# =============================================================================
# Functor Registry (concrete instances)
# =============================================================================


FUNCTORS: Dict[str, Functor] = {
    # L (left adjoint): /boot — expand compressed memory to full session
    "boot": Functor(
        name="boot",
        source_cat="Mem",
        target_cat="Ses",
        object_map={
            "handoff": "session_context",
            "ki": "knowledge_items",
            "self_profile": "agent_state",
            "doxa": "beliefs",
        },
        morphism_map={
            "restore": "expand",
            "decompress": "hydrate",
        },
    ),
    # R (right adjoint): /bye — compress session to memory
    "bye": Functor(
        name="bye",
        source_cat="Ses",
        target_cat="Mem",
        object_map={
            "session_context": "handoff",
            "knowledge_items": "ki",
            "agent_state": "self_profile",
            "beliefs": "doxa",
        },
        morphism_map={
            "summarize": "compress",
            "extract": "distill",
        },
    ),
    # T (endofunctor): /zet — question generation
    "zet": Functor(
        name="zet",
        source_cat="Cog",
        target_cat="Cog",
        object_map={
            "O1": "O3",  # Noēsis → Zētēsis (recognition generates inquiry)
            "S2": "S4",  # Mekhanē → Praxis (method generates practice)
        },
        is_endofunctor=True,
    ),
    # F: /eat — digest external content into Cog
    "eat": Functor(
        name="eat",
        source_cat="Ext",
        target_cat="Cog",
        object_map={
            "paper": "K4",     # Academic paper → Sophia (wisdom)
            "tutorial": "S2",  # Tutorial → Mekhanē (method)
            "concept": "O1",   # Concept → Noēsis (recognition)
            "rule": "A3",      # Rule → Gnōmē (maxim)
        },
    ),
    # MP: Metacognitive Prompting 5-Stage → Cog
    # Source: Wang & Zhao (2023) arXiv:2308.05342
    # Maps MP stages to the cognitive category as external objects
    "mp": Functor(
        name="MP",
        source_cat="MP",   # MP category (5 stages)
        target_cat="Cog",  # Hegemonikón cognitive category
        object_map={
            "S1": "O1",  # Understanding → Noēsis
            "S2": "A1",  # Preliminary Judgment → Pathos
            "S3": "A2",  # Critical Evaluation → Krisis
            "S4": "O4",  # Decision + Explanation → Energeia
            "S5": "A4",  # Confidence Assessment → Epistēmē
        },
        morphism_map={
            "S1→S2": "X-OH1",  # Understanding→Judgment ≈ Noēsis→Propatheia→Pathos
            "S2→S3": "X-HA2",  # Judgment→Critique ≈ Propatheia→Krisis
            "S3→S4": "X-OS8",  # Critique→Decision ≈ (via A2→O4, approximated)
            "S3→S1": "X-KA2",  # Feedback loop: Critique→Understanding (AMP)
        },
    ),
}


# =============================================================================
# Natural Transformation Registry (concrete instances)
# =============================================================================


NATURAL_TRANSFORMATIONS: Dict[str, NaturalTransformation] = {
    # η (unit of boot⊣bye): Id_Mem ⇒ R∘L
    # "How well does bye(boot(mem)) preserve mem?"
    # Components map Mem objects to theorems governing preservation:
    #   handoff → H4 (Doxa: belief/context preservation)
    #   ki      → K4 (Sophia: knowledge preservation)
    #   self_profile → A4 (Epistēmē: identity knowledge)
    #   doxa    → H4 (Doxa: belief persistence)
    "eta": NaturalTransformation(
        name="η",
        source_functor="Id_Mem",
        target_functor="bye∘boot",
        components={
            "handoff": "H4",        # Doxa preserves context/beliefs
            "ki": "K4",             # Sophia preserves knowledge
            "self_profile": "A4",   # Epistēmē preserves identity
            "doxa": "H4",           # Doxa preserves beliefs
        },
    ),
    # ε (counit of boot⊣bye): L∘R ⇒ Id_Ses
    # "How well does boot(bye(ses)) restore ses?"
    # Components map Ses objects to theorems governing restoration:
    #   session_context → O1 (Noēsis: context recognition)
    #   knowledge_items → K4 (Sophia: knowledge retrieval)
    #   agent_state     → O4 (Energeia: state activation)
    #   beliefs         → H4 (Doxa: belief restoration)
    "epsilon": NaturalTransformation(
        name="ε",
        source_functor="boot∘bye",
        target_functor="Id_Ses",
        components={
            "session_context": "O1",    # Noēsis restores context recognition
            "knowledge_items": "K4",    # Sophia restores knowledge
            "agent_state": "O4",        # Energeia restores active state
            "beliefs": "H4",            # Doxa restores beliefs
        },
    ),
    # η_MP: MP ⇒ HGK — Metacognitive Prompting → Hegemonikón
    # Source: Wang & Zhao (2023) arXiv:2308.05342
    # Each component η_i maps MP Stage i to the corresponding HGK theorem.
    # Operationally: "Stage i of MP is implemented by theorem T in HGK"
    "mp_hgk": NaturalTransformation(
        name="η_MP",
        source_functor="MP",
        target_functor="HGK",
        components={
            "S1": "O1",  # η₁: 理解 → Noēsis (Understanding)
            "S2": "A1",  # η₂: 予備判断 → Pathos (感情精緻化, Bridge U→R)
            "S3": "A2",  # η₃: 批判的再評価 → Krisis (判定, Reasoning)
            "S4": "O4",  # η₄: 決定+説明 → Energeia (活動, Understanding)
            "S5": "A4",  # η₅: 確信度評価 → Epistēmē (知識確定, Reasoning)
        },
    ),
}


# =============================================================================
# Composed Functors (CR-2: co-located with FUNCTORS for discoverability)
# =============================================================================

# Pre-compute bye∘boot and boot∘bye for η/ε adjunction auto-resolve.
# η target_functor = "bye∘boot", ε source_functor = "boot∘bye"
_boot = FUNCTORS["boot"]
_bye = FUNCTORS["bye"]
FUNCTORS["bye∘boot"] = _boot.compose(_bye)  # Mem → Mem (η target)
FUNCTORS["boot∘bye"] = _bye.compose(_boot)  # Ses → Ses (ε source)
