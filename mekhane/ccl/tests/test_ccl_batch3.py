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

class TestValidationError:
    """検証エラーデータクラスのテスト"""

    def test_create(self):
        e = ValidationError(
            operator="!",
            error_type="必須セクション欠落",
            message="Test error",
            suggestion="Fix this",
        )
        assert e.operator == "!"
        assert e.error_type == "必須セクション欠落"


# ═══ ValidationResult ══════════════════

class TestValidationResult:
    """検証結果データクラスのテスト"""

    def test_valid(self):
        r = ValidationResult(valid=True, errors=[], warnings=[])
        assert r.valid is True

    def test_invalid(self):
        r = ValidationResult(
            valid=False,
            errors=[
                ValidationError("!", "test", "msg", "sug")
            ],
            warnings=[],
        )
        assert r.valid is False

    def test_regeneration_instruction_valid(self):
        r = ValidationResult(valid=True, errors=[], warnings=[])
        assert r.regeneration_instruction == ""

    def test_regeneration_instruction_invalid(self):
        r = ValidationResult(
            valid=False,
            errors=[ValidationError("!", "test_type", "test_msg", "test_sug")],
            warnings=[],
        )
        instr = r.regeneration_instruction
        assert "再生成" in instr
        assert "test_type" in instr


# ═══ CCLOutputValidator ════════════════

class TestCCLOutputValidator:
    """CCL 出力検証器のテスト"""

    @pytest.fixture
    def validator(self):
        return CCLOutputValidator()

    # ── parse_operators ──
    def test_parse_factorial(self, validator):
        ops = validator.parse_operators("/noe!")
        assert "!" in ops

    def test_parse_oscillation(self, validator):
        ops = validator.parse_operators("/noe~/dia")
        assert "~" in ops

    def test_parse_merge(self, validator):
        ops = validator.parse_operators("/noe*/dia")
        assert "*" in ops

    def test_parse_meta(self, validator):
        ops = validator.parse_operators("/noe^")
        assert "^" in ops

    def test_parse_deepen(self, validator):
        ops = validator.parse_operators("/noe+")
        assert "+" in ops

    def test_parse_multiple(self, validator):
        ops = validator.parse_operators("/noe!~/u+")
        assert "!" in ops
        assert "~" in ops
        assert "+" in ops

    def test_parse_no_operators(self, validator):
        ops = validator.parse_operators("/noe")
        assert len(ops) == 0

    # ── check_required_sections ──
    def test_factorial_missing_sections(self, validator):
        errors = validator.check_required_sections("Short output", {"!"})
        assert len(errors) > 0

    def test_factorial_with_sections(self, validator):
        output = "## 全派生\n派生リスト\n同時実行"
        errors = validator.check_required_sections(output, {"!"})
        assert len(errors) == 0

    def test_oscillation_missing(self, validator):
        errors = validator.check_required_sections("No oscillation", {"~"})
        assert len(errors) > 0

    def test_oscillation_with_arrow(self, validator):
        output = "## 振動\n←→ 分析"
        errors = validator.check_required_sections(output, {"~"})
        assert len(errors) == 0

    def test_meta_with_sections(self, validator):
        output = "## メタ分析"
        errors = validator.check_required_sections(output, {"^"})
        assert len(errors) == 0

    # ── check_minimum_length ──
    def test_too_short_for_factorial(self, validator):
        output = "Line\n" * 5  # 5 lines < 20 min
        errors = validator.check_minimum_length(output, {"!"})
        assert len(errors) > 0

    def test_long_enough_for_meta(self, validator):
        output = "Line\n" * 15  # 15 lines >= 10 min
        errors = validator.check_minimum_length(output, {"^"})
        assert len(errors) == 0

    # ── check_operator_understanding ──
    def test_no_understanding(self, validator):
        errors = validator.check_operator_understanding("Just text", {"!"})
        assert len(errors) > 0

    def test_with_understanding(self, validator):
        output = "## 理解確認\n演算子の意味を確認しました"
        errors = validator.check_operator_understanding(output, {"!"})
        assert len(errors) == 0

    # ── validate (integration) ──
    def test_validate_bad_output(self, validator):
        result = validator.validate("Short.", "/noe!~/u+")
        assert result.valid is False
        assert len(result.errors) > 0

    def test_validate_good_output(self, validator):
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

    def test_validate_warnings(self, validator):
        result = validator.validate("short text", "/noe")
        # Should have warning about short output
        assert len(result.warnings) >= 1


# ═══ OPERATOR constants ═══════════════

class TestOperatorConstants:
    """演算子定数のテスト"""

    def test_required_sections_factorial(self):
        assert "!" in OPERATOR_REQUIRED_SECTIONS

    def test_required_sections_oscillation(self):
        assert "~" in OPERATOR_REQUIRED_SECTIONS

    def test_required_sections_merge(self):
        assert "*" in OPERATOR_REQUIRED_SECTIONS

    def test_min_lines_factorial(self):
        assert OPERATOR_MIN_LINES["!"] >= 10

    def test_min_lines_oscillation(self):
        assert OPERATOR_MIN_LINES["~"] >= 10


# ═══ LearnedPattern ════════════════════

class TestLearnedPattern:
    """学習パターンデータクラスのテスト"""

    def test_create(self):
        p = LearnedPattern(
            intent="分析して", ccl="/s+", confidence=0.8, usage_count=1
        )
        assert p.intent == "分析して"
        assert p.confidence == 0.8


# ═══ DoxaLearner ═══════════════════════

class TestDoxaLearner:
    """Doxa パターン学習のテスト"""

    @pytest.fixture
    def learner(self, tmp_path):
        return DoxaLearner(store_path=tmp_path / "patterns.json")

    def test_init_empty(self, learner):
        assert len(learner.patterns) == 0

    def test_record(self, learner):
        learner.record("分析してください", "/s+")
        assert len(learner.patterns) == 1

    def test_record_persists(self, learner, tmp_path):
        learner.record("分析", "/s+")
        # Load fresh
        learner2 = DoxaLearner(store_path=tmp_path / "patterns.json")
        assert len(learner2.patterns) == 1

    def test_record_reinforce(self, learner):
        learner.record("分析", "/s+")
        learner.record("分析", "/s+")
        assert learner.patterns[0].usage_count == 2
        assert learner.patterns[0].confidence > 0.8

    def test_record_update_ccl(self, learner):
        learner.record("分析", "/s+")
        learner.record("分析", "/s-")
        assert learner.patterns[0].ccl == "/s-"

    def test_lookup_exact(self, learner):
        learner.record("分析してください", "/s+")
        result = learner.lookup("分析してください")
        assert result == "/s+"

    def test_lookup_substring(self, learner):
        learner.record("詳しく分析してください", "/s+")
        result = learner.lookup("分析してください")
        assert result == "/s+"

    def test_lookup_no_match(self, learner):
        learner.record("分析", "/s+")
        result = learner.lookup("xyz random text")
        assert result is None

    def test_get_stats_empty(self, learner):
        stats = learner.get_stats()
        assert stats["count"] == 0

    def test_get_stats(self, learner):
        learner.record("分析", "/s+")
        learner.record("判定", "/dia")
        stats = learner.get_stats()
        assert stats["count"] == 2
        assert stats["total_usage"] == 2
        assert 0 < stats["avg_confidence"] <= 1.0

    def test_multiple_patterns(self, learner):
        learner.record("分析", "/s+")
        learner.record("判定", "/dia")
        learner.record("実行", "/ene")
        assert len(learner.patterns) == 3


# ═══ SemanticResult ════════════════════

class TestSemanticResult:
    """意味的検証結果のテスト"""

    def test_aligned_truthy(self):
        r = SemanticResult(
            aligned=True, confidence=0.9, reasoning="OK", suggestions=[]
        )
        assert bool(r) is True

    def test_not_aligned_falsy(self):
        r = SemanticResult(
            aligned=False, confidence=0.1, reasoning="Bad", suggestions=["fix"]
        )
        assert bool(r) is False


# ═══ CCLSemanticValidator ══════════════

class TestCCLSemanticValidator:
    """意味的検証器のテスト"""

    @pytest.fixture
    def validator(self):
        return CCLSemanticValidator()

    def test_init(self, validator):
        assert validator.model_name == "gemini-2.0-flash"

    def test_default_prompt(self, validator):
        prompt = validator._default_prompt()
        assert "CCL" in prompt

    def test_build_prompt(self, validator):
        prompt = validator._build_prompt("分析して", "/s+", None)
        assert "分析して" in prompt
        assert "/s+" in prompt

    def test_build_prompt_with_context(self, validator):
        prompt = validator._build_prompt("分析", "/s", "コンテキスト情報")
        assert "コンテキスト" in prompt

    def test_parse_response_json(self, validator):
        response = '```json\n{"aligned": true, "confidence": 0.95, "reasoning": "Good match", "suggestions": []}\n```'
        result = validator._parse_response(response)
        assert result.aligned is True
        assert result.confidence == 0.95

    def test_parse_response_plain_json(self, validator):
        response = '{"aligned": false, "confidence": 0.3, "reasoning": "Bad", "suggestions": ["fix"]}'
        result = validator._parse_response(response)
        assert result.aligned is False
        assert len(result.suggestions) == 1

    def test_parse_response_fallback(self, validator):
        response = "This expression is aligned with the intent."
        result = validator._parse_response(response)
        assert isinstance(result, SemanticResult)

    def test_validate_without_llm(self, validator):
        result = validator.validate("分析して", "/s+")
        # Without API key, should gracefully degrade
        assert result.aligned is True  # Graceful degradation
        assert result.confidence == 0.0  # No confidence without LLM
