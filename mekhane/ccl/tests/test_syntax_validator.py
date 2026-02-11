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


# PURPOSE: Verify validator behaves correctly
@pytest.fixture
def validator():
    """SyntaxValidator インスタンス"""
    return CCLSyntaxValidator()


# ── ValidationResult ──────────────────────

# PURPOSE: Test suite validating validation result correctness
class TestValidationResult:
    """ValidationResult データクラスのテスト"""

    # PURPOSE: Verify valid result is truthy behaves correctly
    def test_valid_result_is_truthy(self):
        """Verify valid result is truthy behavior."""
        r = ValidationResult(valid=True, errors=[], warnings=[])
        assert bool(r) is True

    # PURPOSE: Verify invalid result is falsy behaves correctly
    def test_invalid_result_is_falsy(self):
        """Verify invalid result is falsy behavior."""
        r = ValidationResult(valid=False, errors=["err"], warnings=[])
        assert bool(r) is False

    # PURPOSE: Verify fields accessible behaves correctly
    def test_fields_accessible(self):
        """Verify fields accessible behavior."""
        r = ValidationResult(valid=True, errors=[], warnings=["w"])
        assert r.valid is True
        assert r.errors == []
        assert r.warnings == ["w"]


# ── VALID_WORKFLOWS ──────────────────────

# PURPOSE: Test suite validating valid workflows correctness
class TestValidWorkflows:
    """Valid workflows set のテスト"""

    # PURPOSE: Verify o series present behaves correctly
    def test_o_series_present(self):
        """Verify o series present behavior."""
        for wf in ["noe", "bou", "zet", "ene"]:
            assert wf in VALID_WORKFLOWS, f"O-series WF {wf} missing"

    # PURPOSE: Verify s series present behaves correctly
    def test_s_series_present(self):
        """Verify s series present behavior."""
        for wf in ["mek", "met", "sta", "pra"]:
            assert wf in VALID_WORKFLOWS, f"S-series WF {wf} missing"

    # PURPOSE: Verify h series present behaves correctly
    def test_h_series_present(self):
        """Verify h series present behavior."""
        for wf in ["pro", "pis", "ore", "dox"]:
            assert wf in VALID_WORKFLOWS, f"H-series WF {wf} missing"

    # PURPOSE: Verify p series present behaves correctly
    def test_p_series_present(self):
        """Verify p series present behavior."""
        for wf in ["kho", "hod", "tro", "tek"]:
            assert wf in VALID_WORKFLOWS, f"P-series WF {wf} missing"

    # PURPOSE: Verify k series present behaves correctly
    def test_k_series_present(self):
        """Verify k series present behavior."""
        for wf in ["euk", "chr", "tel", "sop"]:
            assert wf in VALID_WORKFLOWS, f"K-series WF {wf} missing"

    # PURPOSE: Verify a series present behaves correctly
    def test_a_series_present(self):
        """Verify a series present behavior."""
        for wf in ["pat", "dia", "gno", "epi"]:
            assert wf in VALID_WORKFLOWS, f"A-series WF {wf} missing"

    # PURPOSE: Verify meta present behaves correctly
    def test_meta_present(self):
        """Verify meta present behavior."""
        for wf in ["boot", "bye", "ax", "u"]:
            assert wf in VALID_WORKFLOWS, f"Meta WF {wf} missing"

    # PURPOSE: Verify total count behaves correctly
    def test_total_count(self):
        """Verify total count behavior."""
        assert len(VALID_WORKFLOWS) >= 30, "Should have at least 30 workflows"


# ── Empty/Invalid Input ──────────────────

# PURPOSE: Test suite validating empty input correctness
class TestEmptyInput:
    """空入力のテスト"""

    # PURPOSE: Verify empty string behaves correctly
    def test_empty_string(self, validator):
        """Verify empty string behavior."""
        r = validator.validate("")
        assert not r.valid
        assert "Empty CCL expression" in r.errors[0]

    # PURPOSE: Verify whitespace only behaves correctly
    def test_whitespace_only(self, validator):
        """Verify whitespace only behavior."""
        r = validator.validate("   ")
        assert not r.valid

    # PURPOSE: Verify none like empty behaves correctly
    def test_none_like_empty(self, validator):
        """Verify none like empty behavior."""
        r = validator.validate("")
        assert r.valid is False


# ── Valid Expressions ────────────────────

# PURPOSE: Test suite validating valid expressions correctness
class TestValidExpressions:
    """正常な CCL 式のテスト"""

    # PURPOSE: Verify simple workflow behaves correctly
    def test_simple_workflow(self, validator):
        """Verify simple workflow behavior."""
        r = validator.validate("/noe")
        assert r.valid

    # PURPOSE: Verify workflow with operator behaves correctly
    def test_workflow_with_operator(self, validator):
        """Verify workflow with operator behavior."""
        r = validator.validate("/noe+")
        assert r.valid

    # PURPOSE: Verify sequence behaves correctly
    def test_sequence(self, validator):
        """Verify sequence behavior."""
        r = validator.validate("/bou+_/s+_/dia")
        assert r.valid

    # PURPOSE: Verify oscillation behaves correctly
    def test_oscillation(self, validator):
        """Verify oscillation behavior."""
        r = validator.validate("/s~/dia~/noe")
        assert r.valid

    # PURPOSE: Verify fusion behaves correctly
    def test_fusion(self, validator):
        """Verify fusion behavior."""
        r = validator.validate("/noe*/bou")
        assert r.valid

    # PURPOSE: Verify colimit behaves correctly
    def test_colimit(self, validator):
        """Verify colimit behavior."""
        r = validator.validate("\\(/noe_/dia)")
        assert r.valid

    # PURPOSE: Verify meta operator behaves correctly
    def test_meta_operator(self, validator):
        """Verify meta operator behavior."""
        r = validator.validate("/noe^")
        assert r.valid

    # PURPOSE: Verify compound oscillation behaves correctly
    def test_compound_oscillation(self, validator):
        """Verify compound oscillation behavior."""
        r = validator.validate("/s~*/dia")
        assert r.valid

    # PURPOSE: Verify complex expression behaves correctly
    def test_complex_expression(self, validator):
        """Verify complex expression behavior."""
        r = validator.validate("/s+~(/p*/a)_/dia*/o+")
        assert r.valid

    # PURPOSE: Verify for loop behaves correctly
    def test_for_loop(self, validator):
        """Verify for loop behavior."""
        r = validator.validate("F:3{/dia+_/ene+}")
        assert r.valid

    # PURPOSE: Verify if condition behaves correctly
    def test_if_condition(self, validator):
        """Verify if condition behavior."""
        r = validator.validate("I:conf>0.8{/ene+}")
        assert r.valid

    # PURPOSE: Verify pipe operator behaves correctly
    def test_pipe_operator(self, validator):
        """Verify pipe operator behavior."""
        r = validator.validate("/sop|>/noe")
        assert r.valid


# ── Brace Balancing ──────────────────────

# PURPOSE: Test suite validating brace balancing correctness
class TestBraceBalancing:
    """括弧バランスのテスト"""

    # PURPOSE: Verify unbalanced braces behaves correctly
    def test_unbalanced_braces(self, validator):
        """Verify unbalanced braces behavior."""
        r = validator.validate("/noe{")
        assert not r.valid
        assert any("brace" in e.lower() for e in r.errors)

    # PURPOSE: Verify unbalanced brackets behaves correctly
    def test_unbalanced_brackets(self, validator):
        """Verify unbalanced brackets behavior."""
        r = validator.validate("/noe[")
        assert not r.valid
        assert any("bracket" in e.lower() for e in r.errors)

    # PURPOSE: Verify unbalanced parens behaves correctly
    def test_unbalanced_parens(self, validator):
        """Verify unbalanced parens behavior."""
        r = validator.validate("/noe(")
        assert not r.valid
        assert any("parenthes" in e.lower() for e in r.errors)

    # PURPOSE: Verify balanced all behaves correctly
    def test_balanced_all(self, validator):
        """Verify balanced all behavior."""
        r = validator.validate("{[(/noe)]}")
        assert r.valid


# ── Workflow Validation ──────────────────

# PURPOSE: Test suite validating workflow validation correctness
class TestWorkflowValidation:
    """ワークフロー参照のテスト"""

    # PURPOSE: Verify unknown workflow warns behaves correctly
    def test_unknown_workflow_warns(self, validator):
        """Verify unknown workflow warns behavior."""
        r = validator.validate("/xyz123")
        assert r.valid  # Warning, not error
        assert any("Unknown workflow" in w for w in r.warnings)

    # PURPOSE: Verify known workflow no warning behaves correctly
    def test_known_workflow_no_warning(self, validator):
        """Verify known workflow no warning behavior."""
        r = validator.validate("/noe")
        assert len(r.warnings) == 0

    # PURPOSE: Verify multiple workflows behaves correctly
    def test_multiple_workflows(self, validator):
        """Verify multiple workflows behavior."""
        r = validator.validate("/noe_/bou_/dia")
        assert r.valid
        assert len(r.warnings) == 0


# ── Operator Validation ──────────────────

# PURPOSE: Test suite validating operator validation correctness
class TestOperatorValidation:
    """演算子のテスト"""

    # PURPOSE: Verify consecutive binary ops error behaves correctly
    def test_consecutive_binary_ops_error(self, validator):
        """Verify consecutive binary ops error behavior."""
        r = validator.validate("/noe__/bou")
        assert not r.valid
        assert any("Consecutive" in e for e in r.errors)

    # PURPOSE: Verify compound ops not flagged behaves correctly
    def test_compound_ops_not_flagged(self, validator):
        """Verify compound ops not flagged behavior."""
        r = validator.validate("/s~*/dia")
        # ~* is a valid compound operator
        assert r.valid


# ── Control Syntax ───────────────────────

# PURPOSE: Test suite validating control syntax correctness
class TestControlSyntax:
    """制御構文のテスト"""

    # PURPOSE: Verify for without spec behaves correctly
    def test_for_without_spec(self, validator):
        """Verify for without spec behavior."""
        r = validator.validate("F:{/noe}")
        assert not r.valid
        assert any("For loop" in e for e in r.errors)

    # PURPOSE: Verify if without condition behaves correctly
    def test_if_without_condition(self, validator):
        """Verify if without condition behavior."""
        r = validator.validate("I:{/noe}")
        assert not r.valid
        assert any("If statement" in e for e in r.errors)

    # PURPOSE: Verify valid for behaves correctly
    def test_valid_for(self, validator):
        """Verify valid for behavior."""
        r = validator.validate("F:5{/dia_/ene}")
        assert r.valid

    # PURPOSE: Verify valid if behaves correctly
    def test_valid_if(self, validator):
        """Verify valid if behavior."""
        r = validator.validate("I:h>0.7{/ene+}")
        assert r.valid


# ── Edge Cases ───────────────────────────

# PURPOSE: Test suite validating edge cases correctness
class TestEdgeCases:
    """エッジケースのテスト"""

    # PURPOSE: Verify just operator behaves correctly
    def test_just_operator(self, validator):
        """Verify just operator behavior."""
        r = validator.validate("+")
        assert r.valid  # No braces/control issue

    # PURPOSE: Verify deeply nested behaves correctly
    def test_deeply_nested(self, validator):
        """Verify deeply nested behavior."""
        r = validator.validate("F:3{I:x>0{/noe_/dia+}}")
        assert r.valid

    # PURPOSE: Verify all series hubs behaves correctly
    def test_all_series_hubs(self, validator):
        """Verify all series hubs behavior."""
        for hub in ["s", "h", "p", "k", "a"]:
            r = validator.validate(f"/{hub}+")
            assert r.valid, f"Hub /{hub}+ should be valid"

    # PURPOSE: Verify colimit shorthand behaves correctly
    def test_colimit_shorthand(self, validator):
        """Verify colimit shorthand behavior."""
        r = validator.validate("\\pan+")
        # \pan+ should not generate error
        assert r.valid
