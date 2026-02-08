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

class TestSELRequirement:
    """SEL 要件データクラスのテスト"""

    def test_create(self):
        r = SELRequirement(
            description="Test requirement",
            minimum_requirements=["item1", "item2"],
        )
        assert r.description == "Test requirement"
        assert len(r.minimum_requirements) == 2

    def test_uml_default(self):
        r = SELRequirement(description="", minimum_requirements=[])
        assert r.uml_requirements == {}


# ── SELValidationResult ──────────────────

class TestSELValidationResult:
    """SEL 検証結果データクラスのテスト"""

    def test_compliant(self):
        r = SELValidationResult(
            workflow="boot", operator="+",
            is_compliant=True,
            met_requirements=["req1", "req2"],
            score=1.0,
        )
        assert r.is_compliant is True
        assert r.score == 1.0

    def test_non_compliant(self):
        r = SELValidationResult(
            workflow="boot", operator="+",
            is_compliant=False,
            missing_requirements=["req1"],
            score=0.5,
        )
        assert r.is_compliant is False
        assert len(r.missing_requirements) == 1

    def test_summary_method(self):
        r = SELValidationResult(
            workflow="boot", operator="+",
            is_compliant=True,
            score=0.8,
        )
        summary = r.summary
        assert isinstance(summary, str)
        assert "boot" in summary


# ── SELValidator ─────────────────────────

class TestSELValidator:
    """SEL Validator のテスト"""

    @pytest.fixture
    def validator(self, tmp_path):
        """Temporary workflows dir for testing"""
        return SELValidator(workflows_dir=tmp_path)

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

    @pytest.fixture
    def wf_validator(self, boot_wf):
        """Validator with boot WF available"""
        return SELValidator(workflows_dir=boot_wf.parent)

    def test_load_sel_enforcement(self, wf_validator):
        req = wf_validator.load_sel_enforcement("boot")
        assert req is not None
        assert "+" in req
        assert "-" in req

    def test_load_nonexistent_wf(self, validator):
        req = validator.load_sel_enforcement("nonexistent")
        assert req is None or len(req) == 0

    def test_check_requirement_present(self, wf_validator):
        output = "Handoff 読込に成功しました。KI 参照完了。"
        result = wf_validator.check_requirement("Handoff 読込", output)
        assert result is True

    def test_check_requirement_missing(self, wf_validator):
        output = "Nothing relevant here."
        result = wf_validator.check_requirement("Handoff 読込", output)
        assert result is False

    def test_validate_compliant(self, wf_validator):
        output = "Handoff 読込に成功。KI 参照完了。Persona 設定済。"
        result = wf_validator.validate("boot", "+", output)
        assert isinstance(result, SELValidationResult)
        assert result.workflow == "boot"
        assert result.operator == "+"

    def test_validate_non_compliant(self, wf_validator):
        output = "Handoff 読込のみ"
        result = wf_validator.validate("boot", "+", output)
        assert len(result.missing_requirements) > 0

    def test_validate_minimal_mode(self, wf_validator):
        output = "Handoff 読込完了。"
        result = wf_validator.validate("boot", "-", output)
        # Minimal mode only needs Handoff
        assert result.is_compliant is True

    def test_validate_batch(self, wf_validator):
        outputs = {
            "boot": {
                "+": "Handoff 読込。KI 参照。Persona 設定。",
                "-": "Handoff 読込。",
            }
        }
        results = wf_validator.validate_batch(outputs)
        assert len(results) == 2

    def test_generate_report(self, wf_validator):
        output = "Handoff 読込。KI 参照。Persona 設定。"
        result = wf_validator.validate("boot", "+", output)
        report = wf_validator.generate_report([result])
        assert isinstance(report, str)
        assert "boot" in report
