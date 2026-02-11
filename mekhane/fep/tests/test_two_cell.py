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


# PURPOSE: Test suite validating two cell correctness
class TestTwoCell:
    """Test TwoCell data structure."""

    # PURPOSE: Verify label behaves correctly
    def test_label(self):
        """Verify label behavior."""
        cell = TwoCell("O1", "nous", "phro")
        assert cell.label == "nous ⇒ phro"

    # PURPOSE: Verify identity label behaves correctly
    def test_identity_label(self):
        """Verify identity label behavior."""
        cell = TwoCell("O1", "nous", "nous", is_identity=True)
        assert cell.label == "id(nous)"

    # PURPOSE: Verify compose valid behaves correctly
    def test_compose_valid(self):
        """Verify compose valid behavior."""
        ab = TwoCell("O1", "nous", "phro")
        bc = TwoCell("O1", "phro", "meta")
        result = ab.compose(bc)
        assert result is not None
        assert result.source == "nous"
        assert result.target == "meta"

    # PURPOSE: Verify compose identity left behaves correctly
    def test_compose_identity_left(self):
        """Verify compose identity left behavior."""
        id_a = TwoCell("O1", "nous", "nous", is_identity=True)
        ab = TwoCell("O1", "nous", "phro")
        result = id_a.compose(ab)
        assert result is not None
        assert result.source == "nous"
        assert result.target == "phro"

    # PURPOSE: Verify compose identity right behaves correctly
    def test_compose_identity_right(self):
        """Verify compose identity right behavior."""
        ab = TwoCell("O1", "nous", "phro")
        id_b = TwoCell("O1", "phro", "phro", is_identity=True)
        result = ab.compose(id_b)
        assert result is not None
        assert result.source == "nous"
        assert result.target == "phro"

    # PURPOSE: Verify compose incompatible behaves correctly
    def test_compose_incompatible(self):
        """Verify compose incompatible behavior."""
        ab = TwoCell("O1", "nous", "phro")
        cd = TwoCell("O1", "meta", "nous")
        result = ab.compose(cd)
        assert result is None  # phro ≠ meta

    # PURPOSE: Verify compose different theorems behaves correctly
    def test_compose_different_theorems(self):
        """Verify compose different theorems behavior."""
        ab = TwoCell("O1", "nous", "phro")
        cd = TwoCell("O2", "phro", "meta")
        result = ab.compose(cd)
        assert result is None

    # PURPOSE: Verify compose associativity behaves correctly
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


# PURPOSE: Test suite validating derivative space correctness
class TestDerivativeSpace:
    """Test DerivativeSpace structure."""

    # PURPOSE: Verify o1 space behaves correctly
    def test_o1_space(self):
        """Verify o1 space behavior."""
        space = get_derivative_space("O1")
        assert space is not None
        assert space.theorem == "O1"
        assert space.theorem_name == "Noēsis"
        assert space.series == "O"
        assert space.derivatives == ["nous", "phro", "meta"]

    # PURPOSE: Verify two cells count behaves correctly
    def test_two_cells_count(self):
        """Verify two cells count behavior."""
        space = get_derivative_space("O1")
        assert space is not None
        # 3 identities + 6 non-identity = 9
        assert len(space.two_cells) == 9
        assert len(space.non_identity_cells) == 6

    # PURPOSE: Verify get cell behaves correctly
    def test_get_cell(self):
        """Verify get cell behavior."""
        space = get_derivative_space("O1")
        assert space is not None
        cell = space.get_cell("nous", "phro")
        assert cell is not None
        assert cell.source == "nous"
        assert cell.target == "phro"
        assert not cell.is_identity

    # PURPOSE: Verify get identity cell behaves correctly
    def test_get_identity_cell(self):
        """Verify get identity cell behavior."""
        space = get_derivative_space("O1")
        assert space is not None
        cell = space.get_cell("nous", "nous")
        assert cell is not None
        assert cell.is_identity

    # PURPOSE: Verify get cell invalid behaves correctly
    def test_get_cell_invalid(self):
        """Verify get cell invalid behavior."""
        space = get_derivative_space("O1")
        assert space is not None
        cell = space.get_cell("nous", "invalid")
        assert cell is None

    # PURPOSE: Verify verify composition behaves correctly
    def test_verify_composition(self):
        """Verify verify composition behavior."""
        space = get_derivative_space("O1")
        assert space is not None
        violations = space.verify_composition()
        assert len(violations) == 0


# PURPOSE: Test suite validating registry correctness
class TestRegistry:
    """Test the 24-theorem registry."""

    # PURPOSE: Verify all spaces count behaves correctly
    def test_all_spaces_count(self):
        """Verify all spaces count behavior."""
        spaces = get_all_spaces()
        assert len(spaces) == 24

    # PURPOSE: Verify series counts behaves correctly
    def test_series_counts(self):
        """Verify series counts behavior."""
        for series in ["O", "S", "H", "P", "K", "A"]:
            spaces = get_series_spaces(series)
            assert len(spaces) == 4, f"{series}-series should have 4 theorems"

    # PURPOSE: Verify count two cells behaves correctly
    def test_count_two_cells(self):
        """Verify count two cells behavior."""
        counts = count_two_cells()
        assert counts["theorems"] == 24
        assert counts["total_two_cells"] == 216      # 24 × 9
        assert counts["identity_cells"] == 72         # 24 × 3
        assert counts["transition_cells"] == 144      # 24 × 6

    # PURPOSE: Verify verify all behaves correctly
    def test_verify_all(self):
        """Verify verify all behavior."""
        violations = verify_all()
        # All spaces should be valid
        total = sum(len(v) for v in violations.values())
        assert total == 0, f"Found {total} violations: {violations}"

    # PURPOSE: Verify all theorems have 3 derivatives behaves correctly
    def test_all_theorems_have_3_derivatives(self):
        """Verify all theorems have 3 derivatives behavior."""
        for space in get_all_spaces():
            assert len(space.derivatives) == 3, (
                f"{space.theorem} has {len(space.derivatives)} derivatives"
            )

    # PURPOSE: Verify unknown theorem behaves correctly
    def test_unknown_theorem(self):
        """Verify unknown theorem behavior."""
        space = get_derivative_space("Z9")
        assert space is None


# PURPOSE: Test suite validating display correctness
class TestDisplay:
    """Test display functions."""

    # PURPOSE: Verify describe space behaves correctly
    def test_describe_space(self):
        """Verify describe space behavior."""
        space = get_derivative_space("O1")
        assert space is not None
        desc = describe_space(space)
        assert "O1" in desc
        assert "Noēsis" in desc
        assert "nous" in desc

    # PURPOSE: Verify describe summary behaves correctly
    def test_describe_summary(self):
        """Verify describe summary behavior."""
        summary = describe_summary()
        assert "24" in summary
        assert "216" in summary
        assert "✅" in summary
