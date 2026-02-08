#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/ccl/tests/
# PURPOSE: CCL SyntaxValidator の包括テスト — v2.0仕様準拠を検証
"""CCL SyntaxValidator Tests"""

import pytest
from mekhane.ccl.syntax_validator import (
    CCLSyntaxValidator,
    ValidationResult,
    VALID_WORKFLOWS,
)


@pytest.fixture
def validator():
    """SyntaxValidator インスタンス"""
    return CCLSyntaxValidator()


# ── ValidationResult ──────────────────────

class TestValidationResult:
    """ValidationResult データクラスのテスト"""

    def test_valid_result_is_truthy(self):
        r = ValidationResult(valid=True, errors=[], warnings=[])
        assert bool(r) is True

    def test_invalid_result_is_falsy(self):
        r = ValidationResult(valid=False, errors=["err"], warnings=[])
        assert bool(r) is False

    def test_fields_accessible(self):
        r = ValidationResult(valid=True, errors=[], warnings=["w"])
        assert r.valid is True
        assert r.errors == []
        assert r.warnings == ["w"]


# ── VALID_WORKFLOWS ──────────────────────

class TestValidWorkflows:
    """Valid workflows set のテスト"""

    def test_o_series_present(self):
        for wf in ["noe", "bou", "zet", "ene"]:
            assert wf in VALID_WORKFLOWS, f"O-series WF {wf} missing"

    def test_s_series_present(self):
        for wf in ["mek", "met", "sta", "pra"]:
            assert wf in VALID_WORKFLOWS, f"S-series WF {wf} missing"

    def test_h_series_present(self):
        for wf in ["pro", "pis", "ore", "dox"]:
            assert wf in VALID_WORKFLOWS, f"H-series WF {wf} missing"

    def test_p_series_present(self):
        for wf in ["kho", "hod", "tro", "tek"]:
            assert wf in VALID_WORKFLOWS, f"P-series WF {wf} missing"

    def test_k_series_present(self):
        for wf in ["euk", "chr", "tel", "sop"]:
            assert wf in VALID_WORKFLOWS, f"K-series WF {wf} missing"

    def test_a_series_present(self):
        for wf in ["pat", "dia", "gno", "epi"]:
            assert wf in VALID_WORKFLOWS, f"A-series WF {wf} missing"

    def test_meta_present(self):
        for wf in ["boot", "bye", "ax", "u"]:
            assert wf in VALID_WORKFLOWS, f"Meta WF {wf} missing"

    def test_total_count(self):
        assert len(VALID_WORKFLOWS) >= 30, "Should have at least 30 workflows"


# ── Empty/Invalid Input ──────────────────

class TestEmptyInput:
    """空入力のテスト"""

    def test_empty_string(self, validator):
        r = validator.validate("")
        assert not r.valid
        assert "Empty CCL expression" in r.errors[0]

    def test_whitespace_only(self, validator):
        r = validator.validate("   ")
        assert not r.valid

    def test_none_like_empty(self, validator):
        r = validator.validate("")
        assert r.valid is False


# ── Valid Expressions ────────────────────

class TestValidExpressions:
    """正常な CCL 式のテスト"""

    def test_simple_workflow(self, validator):
        r = validator.validate("/noe")
        assert r.valid

    def test_workflow_with_operator(self, validator):
        r = validator.validate("/noe+")
        assert r.valid

    def test_sequence(self, validator):
        r = validator.validate("/bou+_/s+_/dia")
        assert r.valid

    def test_oscillation(self, validator):
        r = validator.validate("/s~/dia~/noe")
        assert r.valid

    def test_fusion(self, validator):
        r = validator.validate("/noe*/bou")
        assert r.valid

    def test_colimit(self, validator):
        r = validator.validate("\\(/noe_/dia)")
        assert r.valid

    def test_meta_operator(self, validator):
        r = validator.validate("/noe^")
        assert r.valid

    def test_compound_oscillation(self, validator):
        r = validator.validate("/s~*/dia")
        assert r.valid

    def test_complex_expression(self, validator):
        r = validator.validate("/s+~(/p*/a)_/dia*/o+")
        assert r.valid

    def test_for_loop(self, validator):
        r = validator.validate("F:3{/dia+_/ene+}")
        assert r.valid

    def test_if_condition(self, validator):
        r = validator.validate("I:conf>0.8{/ene+}")
        assert r.valid

    def test_pipe_operator(self, validator):
        r = validator.validate("/sop|>/noe")
        assert r.valid


# ── Brace Balancing ──────────────────────

class TestBraceBalancing:
    """括弧バランスのテスト"""

    def test_unbalanced_braces(self, validator):
        r = validator.validate("/noe{")
        assert not r.valid
        assert any("brace" in e.lower() for e in r.errors)

    def test_unbalanced_brackets(self, validator):
        r = validator.validate("/noe[")
        assert not r.valid
        assert any("bracket" in e.lower() for e in r.errors)

    def test_unbalanced_parens(self, validator):
        r = validator.validate("/noe(")
        assert not r.valid
        assert any("parenthes" in e.lower() for e in r.errors)

    def test_balanced_all(self, validator):
        r = validator.validate("{[(/noe)]}")
        assert r.valid


# ── Workflow Validation ──────────────────

class TestWorkflowValidation:
    """ワークフロー参照のテスト"""

    def test_unknown_workflow_warns(self, validator):
        r = validator.validate("/xyz123")
        assert r.valid  # Warning, not error
        assert any("Unknown workflow" in w for w in r.warnings)

    def test_known_workflow_no_warning(self, validator):
        r = validator.validate("/noe")
        assert len(r.warnings) == 0

    def test_multiple_workflows(self, validator):
        r = validator.validate("/noe_/bou_/dia")
        assert r.valid
        assert len(r.warnings) == 0


# ── Operator Validation ──────────────────

class TestOperatorValidation:
    """演算子のテスト"""

    def test_consecutive_binary_ops_error(self, validator):
        r = validator.validate("/noe__/bou")
        assert not r.valid
        assert any("Consecutive" in e for e in r.errors)

    def test_compound_ops_not_flagged(self, validator):
        r = validator.validate("/s~*/dia")
        # ~* is a valid compound operator
        assert r.valid


# ── Control Syntax ───────────────────────

class TestControlSyntax:
    """制御構文のテスト"""

    def test_for_without_spec(self, validator):
        r = validator.validate("F:{/noe}")
        assert not r.valid
        assert any("For loop" in e for e in r.errors)

    def test_if_without_condition(self, validator):
        r = validator.validate("I:{/noe}")
        assert not r.valid
        assert any("If statement" in e for e in r.errors)

    def test_valid_for(self, validator):
        r = validator.validate("F:5{/dia_/ene}")
        assert r.valid

    def test_valid_if(self, validator):
        r = validator.validate("I:h>0.7{/ene+}")
        assert r.valid


# ── Edge Cases ───────────────────────────

class TestEdgeCases:
    """エッジケースのテスト"""

    def test_just_operator(self, validator):
        r = validator.validate("+")
        assert r.valid  # No braces/control issue

    def test_deeply_nested(self, validator):
        r = validator.validate("F:3{I:x>0{/noe_/dia+}}")
        assert r.valid

    def test_all_series_hubs(self, validator):
        for hub in ["s", "h", "p", "k", "a"]:
            r = validator.validate(f"/{hub}+")
            assert r.valid, f"Hub /{hub}+ should be valid"

    def test_colimit_shorthand(self, validator):
        r = validator.validate("\\pan+")
        # \pan+ should not generate error
        assert r.valid
