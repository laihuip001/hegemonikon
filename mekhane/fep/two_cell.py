#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/fep/two_cell.py S2→Mekhane→Implementation
"""
Two-Cell — Weak 2-Category Structure for Derivatives

Origin: G1 of /bou category theory roadmap (2026-02-11)
Mathematical Basis: L3 of mathematical_basis — derivatives as 2-cells in bicategory

Each theorem (1-cell) has 3 derivatives.
Each pair of derivatives defines a 2-cell (transition).
24 theorems × 3 derivatives × 6 transitions (including identities) = the 2-cell structure.

Design decision (2026-02-11):
    The relationship of +/- CCL modifiers to 2-cells is DEFERRED.
    This module focuses solely on derivative ↔ derivative transitions.
    The meaning of +/- across L1/L2/L3 layers will be determined
    after the weak 2-category structure is solidified.

    "弱2-圏を固めきってから、考える" — Creator, 2026-02-11

Design symmetry:
    drift_calculator:   source + compressed → DriftResult (L2: Hom value)
    two_cell:           theorem + derivatives → DerivativeSpace (L3: 2-cells)
    cone_builder:       WF outputs → Cone (C0-C3)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# =============================================================================
# Core Data Structures
# =============================================================================


# PURPOSE: の統一的インターフェースを実現する
@dataclass
class TwoCell:
    """A 2-cell: transition between two derivatives of the same theorem.

    In a weak 2-category (bicategory):
        - 0-cells: categories (Mem, Ses, etc.)
        - 1-cells: functors / WFs (/noe, /bou, ...)
        - 2-cells: transitions between derivatives (nous ⇒ phro)

    The weak (lax) nature means composition is associative
    only up to isomorphism, not strictly.
    """

    theorem: str       # e.g., "O1"
    source: str        # e.g., "nous"
    target: str        # e.g., "phro"
    is_identity: bool = False

    # PURPOSE: two_cell の label 処理を実行する
    @property
    def label(self) -> str:
        if self.is_identity:
            return f"id({self.source})"
        return f"{self.source} ⇒ {self.target}"

    # PURPOSE: two_cell の compose 処理を実行する
    def compose(self, other: "TwoCell") -> Optional["TwoCell"]:
        """Vertical composition of 2-cells.

        (α: f→g) ∘ (β: g→h) = (α∘β: f→h)

        Returns None if composition is not defined (target ≠ other.source).
        """
        if self.theorem != other.theorem:
            return None  # Must be same theorem
        if self.target != other.source:
            return None  # Composability condition

        # Identity laws
        if self.is_identity:
            return other
        if other.is_identity:
            return self

        return TwoCell(
            theorem=self.theorem,
            source=self.source,
            target=other.target,
        )


# PURPOSE: の統一的インターフェースを実現する
@dataclass
class DerivativeSpace:
    """Weak 2-category structure for a single theorem's derivatives.

    Contains the 3 derivatives and all valid 2-cells between them.
    """

    theorem: str                       # e.g., "O1"
    theorem_name: str                  # e.g., "Noēsis"
    series: str                        # e.g., "O"
    derivatives: List[str]             # e.g., ["nous", "phro", "meta"]
    derivative_labels: Dict[str, str]  # e.g., {"nous": "本質直観", ...}

    # PURPOSE: two_cell の two cells 処理を実行する
    @property
    def two_cells(self) -> List[TwoCell]:
        """All valid 2-cells (including identities).

        For 3 derivatives:
            3 identities + 6 transitions = 9 total
        """
        cells: List[TwoCell] = []
        for d in self.derivatives:
            cells.append(TwoCell(self.theorem, d, d, is_identity=True))
        for i, src in enumerate(self.derivatives):
            for j, tgt in enumerate(self.derivatives):
                if i != j:
                    cells.append(TwoCell(self.theorem, src, tgt))
        return cells

    # PURPOSE: two_cell の non identity cells 処理を実行する
    @property
    def non_identity_cells(self) -> List[TwoCell]:
        """Only non-identity 2-cells (transitions)."""
        return [c for c in self.two_cells if not c.is_identity]

    # PURPOSE: cell を取得する
    def get_cell(self, source: str, target: str) -> Optional[TwoCell]:
        """Get a specific 2-cell by source and target."""
        if source not in self.derivatives or target not in self.derivatives:
            return None
        return TwoCell(
            self.theorem, source, target,
            is_identity=(source == target),
        )

    # PURPOSE: composition を検証する
    def verify_composition(self) -> List[str]:
        """Verify weak associativity of 2-cell composition.

        In a weak 2-category, (α∘β)∘γ ≅ α∘(β∘γ) (up to isomorphism).
        For our finite derivatives, this means both compositions
        should yield the same source→target 2-cell.

        Returns list of violations (empty if valid).
        """
        violations: List[str] = []
        for a in self.derivatives:
            for b in self.derivatives:
                for c in self.derivatives:
                    ab = self.get_cell(a, b)
                    bc = self.get_cell(b, c)
                    ac = self.get_cell(a, c)
                    if ab and bc and ac:
                        composed = ab.compose(bc)
                        if composed is None:
                            violations.append(
                                f"Composition failed: {ab.label} ∘ {bc.label}"
                            )
                        elif composed.source != ac.source or composed.target != ac.target:
                            violations.append(
                                f"Associativity: ({ab.label} ∘ {bc.label}) ≠ {ac.label}"
                            )
        return violations


# =============================================================================
# 24 Theorem Registry
# =============================================================================

# Each entry: (theorem_code, theorem_name, series, [d1, d2, d3], {d: label})
_THEOREM_DATA: List[Tuple[str, str, str, List[str], Dict[str, str]]] = [
    # O-Series (Ousia)
    ("O1", "Noēsis", "O", ["nous", "phro", "meta"],
     {"nous": "本質直観", "phro": "実践知", "meta": "反省"}),
    ("O2", "Boulēsis", "O", ["desir", "voli", "akra"],
     {"desir": "欲求", "voli": "意志", "akra": "弱さ"}),
    ("O3", "Zētēsis", "O", ["anom", "hypo", "eval"],
     {"anom": "異常", "hypo": "仮説", "eval": "評価"}),
    ("O4", "Energeia", "O", ["flow", "prax", "pois"],
     {"flow": "フロー", "prax": "実践", "pois": "制作"}),

    # S-Series (Schema)
    ("S1", "Metron", "S", ["cont", "disc", "abst"],
     {"cont": "連続", "disc": "離散", "abst": "抽象"}),
    ("S2", "Mekhanē", "S", ["comp", "inve", "adap"],
     {"comp": "組合", "inve": "発明", "adap": "適応"}),
    ("S3", "Stathmos", "S", ["norm", "empi", "rela"],
     {"norm": "規範", "empi": "経験", "rela": "相対"}),
    ("S4", "Praxis", "S", ["prax", "pois", "temp"],
     {"prax": "自己目的", "pois": "産出", "temp": "時間"}),

    # H-Series (Hormē)
    ("H1", "Propatheia", "H", ["appr", "avoi", "arre"],
     {"appr": "接近", "avoi": "回避", "arre": "停止"}),
    ("H2", "Pistis", "H", ["subj", "inte", "obje"],
     {"subj": "主観", "inte": "間主観", "obje": "客観"}),
    ("H3", "Orexis", "H", ["targ", "acti", "stat"],
     {"targ": "対象", "acti": "活動", "stat": "状態"}),
    ("H4", "Doxa", "H", ["sens", "conc", "form"],
     {"sens": "感覚", "conc": "概念", "form": "形式"}),

    # P-Series (Perigraphē)
    ("P1", "Khōra", "P", ["phys", "conc", "rela"],
     {"phys": "物理", "conc": "概念", "rela": "関係"}),
    ("P2", "Hodos", "P", ["line", "bran", "cycl"],
     {"line": "線形", "bran": "分岐", "cycl": "循環"}),
    ("P3", "Trokhia", "P", ["fixe", "adap", "emer"],
     {"fixe": "固定", "adap": "適応", "emer": "創発"}),
    ("P4", "Tekhnē", "P", ["manu", "mech", "auto"],
     {"manu": "手動", "mech": "機械", "auto": "自動"}),

    # K-Series (Kairos)
    ("K1", "Eukairia", "K", ["urge", "opti", "miss"],
     {"urge": "緊急", "opti": "最適", "miss": "逸失"}),
    ("K2", "Chronos", "K", ["shor", "medi", "long"],
     {"shor": "短期", "medi": "中期", "long": "長期"}),
    ("K3", "Telos", "K", ["intr", "inst", "ulti"],
     {"intr": "内在", "inst": "手段", "ulti": "究極"}),
    ("K4", "Sophia", "K", ["taci", "expl", "meta"],
     {"taci": "暗黙", "expl": "明示", "meta": "メタ"}),

    # A-Series (Akribeia)
    ("A1", "Pathos", "A", ["prim", "seco", "regu"],
     {"prim": "一次", "seco": "二次", "regu": "調整"}),
    ("A2", "Krisis", "A", ["affi", "nega", "susp"],
     {"affi": "肯定", "nega": "否定", "susp": "保留"}),
    ("A3", "Gnōmē", "A", ["conc", "abst", "univ"],
     {"conc": "具体", "abst": "抽象", "univ": "普遍"}),
    ("A4", "Epistēmē", "A", ["tent", "just", "cert"],
     {"tent": "暫定", "just": "正当化", "cert": "確実"}),
]


# PURPOSE: derivative space を取得する
def get_derivative_space(theorem: str) -> Optional[DerivativeSpace]:
    """Get the DerivativeSpace for a theorem.

    Args:
        theorem: Theorem code (e.g., "O1", "S2", "A4")

    Returns:
        DerivativeSpace or None if theorem not found.
    """
    for code, name, series, derivs, labels in _THEOREM_DATA:
        if code == theorem:
            return DerivativeSpace(
                theorem=code,
                theorem_name=name,
                series=series,
                derivatives=derivs,
                derivative_labels=labels,
            )
    return None


# PURPOSE: all spaces を取得する
def get_all_spaces() -> List[DerivativeSpace]:
    """Get DerivativeSpaces for all 24 theorems."""
    return [
        DerivativeSpace(code, name, series, derivs, labels)
        for code, name, series, derivs, labels in _THEOREM_DATA
    ]


# PURPOSE: series spaces を取得する
def get_series_spaces(series: str) -> List[DerivativeSpace]:
    """Get DerivativeSpaces for a specific series (O, S, H, P, K, A)."""
    return [
        DerivativeSpace(code, name, s, derivs, labels)
        for code, name, s, derivs, labels in _THEOREM_DATA
        if s == series
    ]


# =============================================================================
# Statistics & Verification
# =============================================================================


# PURPOSE: two_cell の count two cells 処理を実行する
def count_two_cells() -> Dict[str, int]:
    """Count total 2-cells across the system.

    Expected:
        24 theorems × 9 cells/theorem = 216 total
        24 × 3 identities = 72 identity cells
        24 × 6 transitions = 144 non-identity cells
    """
    spaces = get_all_spaces()
    total = sum(len(s.two_cells) for s in spaces)
    identities = sum(
        sum(1 for c in s.two_cells if c.is_identity) for s in spaces
    )
    return {
        "theorems": len(spaces),
        "total_two_cells": total,
        "identity_cells": identities,
        "transition_cells": total - identities,
    }


# PURPOSE: all を検証する
def verify_all() -> Dict[str, List[str]]:
    """Verify weak associativity for all theorem spaces.

    Returns dict of theorem → list of violations.
    Empty violations means the space is valid.
    """
    results: Dict[str, List[str]] = {}
    for space in get_all_spaces():
        violations = space.verify_composition()
        if violations:
            results[space.theorem] = violations
    return results


# =============================================================================
# Display
# =============================================================================


# PURPOSE: two_cell の describe space 処理を実行する
def describe_space(space: DerivativeSpace) -> str:
    """Human-readable description of a derivative space."""
    lines = [
        f"📐 DerivativeSpace: {space.theorem} {space.theorem_name} ({space.series}-series)",
        f"  Derivatives: {', '.join(space.derivatives)}",
        f"  2-cells: {len(space.two_cells)} ({len(space.non_identity_cells)} transitions + "
        f"{len(space.derivatives)} identities)",
        "",
        "  Transitions:",
    ]
    for cell in space.non_identity_cells:
        src_label = space.derivative_labels.get(cell.source, "")
        tgt_label = space.derivative_labels.get(cell.target, "")
        lines.append(f"    {cell.source}({src_label}) ⇒ {cell.target}({tgt_label})")
    return "\n".join(lines)


# PURPOSE: two_cell の describe summary 処理を実行する
def describe_summary() -> str:
    """Summary of the entire 2-cell structure."""
    counts = count_two_cells()
    violations = verify_all()
    lines = [
        "📐 Weak 2-Category Summary",
        f"  Theorems:        {counts['theorems']}",
        f"  Total 2-cells:   {counts['total_two_cells']}",
        f"  Identities:      {counts['identity_cells']}",
        f"  Transitions:     {counts['transition_cells']}",
        f"  Violations:      {sum(len(v) for v in violations.values())}",
    ]
    if violations:
        lines.append("")
        lines.append("  ⚠️ Violations:")
        for thm, vs in violations.items():
            for v in vs:
                lines.append(f"    {thm}: {v}")
    else:
        lines.append("  ✅ All compositions verified")
    return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        theorem = sys.argv[1].upper()
        space = get_derivative_space(theorem)
        if space:
            print(describe_space(space))
        else:
            print(f"Unknown theorem: {theorem}")
            sys.exit(1)
    else:
        print(describe_summary())
        print()
        for space in get_all_spaces():
            print(describe_space(space))
            print()
