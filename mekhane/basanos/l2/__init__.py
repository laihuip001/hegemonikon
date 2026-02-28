# PROOF: [L2/Mekhane] <- mekhane/ A0->Existence
# PURPOSE: L2 問い生成機構 — 構造的差分検出によるズレの発見
# REASON: F⊣G 随伴構造の ε/η deficit を具象化し、自動的に問いを生成するため
"""
Basanos L2: Structural Deficit Detection

F⊣G adjunction-based question generation:
- η deficit: External knowledge not absorbed into HGK
- ε deficit: HGK claims lacking implementation or justification
- Δε/Δt deficit: Changes introducing new discrepancies
"""

from mekhane.basanos.l2.models import (
    ExternalForm,
    Deficit,
    DeficitType,
    HGKConcept,
    Question,
)
from mekhane.basanos.l2.g_struct import GStruct
from mekhane.basanos.l2.g_semantic import GSemantic
from mekhane.basanos.l2.hom import HomCalculator, HomScore

__all__ = [
    "ExternalForm",
    "Deficit",
    "DeficitType",
    "HGKConcept",
    "Question",
    "GStruct",
    "GSemantic",
    "HomCalculator",
    "HomScore",
]

