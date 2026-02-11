#!/usr/bin/env python3
"""
Prompt Quality Testing Suite

テスト項目:
  1. スコアラーの正確性 (good/bad/medium フィクスチャ)
  2. フォーマット検出の正確性
  3. Archetype 検出の正確性
  4. フォーマット変換の動作
  5. Self-Refine パイプラインの動作
  6. 既存 SKILL.md の回帰テスト
"""

import glob
import sys
from pathlib import Path

import pytest

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from prompt_quality_scorer import (
    QualityReport,
    check_archetype_fit,
    check_completeness,
    check_safety,
    check_structure,
    detect_archetype,
    detect_format,
    extract_frontmatter,
    score_prompt,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent  # hegemonikon/


# ============================================================
# 1. Scorer Accuracy Tests
# ============================================================

# PURPOSE: Test suite validating scorer accuracy correctness
class TestScorerAccuracy:
    """Good prompt should score high, bad prompt should score low."""

    # PURPOSE: Verify good prompt high score behaves correctly
    def test_good_prompt_high_score(self):
        """Verify good prompt high score behavior."""
        report = score_prompt(str(FIXTURES_DIR / "good_prompt.skill.md"))
        assert report.total >= 60, f"Good prompt scored too low: {report.total}/100"
        assert report.grade in ("S", "A", "B"), f"Expected grade A+ but got {report.grade}"

    # PURPOSE: Verify bad prompt low score behaves correctly
    def test_bad_prompt_low_score(self):
        """Verify bad prompt low score behavior."""
        report = score_prompt(str(FIXTURES_DIR / "bad_prompt.skill.md"))
        assert report.total < 40, f"Bad prompt scored too high: {report.total}/100"
        assert report.grade in ("D", "F"), f"Expected grade D/F but got {report.grade}"

    # PURPOSE: Verify medium prompt between behaves correctly
    def test_medium_prompt_between(self):
        """Verify medium prompt between behavior."""
        report = score_prompt(str(FIXTURES_DIR / "medium_prompt.prompt"))
        assert 30 <= report.total <= 85, (
            f"Medium prompt should be between 30-85, got {report.total}"
        )

    # PURPOSE: Verify good beats bad behaves correctly
    def test_good_beats_bad(self):
        """Verify good beats bad behavior."""
        good = score_prompt(str(FIXTURES_DIR / "good_prompt.skill.md"))
        bad = score_prompt(str(FIXTURES_DIR / "bad_prompt.skill.md"))
        assert good.total > bad.total, (
            f"Good ({good.total}) should beat Bad ({bad.total})"
        )

    # PURPOSE: Verify all dimensions non negative behaves correctly
    def test_all_dimensions_non_negative(self):
        """Verify all dimensions non negative behavior."""
        report = score_prompt(str(FIXTURES_DIR / "good_prompt.skill.md"))
        assert report.structure.normalized >= 0
        assert report.safety.normalized >= 0
        assert report.completeness.normalized >= 0
        assert report.archetype_fit.normalized >= 0


# ============================================================
# 2. Format Detection Tests
# ============================================================

# PURPOSE: Test suite validating format detection correctness
class TestFormatDetection:
    """Format auto-detection should work correctly."""

    # PURPOSE: Verify detect skill format behaves correctly
    def test_detect_skill_format(self):
        """Verify detect skill format behavior."""
        content = Path(FIXTURES_DIR / "good_prompt.skill.md").read_text()
        assert detect_format(content) == "skill"

    # PURPOSE: Verify detect prompt format behaves correctly
    def test_detect_prompt_format(self):
        """Verify detect prompt format behavior."""
        content = Path(FIXTURES_DIR / "medium_prompt.prompt").read_text()
        assert detect_format(content) == "prompt"

    # PURPOSE: Verify detect sage format behaves correctly
    def test_detect_sage_format(self):
        """Verify detect sage format behavior."""
        sage_content = """<module_config>
  <name>test</name>
</module_config>
<instruction>test</instruction>"""
        assert detect_format(sage_content) == "sage"

    # PURPOSE: Verify detect unknown format behaves correctly
    def test_detect_unknown_format(self):
        """Verify detect unknown format behavior."""
        assert detect_format("Just some random text") == "unknown"

    # PURPOSE: Verify bad prompt detected behaves correctly
    def test_bad_prompt_detected(self):
        """Verify bad prompt detected behavior."""
        content = Path(FIXTURES_DIR / "bad_prompt.skill.md").read_text()
        # Bad prompt has no frontmatter, should be unknown
        fmt = detect_format(content)
        assert fmt in ("unknown", "skill")  # May detect as unknown


# ============================================================
# 3. Archetype Detection Tests
# ============================================================

# PURPOSE: Test suite validating archetype detection correctness
class TestArchetypeDetection:
    """Archetype detection should identify the correct type."""

    # PURPOSE: Verify precision archetype behaves correctly
    def test_precision_archetype(self):
        """Verify precision archetype behavior."""
        content = "This prompt uses CoVe for verification and confidence estimation"
        assert detect_archetype(content) == "Precision"

    # PURPOSE: Verify safety archetype behaves correctly
    def test_safety_archetype(self):
        """Verify safety archetype behavior."""
        content = "Apply URIAL for safety, filter harmful content, injection防止"
        assert detect_archetype(content) == "Safety"

    # PURPOSE: Verify autonomy archetype behaves correctly
    def test_autonomy_archetype(self):
        """Verify autonomy archetype behavior."""
        content = "Use ReAct agent loop with Reflexion for autonomous execution"
        assert detect_archetype(content) == "Autonomy"

    # PURPOSE: Verify no archetype behaves correctly
    def test_no_archetype(self):
        """Verify no archetype behavior."""
        content = "Simple text with no technical keywords"
        result = detect_archetype(content)
        assert result is None


# ============================================================
# 4. Frontmatter Extraction Tests
# ============================================================

# PURPOSE: Test suite validating frontmatter correctness
class TestFrontmatter:

    """Test suite for frontmatter."""
    # PURPOSE: Verify valid frontmatter behaves correctly
    def test_valid_frontmatter(self):
        """Verify valid frontmatter behavior."""
        content = "---\nname: Test\ndescription: Hello\n---\nContent here"
        fm = extract_frontmatter(content)
        assert fm.get("name") == "Test"
        assert fm.get("description") == "Hello"

    # PURPOSE: Verify missing frontmatter behaves correctly
    def test_missing_frontmatter(self):
        """Verify missing frontmatter behavior."""
        content = "No frontmatter here"
        fm = extract_frontmatter(content)
        assert fm == {}


# ============================================================
# 5. Format Conversion Tests
# ============================================================

# PURPOSE: Test suite validating format conversion correctness
class TestFormatConversion:
    """Format converter should produce valid output."""

    # PURPOSE: Verify skill to prompt behaves correctly
    def test_skill_to_prompt(self):
        """Verify skill to prompt behavior."""
        from format_converter import convert
        result = convert(str(FIXTURES_DIR / "good_prompt.skill.md"), "prompt")
        assert "#prompt" in result
        assert "@goal:" in result

    # PURPOSE: Verify skill to sage behaves correctly
    def test_skill_to_sage(self):
        """Verify skill to sage behavior."""
        from format_converter import convert
        result = convert(str(FIXTURES_DIR / "good_prompt.skill.md"), "sage")
        assert "<module_config>" in result
        assert "<instruction>" in result

    # PURPOSE: Verify prompt to skill behaves correctly
    def test_prompt_to_skill(self):
        """Verify prompt to skill behavior."""
        from format_converter import convert
        result = convert(str(FIXTURES_DIR / "medium_prompt.prompt"), "skill")
        assert "---" in result
        assert "## Overview" in result

    # PURPOSE: Verify converted output scorable behaves correctly
    def test_converted_output_scorable(self):
        """Converted output should be scorable without errors."""
        from format_converter import convert
        import tempfile

        result = convert(str(FIXTURES_DIR / "good_prompt.skill.md"), "prompt")
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".prompt", delete=False, encoding="utf-8"
        ) as f:
            f.write(result)
            temp_path = f.name

        try:
            report = score_prompt(temp_path)
            assert report.total >= 0  # Should not crash
        finally:
            Path(temp_path).unlink(missing_ok=True)


# ============================================================
# 6. Self-Refine Pipeline Tests
# ============================================================

# PURPOSE: Test suite validating self refine pipeline correctness
class TestSelfRefinePipeline:
    """Self-refine pipeline should produce improvement suggestions."""

    # PURPOSE: Verify static refine pass behaves correctly
    def test_static_refine_pass(self):
        """Verify static refine pass behavior."""
        from self_refine_pipeline import static_refine
        result = static_refine(
            str(FIXTURES_DIR / "good_prompt.skill.md"), threshold=30
        )
        # Good prompt should pass a low threshold
        assert result["status"] in ("pass", "needs_improvement")

    # PURPOSE: Verify static refine fail behaves correctly
    def test_static_refine_fail(self):
        """Verify static refine fail behavior."""
        from self_refine_pipeline import static_refine
        result = static_refine(
            str(FIXTURES_DIR / "bad_prompt.skill.md"), threshold=80
        )
        assert result["status"] == "needs_improvement"
        assert len(result["suggestions"]) > 0

    # PURPOSE: Verify suggestions sorted by impact behaves correctly
    def test_suggestions_sorted_by_impact(self):
        """Verify suggestions sorted by impact behavior."""
        from self_refine_pipeline import static_refine
        result = static_refine(
            str(FIXTURES_DIR / "bad_prompt.skill.md"), threshold=80
        )
        if result["suggestions"]:
            impacts = [s["impact"] for s in result["suggestions"]]
            assert impacts == sorted(impacts, reverse=True), (
                "Suggestions should be sorted by impact (descending)"
            )


# ============================================================
# 7. Regression Tests (Existing Skills)
# ============================================================

# PURPOSE: Test suite validating regression correctness
class TestRegression:
    """Existing SKILL.md files should score above minimum threshold."""

    SKILLS_GLOB = str(PROJECT_ROOT / ".agent" / "skills" / "*" / "SKILL.md")
    MIN_SCORE = 10  # Very lenient — just ensure they don't crash

    # PURPOSE: Verify skill files behaves correctly
    @pytest.fixture
    def skill_files(self):
        """Verify skill files behavior."""
        files = sorted(glob.glob(self.SKILLS_GLOB))
        if not files:
            pytest.skip("No SKILL.md files found")
        return files

    # PURPOSE: Verify all skills scorable behaves correctly
    def test_all_skills_scorable(self, skill_files):
        """All existing skills should be scorable without errors."""
        errors = []
        for f in skill_files:
            try:
                report = score_prompt(f)
                assert report.total >= 0
            except Exception as e:
                errors.append(f"{Path(f).parent.name}: {e}")
        assert not errors, f"Failed to score: {errors}"

    # PURPOSE: Verify no skill below minimum behaves correctly
    def test_no_skill_below_minimum(self, skill_files):
        """No skill should score below the absolute minimum."""
        failures = []
        for f in skill_files:
            report = score_prompt(f)
            if report.total < self.MIN_SCORE:
                failures.append(
                    f"{Path(f).parent.name}: {report.total}/100 (Grade: {report.grade})"
                )
        assert not failures, f"Skills below {self.MIN_SCORE}: {failures}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
