#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/ccl/tests/
# PURPOSE: CCL Guardrails, DoxaLearner, SemanticValidator の包括テスト
"""CCL Module Tests — Batch 3"""

import json
import pytest
from pathlib import Path

from mekhane.ccl.guardrails.validators import (
    ValidationError,
    ValidationResult,
    CCLOutputValidator,
    OPERATOR_REQUIRED_SECTIONS,
    OPERATOR_MIN_LINES,
)
from mekhane.ccl.doxa_learner import DoxaLearner, LearnedPattern
from mekhane.ccl.semantic_validator import (
    SemanticResult,
    CCLSemanticValidator,
)


# ═══ ValidationError ═══════════════════

# PURPOSE: Test suite validating validation error correctness
class TestValidationError:
    """検証エラーデータクラスのテスト"""

    # PURPOSE: Verify create behaves correctly
    def test_create(self):
        """Verify create behavior."""
        e = ValidationError(
            operator="!",
            error_type="必須セクション欠落",
            message="Test error",
            suggestion="Fix this",
        )
        assert e.operator == "!"
        assert e.error_type == "必須セクション欠落"


# ═══ ValidationResult ══════════════════

# PURPOSE: Test suite validating validation result correctness
class TestValidationResult:
    """検証結果データクラスのテスト"""

    # PURPOSE: Verify valid behaves correctly
    def test_valid(self):
        """Verify valid behavior."""
        r = ValidationResult(valid=True, errors=[], warnings=[])
        assert r.valid is True

    # PURPOSE: Verify invalid behaves correctly
    def test_invalid(self):
        """Verify invalid behavior."""
        r = ValidationResult(
            valid=False,
            errors=[
                ValidationError("!", "test", "msg", "sug")
            ],
            warnings=[],
        )
        assert r.valid is False

    # PURPOSE: Verify regeneration instruction valid behaves correctly
    def test_regeneration_instruction_valid(self):
        """Verify regeneration instruction valid behavior."""
        r = ValidationResult(valid=True, errors=[], warnings=[])
        assert r.regeneration_instruction == ""

    # PURPOSE: Verify regeneration instruction invalid behaves correctly
    def test_regeneration_instruction_invalid(self):
        """Verify regeneration instruction invalid behavior."""
        r = ValidationResult(
            valid=False,
            errors=[ValidationError("!", "test_type", "test_msg", "test_sug")],
            warnings=[],
        )
        instr = r.regeneration_instruction
        assert "再生成" in instr
        assert "test_type" in instr


# ═══ CCLOutputValidator ════════════════

# PURPOSE: Test suite validating c c l output validator correctness
class TestCCLOutputValidator:
    """CCL 出力検証器のテスト"""

    # PURPOSE: Verify validator behaves correctly
    @pytest.fixture
    def validator(self):
        """Verify validator behavior."""
        return CCLOutputValidator()

    # ── parse_operators ──
    # PURPOSE: Verify parse factorial behaves correctly
    def test_parse_factorial(self, validator):
        """Verify parse factorial behavior."""
        ops = validator.parse_operators("/noe!")
        assert "!" in ops

    # PURPOSE: Verify parse oscillation behaves correctly
    def test_parse_oscillation(self, validator):
        """Verify parse oscillation behavior."""
        ops = validator.parse_operators("/noe~/dia")
        assert "~" in ops

    # PURPOSE: Verify parse merge behaves correctly
    def test_parse_merge(self, validator):
        """Verify parse merge behavior."""
        ops = validator.parse_operators("/noe*/dia")
        assert "*" in ops

    # PURPOSE: Verify parse meta behaves correctly
    def test_parse_meta(self, validator):
        """Verify parse meta behavior."""
        ops = validator.parse_operators("/noe^")
        assert "^" in ops

    # PURPOSE: Verify parse deepen behaves correctly
    def test_parse_deepen(self, validator):
        """Verify parse deepen behavior."""
        ops = validator.parse_operators("/noe+")
        assert "+" in ops

    # PURPOSE: Verify parse multiple behaves correctly
    def test_parse_multiple(self, validator):
        """Verify parse multiple behavior."""
        ops = validator.parse_operators("/noe!~/u+")
        assert "!" in ops
        assert "~" in ops
        assert "+" in ops

    # PURPOSE: Verify parse no operators behaves correctly
    def test_parse_no_operators(self, validator):
        """Verify parse no operators behavior."""
        ops = validator.parse_operators("/noe")
        assert len(ops) == 0

    # ── check_required_sections ──
    # PURPOSE: Verify factorial missing sections behaves correctly
    def test_factorial_missing_sections(self, validator):
        """Verify factorial missing sections behavior."""
        errors = validator.check_required_sections("Short output", {"!"})
        assert len(errors) > 0

    # PURPOSE: Verify factorial with sections behaves correctly
    def test_factorial_with_sections(self, validator):
        """Verify factorial with sections behavior."""
        output = "## 全派生\n派生リスト\n同時実行"
        errors = validator.check_required_sections(output, {"!"})
        assert len(errors) == 0

    # PURPOSE: Verify oscillation missing behaves correctly
    def test_oscillation_missing(self, validator):
        """Verify oscillation missing behavior."""
        errors = validator.check_required_sections("No oscillation", {"~"})
        assert len(errors) > 0

    # PURPOSE: Verify oscillation with arrow behaves correctly
    def test_oscillation_with_arrow(self, validator):
        """Verify oscillation with arrow behavior."""
        output = "## 振動\n←→ 分析"
        errors = validator.check_required_sections(output, {"~"})
        assert len(errors) == 0

    # PURPOSE: Verify meta with sections behaves correctly
    def test_meta_with_sections(self, validator):
        """Verify meta with sections behavior."""
        output = "## メタ分析"
        errors = validator.check_required_sections(output, {"^"})
        assert len(errors) == 0

    # ── check_minimum_length ──
    # PURPOSE: Verify too short for factorial behaves correctly
    def test_too_short_for_factorial(self, validator):
        """Verify too short for factorial behavior."""
        output = "Line\n" * 5  # 5 lines < 20 min
        errors = validator.check_minimum_length(output, {"!"})
        assert len(errors) > 0

    # PURPOSE: Verify long enough for meta behaves correctly
    def test_long_enough_for_meta(self, validator):
        """Verify long enough for meta behavior."""
        output = "Line\n" * 15  # 15 lines >= 10 min
        errors = validator.check_minimum_length(output, {"^"})
        assert len(errors) == 0

    # ── check_operator_understanding ──
    # PURPOSE: Verify no understanding behaves correctly
    def test_no_understanding(self, validator):
        """Verify no understanding behavior."""
        errors = validator.check_operator_understanding("Just text", {"!"})
        assert len(errors) > 0

    # PURPOSE: Verify with understanding behaves correctly
    def test_with_understanding(self, validator):
        """Verify with understanding behavior."""
        output = "## 理解確認\n演算子の意味を確認しました"
        errors = validator.check_operator_understanding(output, {"!"})
        assert len(errors) == 0

    # ── validate (integration) ──
    # PURPOSE: Verify validate bad output behaves correctly
    def test_validate_bad_output(self, validator):
        """Verify validate bad output behavior."""
        result = validator.validate("Short.", "/noe!~/u+")
        assert result.valid is False
        assert len(result.errors) > 0

    # PURPOSE: Verify validate good output behaves correctly
    def test_validate_good_output(self, validator):
        """Verify validate good output behavior."""
        output = "\n".join([
            "## 全派生", "派生リスト", "同時実行",
            "## 振動", "← A", "→ B", "↔ 対話",
            "## 詳細展開",
            "## 理解確認", "A: 演算子を確認しました",
            "自己監査",
        ] + [f"Line {i}" for i in range(25)])
        result = validator.validate(output, "/noe!~/u+")
        # Should pass most checks
        assert isinstance(result, ValidationResult)

    # PURPOSE: Verify validate warnings behaves correctly
    def test_validate_warnings(self, validator):
        """Verify validate warnings behavior."""
        result = validator.validate("short text", "/noe")
        # Should have warning about short output
        assert len(result.warnings) >= 1


# ═══ OPERATOR constants ═══════════════

# PURPOSE: Test suite validating operator constants correctness
class TestOperatorConstants:
    """演算子定数のテスト"""

    # PURPOSE: Verify required sections factorial behaves correctly
    def test_required_sections_factorial(self):
        """Verify required sections factorial behavior."""
        assert "!" in OPERATOR_REQUIRED_SECTIONS

    # PURPOSE: Verify required sections oscillation behaves correctly
    def test_required_sections_oscillation(self):
        """Verify required sections oscillation behavior."""
        assert "~" in OPERATOR_REQUIRED_SECTIONS

    # PURPOSE: Verify required sections merge behaves correctly
    def test_required_sections_merge(self):
        """Verify required sections merge behavior."""
        assert "*" in OPERATOR_REQUIRED_SECTIONS

    # PURPOSE: Verify min lines factorial behaves correctly
    def test_min_lines_factorial(self):
        """Verify min lines factorial behavior."""
        assert OPERATOR_MIN_LINES["!"] >= 10

    # PURPOSE: Verify min lines oscillation behaves correctly
    def test_min_lines_oscillation(self):
        """Verify min lines oscillation behavior."""
        assert OPERATOR_MIN_LINES["~"] >= 10


# ═══ LearnedPattern ════════════════════

# PURPOSE: Test suite validating learned pattern correctness
class TestLearnedPattern:
    """学習パターンデータクラスのテスト"""

    # PURPOSE: Verify create behaves correctly
    def test_create(self):
        """Verify create behavior."""
        p = LearnedPattern(
            intent="分析して", ccl="/s+", confidence=0.8, usage_count=1
        )
        assert p.intent == "分析して"
        assert p.confidence == 0.8


# ═══ DoxaLearner ═══════════════════════

# PURPOSE: Test suite validating doxa learner correctness
class TestDoxaLearner:
    """Doxa パターン学習のテスト"""

    # PURPOSE: Verify learner behaves correctly
    @pytest.fixture
    def learner(self, tmp_path):
        """Verify learner behavior."""
        return DoxaLearner(store_path=tmp_path / "patterns.json")

    # PURPOSE: Verify init empty behaves correctly
    def test_init_empty(self, learner):
        """Verify init empty behavior."""
        assert len(learner.patterns) == 0

    # PURPOSE: Verify record behaves correctly
    def test_record(self, learner):
        """Verify record behavior."""
        learner.record("分析してください", "/s+")
        assert len(learner.patterns) == 1

    # PURPOSE: Verify record persists behaves correctly
    def test_record_persists(self, learner, tmp_path):
        """Verify record persists behavior."""
        learner.record("分析", "/s+")
        # Load fresh
        learner2 = DoxaLearner(store_path=tmp_path / "patterns.json")
        assert len(learner2.patterns) == 1

    # PURPOSE: Verify record reinforce behaves correctly
    def test_record_reinforce(self, learner):
        """Verify record reinforce behavior."""
        learner.record("分析", "/s+")
        learner.record("分析", "/s+")
        assert learner.patterns[0].usage_count == 2
        assert learner.patterns[0].confidence > 0.8

    # PURPOSE: Verify record update ccl behaves correctly
    def test_record_update_ccl(self, learner):
        """Verify record update ccl behavior."""
        learner.record("分析", "/s+")
        learner.record("分析", "/s-")
        assert learner.patterns[0].ccl == "/s-"

    # PURPOSE: Verify lookup exact behaves correctly
    def test_lookup_exact(self, learner):
        """Verify lookup exact behavior."""
        learner.record("分析してください", "/s+")
        result = learner.lookup("分析してください")
        assert result == "/s+"

    # PURPOSE: Verify lookup substring behaves correctly
    def test_lookup_substring(self, learner):
        """Verify lookup substring behavior."""
        learner.record("詳しく分析してください", "/s+")
        result = learner.lookup("分析してください")
        assert result == "/s+"

    # PURPOSE: Verify lookup no match behaves correctly
    def test_lookup_no_match(self, learner):
        """Verify lookup no match behavior."""
        learner.record("分析", "/s+")
        result = learner.lookup("xyz random text")
        assert result is None

    # PURPOSE: Verify get stats empty behaves correctly
    def test_get_stats_empty(self, learner):
        """Verify get stats empty behavior."""
        stats = learner.get_stats()
        assert stats["count"] == 0

    # PURPOSE: Verify get stats behaves correctly
    def test_get_stats(self, learner):
        """Verify get stats behavior."""
        learner.record("分析", "/s+")
        learner.record("判定", "/dia")
        stats = learner.get_stats()
        assert stats["count"] == 2
        assert stats["total_usage"] == 2
        assert 0 < stats["avg_confidence"] <= 1.0

    # PURPOSE: Verify multiple patterns behaves correctly
    def test_multiple_patterns(self, learner):
        """Verify multiple patterns behavior."""
        learner.record("分析", "/s+")
        learner.record("判定", "/dia")
        learner.record("実行", "/ene")
        assert len(learner.patterns) == 3


# ═══ SemanticResult ════════════════════

# PURPOSE: Test suite validating semantic result correctness
class TestSemanticResult:
    """意味的検証結果のテスト"""

    # PURPOSE: Verify aligned truthy behaves correctly
    def test_aligned_truthy(self):
        """Verify aligned truthy behavior."""
        r = SemanticResult(
            aligned=True, confidence=0.9, reasoning="OK", suggestions=[]
        )
        assert bool(r) is True

    # PURPOSE: Verify not aligned falsy behaves correctly
    def test_not_aligned_falsy(self):
        """Verify not aligned falsy behavior."""
        r = SemanticResult(
            aligned=False, confidence=0.1, reasoning="Bad", suggestions=["fix"]
        )
        assert bool(r) is False


# ═══ CCLSemanticValidator ══════════════

# PURPOSE: Test suite validating c c l semantic validator correctness
class TestCCLSemanticValidator:
    """意味的検証器のテスト"""

    # PURPOSE: Verify validator behaves correctly
    @pytest.fixture
    def validator(self):
        """Verify validator behavior."""
        return CCLSemanticValidator()

    # PURPOSE: Verify init behaves correctly
    def test_init(self, validator):
        """Verify init behavior."""
        assert validator.model_name == "gemini-2.0-flash"

    # PURPOSE: Verify default prompt behaves correctly
    def test_default_prompt(self, validator):
        """Verify default prompt behavior."""
        prompt = validator._default_prompt()
        assert "CCL" in prompt

    # PURPOSE: Verify build prompt behaves correctly
    def test_build_prompt(self, validator):
        """Verify build prompt behavior."""
        prompt = validator._build_prompt("分析して", "/s+", None)
        assert "分析して" in prompt
        assert "/s+" in prompt

    # PURPOSE: Verify build prompt with context behaves correctly
    def test_build_prompt_with_context(self, validator):
        """Verify build prompt with context behavior."""
        prompt = validator._build_prompt("分析", "/s", "コンテキスト情報")
        assert "コンテキスト" in prompt

    # PURPOSE: Verify parse response json behaves correctly
    def test_parse_response_json(self, validator):
        """Verify parse response json behavior."""
        response = '```json\n{"aligned": true, "confidence": 0.95, "reasoning": "Good match", "suggestions": []}\n```'
        result = validator._parse_response(response)
        assert result.aligned is True
        assert result.confidence == 0.95

    # PURPOSE: Verify parse response plain json behaves correctly
    def test_parse_response_plain_json(self, validator):
        """Verify parse response plain json behavior."""
        response = '{"aligned": false, "confidence": 0.3, "reasoning": "Bad", "suggestions": ["fix"]}'
        result = validator._parse_response(response)
        assert result.aligned is False
        assert len(result.suggestions) == 1

    # PURPOSE: Verify parse response fallback behaves correctly
    def test_parse_response_fallback(self, validator):
        """Verify parse response fallback behavior."""
        response = "This expression is aligned with the intent."
        result = validator._parse_response(response)
        assert isinstance(result, SemanticResult)

    # PURPOSE: Verify validate without llm behaves correctly
    def test_validate_without_llm(self, validator):
        """Verify validate without llm behavior."""
        result = validator.validate("分析して", "/s+")
        # Without API key, should gracefully degrade
        assert result.aligned is True  # Graceful degradation
        assert result.confidence == 0.0  # No confidence without LLM
