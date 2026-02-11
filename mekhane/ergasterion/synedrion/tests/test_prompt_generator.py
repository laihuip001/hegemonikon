# PROOF: [L2/インフラ] <- mekhane/ergasterion/synedrion/tests/ A2→評議会システムが必要→test_prompt_generator が担う
#!/usr/bin/env python3
"""
Tests for Jules Synedrion v2 Prompt Generator.

Verifies the 20×6=120 orthogonal perspective matrix.
"""

import pytest
from pathlib import Path

# Import from parent package
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from mekhane.ergasterion.synedrion.prompt_generator import (
    PerspectiveMatrix,
    Perspective,
)


# PURPOSE: Tests for PerspectiveMatrix class
class TestPerspectiveMatrix:
    """Tests for PerspectiveMatrix class."""

    # PURPOSE: Load the perspective matrix
    @pytest.fixture
    def matrix(self) -> PerspectiveMatrix:
        """Load the perspective matrix."""
        return PerspectiveMatrix.load()

    # PURPOSE: Verify matrix loads successfully
    def test_load_matrix(self, matrix: PerspectiveMatrix):
        """Verify matrix loads successfully."""
        assert matrix is not None
        assert matrix.total_perspectives == 480

    # PURPOSE: Verify 20 domains are defined
    def test_domain_count(self, matrix: PerspectiveMatrix):
        """Verify 20 domains are defined."""
        assert len(matrix.domains) == 20

    # PURPOSE: Verify 6 axes are defined
    def test_axis_count(self, matrix: PerspectiveMatrix):
        """Verify 6 axes are defined."""
        assert len(matrix.axes) == 24

    # PURPOSE: Test getting a specific perspective
    def test_get_perspective(self, matrix: PerspectiveMatrix):
        """Test getting a specific perspective."""
        p = matrix.get("Resource", "O1")
        assert p.domain_id == "Resource"
        assert p.axis_id == "O1"
        assert p.id == "Resource-O1"

    # PURPOSE: Test error on invalid domain
    def test_get_invalid_domain(self, matrix: PerspectiveMatrix):
        """Test error on invalid domain."""
        with pytest.raises(KeyError):
            matrix.get("InvalidDomain", "O")

    # PURPOSE: Test error on invalid axis
    def test_get_invalid_axis(self, matrix: PerspectiveMatrix):
        """Test error on invalid axis."""
        with pytest.raises(KeyError):
            matrix.get("Resource", "X")

    # PURPOSE: Verify all_perspectives returns 120 items
    def test_all_perspectives_count(self, matrix: PerspectiveMatrix):
        """Verify all_perspectives returns 120 items."""
        perspectives = matrix.all_perspectives()
        assert len(perspectives) == 480

    # PURPOSE: Verify all perspective IDs are unique
    def test_all_perspectives_unique(self, matrix: PerspectiveMatrix):
        """Verify all perspective IDs are unique."""
        perspectives = matrix.all_perspectives()
        ids = [p.id for p in perspectives]
        assert len(ids) == len(set(ids))  # No duplicates

    # PURPOSE: Test prompt generation
    def test_generate_prompt(self, matrix: PerspectiveMatrix):
        """Test prompt generation."""
        p = matrix.get("Security", "H1")
        prompt = matrix.generate_prompt(p)

        # Check prompt contains key elements
        assert "Security" in prompt
        assert "前感情" in prompt
        assert "Propatheia" in prompt
        assert "SILENCE" in prompt

    # PURPOSE: Test generating all 120 prompts
    def test_generate_all_prompts(self, matrix: PerspectiveMatrix):
        """Test generating all 120 prompts."""
        prompts = matrix.generate_all_prompts()
        assert len(prompts) == 480

        # Check all prompts are non-empty
        for pid, prompt in prompts.items():
            assert len(prompt) > 100, f"Prompt {pid} is too short"

    # PURPOSE: Test batching for rate limiting
    def test_batch_perspectives(self, matrix: PerspectiveMatrix):
        """Test batching for rate limiting."""
        batches = matrix.batch_perspectives(batch_size=60)
        assert len(batches) == 8
        assert len(batches[0]) == 60
        assert len(batches[1]) == 60


# PURPOSE: Tests for Perspective dataclass
class TestPerspective:
    """Tests for Perspective dataclass."""

    # PURPOSE: Test perspective ID generation
    def test_perspective_id(self):
        """Test perspective ID generation."""
        p = Perspective(
            domain_id="Test",
            domain_name="テスト",
            domain_description="テスト領域",
            domain_keywords=["test"],
            axis_id="O",
            axis_name="本質",
            axis_question="What?",
            axis_focus="Focus",
            theorem="O1 Noēsis",
        )
        assert p.id == "Test-O"
        assert p.name == "テスト × 本質"


# PURPOSE: Tests verifying structural orthogonality
class TestOrthogonality:
    """Tests verifying structural orthogonality."""

    # PURPOSE: matrix の処理
    @pytest.fixture
    def matrix(self) -> PerspectiveMatrix:
        """Verify matrix behavior."""
        return PerspectiveMatrix.load()

    # PURPOSE: Verify perspectives are exactly domains × axes
    def test_domain_axis_direct_product(self, matrix: PerspectiveMatrix):
        """Verify perspectives are exactly domains × axes."""
        expected = set()
        for d in matrix.domains:
            for a in matrix.axes:
                expected.add(f"{d}-{a}")

        actual = {p.id for p in matrix.all_perspectives()}

        assert expected == actual

    # PURPOSE: Verify no two perspectives can find the same issue
    def test_no_perspective_overlap(self, matrix: PerspectiveMatrix):
        """Verify no two perspectives can find the same issue."""
        perspectives = matrix.all_perspectives()

        # Each perspective has a unique (domain, axis) pair
        pairs = [(p.domain_id, p.axis_id) for p in perspectives]
        assert len(pairs) == len(set(pairs))

    # PURPOSE: Verify complete coverage: every cell in the matrix is filled
    def test_complete_coverage(self, matrix: PerspectiveMatrix):
        """Verify complete coverage: every cell in the matrix is filled."""
        perspectives = matrix.all_perspectives()

        # Create a coverage matrix
        coverage = {}
        for d in matrix.domains:
            coverage[d] = set()

        for p in perspectives:
            coverage[p.domain_id].add(p.axis_id)

        # Every domain should cover all axes
        for d, axes in coverage.items():
            assert axes == set(
                matrix.axes
            ), f"Domain {d} missing axes: {set(matrix.axes) - axes}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
