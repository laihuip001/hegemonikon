#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/ccl/tests/
# PURPOSE: CCL SEL Validator の包括テスト — WF出力がSEL要件を満たすか検証
"""CCL SEL Validator Tests"""

import pytest
from pathlib import Path
from mekhane.ccl.sel_validator import (
    SELRequirement,
    SELValidationResult,
    SELValidator,
)


# ── SELRequirement ───────────────────────

# PURPOSE: Test suite validating s e l requirement correctness
class TestSELRequirement:
    """SEL 要件データクラスのテスト"""

    # PURPOSE: Verify create behaves correctly
    def test_create(self):
        """Verify create behavior."""
        r = SELRequirement(
            description="Test requirement",
            minimum_requirements=["item1", "item2"],
        )
        assert r.description == "Test requirement"
        assert len(r.minimum_requirements) == 2

    # PURPOSE: Verify uml default behaves correctly
    def test_uml_default(self):
        """Verify uml default behavior."""
        r = SELRequirement(description="", minimum_requirements=[])
        assert r.uml_requirements == {}


# ── SELValidationResult ──────────────────

# PURPOSE: Test suite validating s e l validation result correctness
class TestSELValidationResult:
    """SEL 検証結果データクラスのテスト"""

    # PURPOSE: Verify compliant behaves correctly
    def test_compliant(self):
        """Verify compliant behavior."""
        r = SELValidationResult(
            workflow="boot", operator="+",
            is_compliant=True,
            met_requirements=["req1", "req2"],
            score=1.0,
        )
        assert r.is_compliant is True
        assert r.score == 1.0

    # PURPOSE: Verify non compliant behaves correctly
    def test_non_compliant(self):
        """Verify non compliant behavior."""
        r = SELValidationResult(
            workflow="boot", operator="+",
            is_compliant=False,
            missing_requirements=["req1"],
            score=0.5,
        )
        assert r.is_compliant is False
        assert len(r.missing_requirements) == 1

    # PURPOSE: Verify summary method behaves correctly
    def test_summary_method(self):
        """Verify summary method behavior."""
        r = SELValidationResult(
            workflow="boot", operator="+",
            is_compliant=True,
            score=0.8,
        )
        summary = r.summary
        assert isinstance(summary, str)
        assert "boot" in summary


# ── SELValidator ─────────────────────────

# PURPOSE: Test suite validating s e l validator correctness
class TestSELValidator:
    """SEL Validator のテスト"""

    # PURPOSE: Verify validator behaves correctly
    @pytest.fixture
    def validator(self, tmp_path):
        """Temporary workflows dir for testing"""
        return SELValidator(workflows_dir=tmp_path)

    # PURPOSE: Verify boot wf behaves correctly
    @pytest.fixture
    def boot_wf(self, tmp_path):
        """Boot workflow with sel_enforcement"""
        wf = tmp_path / "boot.md"
        wf.write_text("""---
description: Boot workflow
sel_enforcement:
  "+":
    description: "Detailed boot"
    minimum_requirements:
      - "Handoff 読込"
      - "KI 参照"
      - "Persona 設定"
  "-":
    description: "快速 boot"
    minimum_requirements:
      - "Handoff 読込"
---

# Boot WF
""")
        return wf

    # PURPOSE: Verify wf validator behaves correctly
    @pytest.fixture
    def wf_validator(self, boot_wf):
        """Validator with boot WF available"""
        return SELValidator(workflows_dir=boot_wf.parent)

    # PURPOSE: Verify load sel enforcement behaves correctly
    def test_load_sel_enforcement(self, wf_validator):
        """Verify load sel enforcement behavior."""
        req = wf_validator.load_sel_enforcement("boot")
        assert req is not None
        assert "+" in req
        assert "-" in req

    # PURPOSE: Verify load nonexistent wf behaves correctly
    def test_load_nonexistent_wf(self, validator):
        """Verify load nonexistent wf behavior."""
        req = validator.load_sel_enforcement("nonexistent")
        assert req is None or len(req) == 0

    # PURPOSE: Verify check requirement present behaves correctly
    def test_check_requirement_present(self, wf_validator):
        """Verify check requirement present behavior."""
        output = "Handoff 読込に成功しました。KI 参照完了。"
        result = wf_validator.check_requirement("Handoff 読込", output)
        assert result is True

    # PURPOSE: Verify check requirement missing behaves correctly
    def test_check_requirement_missing(self, wf_validator):
        """Verify check requirement missing behavior."""
        output = "Nothing relevant here."
        result = wf_validator.check_requirement("Handoff 読込", output)
        assert result is False

    # PURPOSE: Verify validate compliant behaves correctly
    def test_validate_compliant(self, wf_validator):
        """Verify validate compliant behavior."""
        output = "Handoff 読込に成功。KI 参照完了。Persona 設定済。"
        result = wf_validator.validate("boot", "+", output)
        assert isinstance(result, SELValidationResult)
        assert result.workflow == "boot"
        assert result.operator == "+"

    # PURPOSE: Verify validate non compliant behaves correctly
    def test_validate_non_compliant(self, wf_validator):
        """Verify validate non compliant behavior."""
        output = "Handoff 読込のみ"
        result = wf_validator.validate("boot", "+", output)
        assert len(result.missing_requirements) > 0

    # PURPOSE: Verify validate minimal mode behaves correctly
    def test_validate_minimal_mode(self, wf_validator):
        """Verify validate minimal mode behavior."""
        output = "Handoff 読込完了。"
        result = wf_validator.validate("boot", "-", output)
        # Minimal mode only needs Handoff
        assert result.is_compliant is True

    # PURPOSE: Verify validate batch behaves correctly
    def test_validate_batch(self, wf_validator):
        """Verify validate batch behavior."""
        outputs = {
            "boot": {
                "+": "Handoff 読込。KI 参照。Persona 設定。",
                "-": "Handoff 読込。",
            }
        }
        results = wf_validator.validate_batch(outputs)
        assert len(results) == 2

    # PURPOSE: Verify generate report behaves correctly
    def test_generate_report(self, wf_validator):
        """Verify generate report behavior."""
        output = "Handoff 読込。KI 参照。Persona 設定。"
        result = wf_validator.validate("boot", "+", output)
        report = wf_validator.generate_report([result])
        assert isinstance(report, str)
        assert "boot" in report
