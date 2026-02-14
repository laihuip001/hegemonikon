# PROOF: [L3/テスト] <- mekhane/symploke/tests/ 対象モジュールが存在→検証が必要→test_generate_prompt が担う
#!/usr/bin/env python3
"""
Tests for generate_prompt with dynamic project context loading.

Run with:
    .venv/bin/python -m pytest mekhane/symploke/tests/test_generate_prompt.py -v
"""

import pytest
from unittest.mock import patch
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mekhane.symploke.specialist_v2 import (
    Specialist,
    Archetype,
    VerdictFormat,
    Severity,
    generate_prompt,
    _load_project_context,
    _get_project_context,
)


# PURPOSE: Sample specialist for testing
SAMPLE_SPECIALIST = Specialist(
    id="TEST-001",
    name="テスト専門家",
    category="test",
    archetype=Archetype.PRECISION,
    domain="テスト領域",
    principle="テストは証明、証明はテスト",
    perceives=["問題パターンA", "問題パターンB"],
    blind_to=["無関係な領域"],
    measure="全テストが通過",
    verdict=VerdictFormat.REVIEW,
    severity_map={"パターンA": Severity.HIGH},
)


# PURPOSE: Test suite for generate_prompt with project context
class TestGeneratePromptContext:
    """Test dynamic context loading in generate_prompt."""

    # PURPOSE: Test that generated prompt contains Project Context section
    def test_prompt_contains_project_context(self) -> None:
        """Verify prompt includes Project Context section."""
        prompt = generate_prompt(SAMPLE_SPECIALIST, "example.py")
        assert "Project Context" in prompt
        assert "理解してから分析すること" in prompt

    # PURPOSE: Test that AGENTS.md content is loaded into prompt
    def test_prompt_loads_agents_md(self) -> None:
        """Verify AGENTS.md content appears in generated prompt."""
        prompt = generate_prompt(SAMPLE_SPECIALIST, "example.py")
        # AGENTS.md v5 should contain these terms
        assert "Hegemonikon" in prompt or "hegemonikon" in prompt.lower()

    # PURPOSE: Test that context includes design principles
    def test_prompt_includes_design_principles(self) -> None:
        """Verify design principles from context files are present."""
        prompt = generate_prompt(SAMPLE_SPECIALIST, "example.py")
        # hgk_knowledge.md contains design principles
        assert "PURPOSE" in prompt

    # PURPOSE: Test specialist identity is preserved
    def test_specialist_identity_preserved(self) -> None:
        """Verify specialist-specific fields are in the prompt."""
        prompt = generate_prompt(SAMPLE_SPECIALIST, "example.py")
        assert "TEST-001" in prompt
        assert "テスト専門家" in prompt
        assert "テスト領域" in prompt
        assert "テストは証明" in prompt

    # PURPOSE: Test perceives and blind_to sections
    def test_perceives_and_blind_to(self) -> None:
        """Verify perceives and blind_to lists are rendered."""
        prompt = generate_prompt(SAMPLE_SPECIALIST, "example.py")
        assert "問題パターンA" in prompt
        assert "問題パターンB" in prompt
        assert "無関係な領域" in prompt

    # PURPOSE: Test output format section
    def test_output_format(self) -> None:
        """Verify output format instructions are present."""
        prompt = generate_prompt(SAMPLE_SPECIALIST, "example.py")
        assert "Output Format" in prompt
        assert "REVIEW" in prompt


# PURPOSE: Test _load_project_context directly
class TestLoadProjectContext:
    """Test the context loading function."""

    # PURPOSE: Test loading from real files
    def test_loads_real_files(self) -> None:
        """Verify real AGENTS.md and context files are loaded."""
        context = _load_project_context()
        assert len(context) > 100  # Should have substantial content
        assert "Hegemonikon" in context or "hegemonikon" in context.lower()

    # PURPOSE: Test fallback when directory missing
    def test_fallback_on_missing_dir(self) -> None:
        """Verify fallback context when context_dir is missing."""
        context = _load_project_context(context_dir="nonexistent/path")
        # Should still have AGENTS.md content
        assert len(context) > 50

    # PURPOSE: Test caching works
    def test_caching(self) -> None:
        """Verify context is cached after first load."""
        # Reset cache
        import mekhane.symploke.specialist_v2 as mod
        mod._PROJECT_CONTEXT_CACHE = None

        ctx1 = _get_project_context()
        ctx2 = _get_project_context()
        assert ctx1 is ctx2  # Same object (cached)

        # Reset cache for other tests
        mod._PROJECT_CONTEXT_CACHE = None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
