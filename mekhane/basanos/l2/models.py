# PROOF: [L2/Basanos] <- mekhane/l2/ A0->Auto->AddedByCI
# PURPOSE: L2 問い生成のコアデータモデル — deficit と question の型定義
# REASON: F⊣G 随伴構造の概念を Python の型として具象化するため
"""Core data models for Basanos L2 structural deficit detection."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DeficitType(Enum):
    """Type of structural deficit detected."""

    ETA = "η"  # External knowledge not absorbed into HGK
    EPSILON_IMPL = "ε-impl"  # HGK claim lacking implementation
    EPSILON_JUST = "ε-just"  # HGK claim lacking external justification
    DELTA = "Δε/Δt"  # Change-introduced discrepancy


@dataclass(frozen=True)
class ExternalForm:
    """G(hgk): HGK concept projected into external-comparable form.

    This is the output of G_struct ∘ G_semantic.
    G_struct extracts structural elements mechanically.
    G_semantic (LLM) translates HGK-specific terms to general terms.
    """

    source_path: str  # e.g. "kernel/ousia.md"
    keywords: list[str] = field(default_factory=list)
    mechanisms: list[str] = field(default_factory=list)
    claims: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)  # extends/requires
    theorem_ids: list[str] = field(default_factory=list)  # e.g. ["O1", "O2"]


@dataclass(frozen=True)
class HGKConcept:
    """Internal HGK concept extracted from kernel/."""

    doc_id: str  # YAML frontmatter doc_id
    path: str  # file path relative to project root
    title: str  # document title
    series: str  # O, S, H, P, K, A
    theorem_ids: list[str] = field(default_factory=list)
    status: str = "CANONICAL"
    extends: list[str] = field(default_factory=list)  # axiom dependencies
    has_proof: bool = False  # PROOF.md exists in implementation dir
    has_implementation: bool = False  # mekhane/ counterpart exists


@dataclass
class Deficit:
    """Structural discrepancy detected by Basanos L2.

    Each deficit naturally generates a question.
    """

    type: DeficitType
    severity: float  # 0.0 - 1.0
    source: str  # what was compared
    target: str  # against what
    description: str  # human-readable description
    evidence: list[str] = field(default_factory=list)  # supporting facts
    suggested_action: Optional[str] = None

    def to_question(self) -> Question:
        """Convert deficit to a natural question."""
        templates = {
            DeficitType.ETA: "論文「{source}」の概念が HGK に取り込まれていないのはなぜか？ 取り込むべきか？",
            DeficitType.EPSILON_IMPL: "kernel/{source} で定義された {target} の実装が存在しない。実装すべきか？ 優先度は？",
            DeficitType.EPSILON_JUST: "{source} の主張「{target}」に外部学術的根拠があるか？",
            DeficitType.DELTA: "最近の変更で {source} と {target} の間に新たなズレが生じた。意図的か？",
        }
        text = templates.get(self.type, "{source} と {target} にズレがある").format(
            source=self.source, target=self.target
        )
        return Question(
            text=text,
            deficit=self,
            priority=self.severity,
        )


@dataclass
class Question:
    """Question generated from a structural deficit."""

    text: str
    deficit: Deficit
    priority: float  # 0.0 - 1.0, higher = more important
    answered: bool = False
    answer: Optional[str] = None
