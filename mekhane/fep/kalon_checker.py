# PROOF: [L2/品質検証] <- mekhane/fep/
"""
PROOF: [L2/品質検証] このファイルは存在しなければならない

A0 → 圏論的構造の品質 (Kalon) を定量評価する必要がある
   → category.py の型定義が「美しい不動点」に到達しているか検証する
   → kalon_checker.py が担う

Q.E.D.

---

Kalon (καλόν) Checker — 圏論的構造の品質検証

Kalon の定義:
    Kalon(x) ⟺ x = Fix(G∘F)
    
    概念 x が「美しい」とは、
    F(抽象化) と G(具体化) の反復が不動点に到達し、
    もはや変化しない状態に安定していること。

判定基準 (BC-17 表現完全性から導出):
    - 抽象: 数式/定義が1つ以上あるか
    - 具体: 異なる文脈の例が3つ以上あるか
    - 操作: 使い方が明示されているか
    - 構造: 圏論的対応が定義されているか

Checks:
    1. Series Enrichment: 全6 series に Enrichment が定義されているか
    2. Adjoint Pairs: 12随伴対が完全か
    3. Kalon Score: Enrichment の kalon スコアが閾値以上か
    4. Structural Completeness: Theorem/Morphism/Cone/Adjunction の整合性
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

from mekhane.fep.category import (
    ADJOINT_PAIRS_D,
    SERIES_ENRICHMENTS,
    AdjointPair,
    Enrichment,
    GaloisConnection,
    Series,
)


# PURPOSE: Quality level of a Kalon check
class KalonLevel(Enum):
    """Quality level of a Kalon check result."""

    KALON = "kalon"          # 美しい: Fix(G∘F) 到達
    APPROACHING = "approaching"  # 近づいている: 軽微な問題のみ
    INCOMPLETE = "incomplete"    # 不完全: 重要な要素が欠けている
    ABSENT = "absent"            # 不在: 骨格すらない


# PURPOSE: Result of a single Kalon check
@dataclass
class KalonResult:
    """Result of a single Kalon check.
    
    Represents the outcome of checking one aspect of Kalon quality.
    """

    name: str
    level: KalonLevel
    score: float  # 0.0 - 1.0
    details: str = ""
    issues: List[str] = field(default_factory=list)

    # PURPOSE: [L2-auto] Whether this check passes Kalon quality.
    @property
    def is_kalon(self) -> bool:
        """Whether this check passes Kalon quality."""
        return self.level == KalonLevel.KALON


# PURPOSE: Aggregate report from checking all Kalon dimensions
@dataclass
class KalonReport:
    """Aggregate report from all Kalon checks.
    
    Combines individual check results into an overall assessment.
    """

    results: List[KalonResult] = field(default_factory=list)
    timestamp: str = ""

    # PURPOSE: [L2-auto] Weighted average of all check scores.
    @property
    def overall_score(self) -> float:
        """Weighted average of all check scores."""
        if not self.results:
            return 0.0
        return sum(r.score for r in self.results) / len(self.results)

    # PURPOSE: [L2-auto] Overall Kalon level based on individual results.
    @property
    def overall_level(self) -> KalonLevel:
        """Overall Kalon level based on individual results."""
        if not self.results:
            return KalonLevel.ABSENT
        
        levels = [r.level for r in self.results]
        if all(l == KalonLevel.KALON for l in levels):
            return KalonLevel.KALON
        if any(l == KalonLevel.ABSENT for l in levels):
            return KalonLevel.INCOMPLETE
        if all(l in (KalonLevel.KALON, KalonLevel.APPROACHING) for l in levels):
            return KalonLevel.APPROACHING
        return KalonLevel.INCOMPLETE

    # PURPOSE: [L2-auto] Collect all issues from all results.
    @property
    def all_issues(self) -> List[str]:
        """Collect all issues from all results."""
        issues = []
        for r in self.results:
            for issue in r.issues:
                issues.append(f"[{r.name}] {issue}")
        return issues

    # PURPOSE: [L2-auto] One-line summary of the report.
    def summary(self) -> str:
        """One-line summary of the report."""
        passed = sum(1 for r in self.results if r.is_kalon)
        total = len(self.results)
        return (
            f"Kalon: {self.overall_level.value} "
            f"({passed}/{total} checks passed, "
            f"score={self.overall_score:.2f})"
        )


# PURPOSE: 圏論的構造の品質 (Kalon) を検証し、Fix(G∘F) 不動点到達を判定する
class KalonChecker:
    """Kalon (καλόν) Checker — 圏論的構造の品質検証.

    Checks whether the categorical structures in category.py
    have reached the Fix(G∘F) fixed point of quality.
    
    F = 抽象化 (concrete → abstract definition)
    G = 具体化 (abstract → concrete example)
    Fix(G∘F) = 反復しても変化しない不動点

    Usage:
        checker = KalonChecker()
        report = checker.check_all()
        print(report.summary())
    """

    # PURPOSE: Minimum kalon score threshold for each series
    KALON_THRESHOLD: float = 0.70

    # PURPOSE: Expected number of structures (evidence items) per enrichment
    MIN_STRUCTURES: int = 2

    # PURPOSE: [L2-auto] Initialize the Kalon checker.
    def __init__(
        self,
        enrichments: Optional[Dict[Series, Enrichment]] = None,
        adjoint_pairs: Optional[Dict[str, AdjointPair]] = None,
        kalon_threshold: float = 0.70,
    ):
        """Initialize the Kalon checker.

        Args:
            enrichments: Series enrichment map (defaults to SERIES_ENRICHMENTS)
            adjoint_pairs: Adjoint pair registry (defaults to ADJOINT_PAIRS_D)
            kalon_threshold: Minimum kalon score for passing
        """
        self.enrichments = enrichments or SERIES_ENRICHMENTS
        self.adjoint_pairs = adjoint_pairs or ADJOINT_PAIRS_D
        self.kalon_threshold = kalon_threshold

    # PURPOSE: Run all Kalon checks and return aggregate report
    def check_all(self) -> KalonReport:
        """Run all Kalon quality checks.

        Returns:
            KalonReport aggregating all individual checks
        """
        report = KalonReport()
        report.results.append(self.check_enrichment_completeness())
        report.results.append(self.check_enrichment_quality())
        report.results.append(self.check_adjoint_completeness())
        report.results.append(self.check_adjoint_symmetry())
        report.results.append(self.check_galois_derivability())
        return report

    # PURPOSE: Check that all 6 series have Enrichment defined
    def check_enrichment_completeness(self) -> KalonResult:
        """Check that all 6 series have Enrichment metadata.
        
        Every series in Cog must carry a typed enrichment.
        Missing enrichments mean the Hom-set structure is undefined.
        """
        missing = []
        for series in Series:
            if series not in self.enrichments:
                missing.append(series.value)

        covered = len(Series) - len(missing)
        score = covered / len(Series)

        if not missing:
            return KalonResult(
                name="enrichment_completeness",
                level=KalonLevel.KALON,
                score=score,
                details=f"All {len(Series)} series have enrichment defined",
            )
        else:
            return KalonResult(
                name="enrichment_completeness",
                level=KalonLevel.INCOMPLETE,
                score=score,
                details=f"{covered}/{len(Series)} series covered",
                issues=[f"Missing enrichment for: {', '.join(missing)}"],
            )

    # PURPOSE: Check that each Enrichment has sufficient quality (kalon score + structures)
    def check_enrichment_quality(self) -> KalonResult:
        """Check enrichment quality: kalon score and structural evidence.
        
        BC-17 (表現完全性): 概念 = 数式(骨格) + 具体例(肉) + 操作性 + 体温
        Enrichment.structures = 具体例のリスト
        Enrichment.kalon = 品質スコア (None for Set = intentionally empty)
        """
        issues = []
        scores = []

        for series, enrichment in self.enrichments.items():
            # Set (P-series) intentionally has no enrichment → skip score check
            if enrichment.kalon is None:
                scores.append(1.0)  # Intentional absence = valid design choice
                continue

            # Check kalon score threshold
            if enrichment.kalon < self.kalon_threshold:
                issues.append(
                    f"{series.value}: kalon={enrichment.kalon:.2f} "
                    f"< threshold {self.kalon_threshold:.2f}"
                )
                scores.append(enrichment.kalon)
            else:
                scores.append(enrichment.kalon)

            # Check structural evidence (BC-17: 具体3)
            if len(enrichment.structures) < self.MIN_STRUCTURES:
                issues.append(
                    f"{series.value}: only {len(enrichment.structures)} "
                    f"structures (need ≥{self.MIN_STRUCTURES})"
                )

        avg_score = sum(scores) / len(scores) if scores else 0.0

        if not issues:
            return KalonResult(
                name="enrichment_quality",
                level=KalonLevel.KALON,
                score=avg_score,
                details=f"All enrichments meet quality threshold (avg={avg_score:.2f})",
            )
        elif avg_score >= self.kalon_threshold:
            return KalonResult(
                name="enrichment_quality",
                level=KalonLevel.APPROACHING,
                score=avg_score,
                details=f"Average score {avg_score:.2f} meets threshold but issues remain",
                issues=issues,
            )
        else:
            return KalonResult(
                name="enrichment_quality",
                level=KalonLevel.INCOMPLETE,
                score=avg_score,
                details=f"Average score {avg_score:.2f} below threshold",
                issues=issues,
            )

    # PURPOSE: Check that all 12 adjoint pairs (2 per series) are present
    def check_adjoint_completeness(self) -> KalonResult:
        """Check that all 12 D-type adjoint pairs are registered.
        
        Each series should have exactly 2 adjoint pairs:
        D1 (T1⊣T3) and D2 (T2⊣T4).
        """
        expected_keys = set()
        for series in Series:
            s = series.name  # O, S, H, P, K, A
            expected_keys.add(f"{s}-D1")
            expected_keys.add(f"{s}-D2")

        actual_keys = set(self.adjoint_pairs.keys())
        missing = expected_keys - actual_keys
        extra = actual_keys - expected_keys

        issues = []
        if missing:
            issues.append(f"Missing adjoint pairs: {', '.join(sorted(missing))}")
        if extra:
            issues.append(f"Unexpected adjoint pairs: {', '.join(sorted(extra))}")

        score = len(expected_keys & actual_keys) / len(expected_keys)

        if not issues:
            return KalonResult(
                name="adjoint_completeness",
                level=KalonLevel.KALON,
                score=score,
                details=f"All {len(expected_keys)} adjoint pairs present",
            )
        else:
            return KalonResult(
                name="adjoint_completeness",
                level=KalonLevel.INCOMPLETE if missing else KalonLevel.APPROACHING,
                score=score,
                details=f"{len(expected_keys & actual_keys)}/{len(expected_keys)} pairs present",
                issues=issues,
            )

    # PURPOSE: Check that each adjoint pair is symmetric (L ⊣ R has distinct L ≠ R)
    def check_adjoint_symmetry(self) -> KalonResult:
        """Check adjoint pair structural integrity.
        
        Each pair must satisfy:
        - left_wf ≠ right_wf (non-degenerate)
        - left_theorem ≠ right_theorem (non-identity)
        - series matches the theorem prefix
        """
        issues = []

        for key, pair in self.adjoint_pairs.items():
            # Non-degenerate
            if pair.left_wf == pair.right_wf:
                issues.append(f"{key}: degenerate pair (L=R={pair.left_wf})")

            # Non-identity
            if pair.left_theorem == pair.right_theorem:
                issues.append(
                    f"{key}: identity adjunction "
                    f"({pair.left_theorem}={pair.right_theorem})"
                )

            # Series consistency
            expected_prefix = pair.series.name
            if not pair.left_theorem.startswith(expected_prefix):
                issues.append(
                    f"{key}: left theorem {pair.left_theorem} "
                    f"doesn't match series {expected_prefix}"
                )
            if not pair.right_theorem.startswith(expected_prefix):
                issues.append(
                    f"{key}: right theorem {pair.right_theorem} "
                    f"doesn't match series {expected_prefix}"
                )

        total = len(self.adjoint_pairs)
        problematic = len(set(i.split(":")[0] for i in issues))
        score = (total - problematic) / total if total else 0.0

        if not issues:
            return KalonResult(
                name="adjoint_symmetry",
                level=KalonLevel.KALON,
                score=1.0,
                details=f"All {total} pairs have valid structure",
            )
        else:
            return KalonResult(
                name="adjoint_symmetry",
                level=KalonLevel.INCOMPLETE,
                score=score,
                details=f"{total - problematic}/{total} pairs structurally valid",
                issues=issues,
            )

    # PURPOSE: Check that every AdjointPair can derive a GaloisConnection
    def check_galois_derivability(self) -> KalonResult:
        """Check that every adjoint pair produces a valid Galois connection.
        
        AdjointPair.galois() should return a well-formed GaloisConnection
        with matching series and non-empty description.
        """
        issues = []

        for key, pair in self.adjoint_pairs.items():
            gc = pair.galois
            if not isinstance(gc, GaloisConnection):
                issues.append(f"{key}: galois() returned {type(gc)}, expected GaloisConnection")
                continue

            if gc.series != pair.series:
                issues.append(
                    f"{key}: Galois series mismatch "
                    f"({gc.series} ≠ {pair.series})"
                )

            if not gc.description:
                issues.append(f"{key}: Galois connection has empty description")

        total = len(self.adjoint_pairs)
        problematic = len(set(i.split(":")[0] for i in issues))
        score = (total - problematic) / total if total else 0.0

        if not issues:
            return KalonResult(
                name="galois_derivability",
                level=KalonLevel.KALON,
                score=1.0,
                details=f"All {total} pairs derive valid Galois connections",
            )
        else:
            return KalonResult(
                name="galois_derivability",
                level=KalonLevel.APPROACHING if problematic <= 2 else KalonLevel.INCOMPLETE,
                score=score,
                details=f"{total - problematic}/{total} pairs derive valid Galois",
                issues=issues,
            )
