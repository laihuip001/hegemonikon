#!/usr/bin/env python3
"""Tests for two_cell.py — Weak 2-category structure."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from mekhane.fep.two_cell import (
    TwoCell,
    DerivativeSpace,
    get_derivative_space,
    get_all_spaces,
    get_series_spaces,
    count_two_cells,
    verify_all,
    describe_space,
    describe_summary,
)


class TestTwoCell:
    """Test TwoCell data structure."""

    def test_label(self):
        cell = TwoCell("O1", "nous", "phro")
        assert cell.label == "nous ⇒ phro"

    def test_identity_label(self):
        cell = TwoCell("O1", "nous", "nous", is_identity=True)
        assert cell.label == "id(nous)"

    def test_compose_valid(self):
        ab = TwoCell("O1", "nous", "phro")
        bc = TwoCell("O1", "phro", "meta")
        result = ab.compose(bc)
        assert result is not None
        assert result.source == "nous"
        assert result.target == "meta"

    def test_compose_identity_left(self):
        id_a = TwoCell("O1", "nous", "nous", is_identity=True)
        ab = TwoCell("O1", "nous", "phro")
        result = id_a.compose(ab)
        assert result is not None
        assert result.source == "nous"
        assert result.target == "phro"

    def test_compose_identity_right(self):
        ab = TwoCell("O1", "nous", "phro")
        id_b = TwoCell("O1", "phro", "phro", is_identity=True)
        result = ab.compose(id_b)
        assert result is not None
        assert result.source == "nous"
        assert result.target == "phro"

    def test_compose_incompatible(self):
        ab = TwoCell("O1", "nous", "phro")
        cd = TwoCell("O1", "meta", "nous")
        result = ab.compose(cd)
        assert result is None  # phro ≠ meta

    def test_compose_different_theorems(self):
        ab = TwoCell("O1", "nous", "phro")
        cd = TwoCell("O2", "phro", "meta")
        result = ab.compose(cd)
        assert result is None

    def test_compose_associativity(self):
        """(α∘β)∘γ should ≅ α∘(β∘γ) — weak associativity."""
        ab = TwoCell("O1", "nous", "phro")
        bc = TwoCell("O1", "phro", "meta")
        ca = TwoCell("O1", "meta", "nous")

        left = ab.compose(bc)
        assert left is not None
        left_full = left.compose(ca)

        right = bc.compose(ca)
        assert right is not None
        right_full = ab.compose(right)

        assert left_full is not None
        assert right_full is not None
        assert left_full.source == right_full.source == "nous"
        assert left_full.target == right_full.target == "nous"


class TestDerivativeSpace:
    """Test DerivativeSpace structure."""

    def test_o1_space(self):
        space = get_derivative_space("O1")
        assert space is not None
        assert space.theorem == "O1"
        assert space.theorem_name == "Noēsis"
        assert space.series == "O"
        assert space.derivatives == ["nous", "phro", "meta"]

    def test_two_cells_count(self):
        space = get_derivative_space("O1")
        assert space is not None
        # 3 identities + 6 non-identity = 9
        assert len(space.two_cells) == 9
        assert len(space.non_identity_cells) == 6

    def test_get_cell(self):
        space = get_derivative_space("O1")
        assert space is not None
        cell = space.get_cell("nous", "phro")
        assert cell is not None
        assert cell.source == "nous"
        assert cell.target == "phro"
        assert not cell.is_identity

    def test_get_identity_cell(self):
        space = get_derivative_space("O1")
        assert space is not None
        cell = space.get_cell("nous", "nous")
        assert cell is not None
        assert cell.is_identity

    def test_get_cell_invalid(self):
        space = get_derivative_space("O1")
        assert space is not None
        cell = space.get_cell("nous", "invalid")
        assert cell is None

    def test_verify_composition(self):
        space = get_derivative_space("O1")
        assert space is not None
        violations = space.verify_composition()
        assert len(violations) == 0


class TestRegistry:
    """Test the 24-theorem registry."""

    def test_all_spaces_count(self):
        spaces = get_all_spaces()
        assert len(spaces) == 24

    def test_series_counts(self):
        for series in ["O", "S", "H", "P", "K", "A"]:
            spaces = get_series_spaces(series)
            assert len(spaces) == 4, f"{series}-series should have 4 theorems"

    def test_count_two_cells(self):
        counts = count_two_cells()
        assert counts["theorems"] == 24
        assert counts["total_two_cells"] == 216      # 24 × 9
        assert counts["identity_cells"] == 72         # 24 × 3
        assert counts["transition_cells"] == 144      # 24 × 6

    def test_verify_all(self):
        violations = verify_all()
        # All spaces should be valid
        total = sum(len(v) for v in violations.values())
        assert total == 0, f"Found {total} violations: {violations}"

    def test_all_theorems_have_3_derivatives(self):
        for space in get_all_spaces():
            assert len(space.derivatives) == 3, (
                f"{space.theorem} has {len(space.derivatives)} derivatives"
            )

    def test_unknown_theorem(self):
        space = get_derivative_space("Z9")
        assert space is None


class TestDisplay:
    """Test display functions."""

    def test_describe_space(self):
        space = get_derivative_space("O1")
        assert space is not None
        desc = describe_space(space)
        assert "O1" in desc
        assert "Noēsis" in desc
        assert "nous" in desc

    def test_describe_summary(self):
        summary = describe_summary()
        assert "24" in summary
        assert "216" in summary
        assert "✅" in summary
