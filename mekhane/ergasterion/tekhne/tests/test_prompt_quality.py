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

class TestScorerAccuracy:
    """Good prompt should score high, bad prompt should score low."""

    def test_good_prompt_high_score(self):
        report = score_prompt(str(FIXTURES_DIR / "good_prompt.skill.md"))
        assert report.total >= 60, f"Good prompt scored too low: {report.total}/100"
        assert report.grade in ("S", "A", "B"), f"Expected grade A+ but got {report.grade}"

    def test_bad_prompt_low_score(self):
        report = score_prompt(str(FIXTURES_DIR / "bad_prompt.skill.md"))
        assert report.total < 40, f"Bad prompt scored too high: {report.total}/100"
        assert report.grade in ("D", "F"), f"Expected grade D/F but got {report.grade}"

    def test_medium_prompt_between(self):
        report = score_prompt(str(FIXTURES_DIR / "medium_prompt.prompt"))
        assert 30 <= report.total <= 85, (
            f"Medium prompt should be between 30-85, got {report.total}"
        )

    def test_good_beats_bad(self):
        good = score_prompt(str(FIXTURES_DIR / "good_prompt.skill.md"))
        bad = score_prompt(str(FIXTURES_DIR / "bad_prompt.skill.md"))
        assert good.total > bad.total, (
            f"Good ({good.total}) should beat Bad ({bad.total})"
        )

    def test_all_dimensions_non_negative(self):
        report = score_prompt(str(FIXTURES_DIR / "good_prompt.skill.md"))
        assert report.structure.normalized >= 0
        assert report.safety.normalized >= 0
        assert report.completeness.normalized >= 0
        assert report.archetype_fit.normalized >= 0


# ============================================================
# 2. Format Detection Tests
# ============================================================

class TestFormatDetection:
    """Format auto-detection should work correctly."""

    def test_detect_skill_format(self):
        content = Path(FIXTURES_DIR / "good_prompt.skill.md").read_text()
        assert detect_format(content) == "skill"

    def test_detect_prompt_format(self):
        content = Path(FIXTURES_DIR / "medium_prompt.prompt").read_text()
        assert detect_format(content) == "prompt"

    def test_detect_sage_format(self):
        sage_content = """<module_config>
  <name>test</name>
</module_config>
<instruction>test</instruction>"""
        assert detect_format(sage_content) == "sage"

    def test_detect_unknown_format(self):
        assert detect_format("Just some random text") == "unknown"

    def test_bad_prompt_detected(self):
        content = Path(FIXTURES_DIR / "bad_prompt.skill.md").read_text()
        # Bad prompt has no frontmatter, should be unknown
        fmt = detect_format(content)
        assert fmt in ("unknown", "skill")  # May detect as unknown


# ============================================================
# 3. Archetype Detection Tests
# ============================================================

class TestArchetypeDetection:
    """Archetype detection should identify the correct type."""

    def test_precision_archetype(self):
        content = "This prompt uses CoVe for verification and confidence estimation"
        assert detect_archetype(content) == "Precision"

    def test_safety_archetype(self):
        content = "Apply URIAL for safety, filter harmful content, injection防止"
        assert detect_archetype(content) == "Safety"

    def test_autonomy_archetype(self):
        content = "Use ReAct agent loop with Reflexion for autonomous execution"
        assert detect_archetype(content) == "Autonomy"

    def test_no_archetype(self):
        content = "Simple text with no technical keywords"
        result = detect_archetype(content)
        assert result is None


# ============================================================
# 4. Frontmatter Extraction Tests
# ============================================================

class TestFrontmatter:

    def test_valid_frontmatter(self):
        content = "---\nname: Test\ndescription: Hello\n---\nContent here"
        fm = extract_frontmatter(content)
        assert fm.get("name") == "Test"
        assert fm.get("description") == "Hello"

    def test_missing_frontmatter(self):
        content = "No frontmatter here"
        fm = extract_frontmatter(content)
        assert fm == {}


# ============================================================
# 5. Format Conversion Tests
# ============================================================

class TestFormatConversion:
    """Format converter should produce valid output."""

    def test_skill_to_prompt(self):
        from format_converter import convert
        result = convert(str(FIXTURES_DIR / "good_prompt.skill.md"), "prompt")
        assert "#prompt" in result
        assert "@goal:" in result

    def test_skill_to_sage(self):
        from format_converter import convert
        result = convert(str(FIXTURES_DIR / "good_prompt.skill.md"), "sage")
        assert "<module_config>" in result
        assert "<instruction>" in result

    def test_prompt_to_skill(self):
        from format_converter import convert
        result = convert(str(FIXTURES_DIR / "medium_prompt.prompt"), "skill")
        assert "---" in result
        assert "## Overview" in result

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

class TestSelfRefinePipeline:
    """Self-refine pipeline should produce improvement suggestions."""

    def test_static_refine_pass(self):
        from self_refine_pipeline import static_refine
        result = static_refine(
            str(FIXTURES_DIR / "good_prompt.skill.md"), threshold=30
        )
        # Good prompt should pass a low threshold
        assert result["status"] in ("pass", "needs_improvement")

    def test_static_refine_fail(self):
        from self_refine_pipeline import static_refine
        result = static_refine(
            str(FIXTURES_DIR / "bad_prompt.skill.md"), threshold=80
        )
        assert result["status"] == "needs_improvement"
        assert len(result["suggestions"]) > 0

    def test_suggestions_sorted_by_impact(self):
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

class TestRegression:
    """Existing SKILL.md files should score above minimum threshold."""

    SKILLS_GLOB = str(PROJECT_ROOT / ".agent" / "skills" / "*" / "SKILL.md")
    MIN_SCORE = 10  # Very lenient — just ensure they don't crash

    @pytest.fixture
    def skill_files(self):
        files = sorted(glob.glob(self.SKILLS_GLOB))
        if not files:
            pytest.skip("No SKILL.md files found")
        return files

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
