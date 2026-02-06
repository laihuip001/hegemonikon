import pytest
from mekhane.synteleia.dokimasia.perigraphe_agent import PerigrapheAgent
from mekhane.synteleia.base import AuditTarget, AuditTargetType, AuditSeverity

class TestPerigrapheAgent:
    def test_scope_creep_detection(self):
        agent = PerigrapheAgent()
        # "ついでに" is a scope creep pattern. Added spaces to ensure \b matches.
        content = "プロジェクトのメインタスクはこれですが、 ついでに アレもやりましょう。"
        target = AuditTarget(content=content, target_type=AuditTargetType.GENERIC)

        result = agent.audit(target)

        assert result.passed is True # LOW severity should still pass by default logic in audit() if no CRITICAL/HIGH
        assert len(result.issues) >= 1

        issue = next(i for i in result.issues if i.code == "P-001")
        assert issue.severity == AuditSeverity.LOW
        assert "ついでに" in issue.message or "スコープ逸脱" in issue.message

    def test_no_scope_creep(self):
        agent = PerigrapheAgent()
        content = "Strictly following the plan."
        target = AuditTarget(content=content, target_type=AuditTargetType.GENERIC)

        result = agent.audit(target)

        # Should not have P-001 to P-004
        scope_codes = ["P-001", "P-002", "P-003", "P-004"]
        found_codes = [i.code for i in result.issues if i.code in scope_codes]
        assert len(found_codes) == 0

    def test_ignore_case(self):
        agent = PerigrapheAgent()
        # "AND ALSO" should match "and also" pattern due to IGNORECASE
        content = "We will do this AND ALSO that."
        target = AuditTarget(content=content, target_type=AuditTargetType.GENERIC)

        result = agent.audit(target)

        issue = next((i for i in result.issues if i.code == "P-004"), None)
        assert issue is not None, "Should detect 'AND ALSO' as scope creep"

    def test_boundary_definition_missing_in_plan(self):
        agent = PerigrapheAgent()
        content = "Just a plan without keywords." # Removed "boundary"
        target = AuditTarget(content=content, target_type=AuditTargetType.PLAN)

        result = agent.audit(target)

        # P-010: Missing boundary definition
        issue = next((i for i in result.issues if i.code == "P-010"), None)
        assert issue is not None
        assert issue.severity == AuditSeverity.MEDIUM

    def test_boundary_definition_present_in_plan(self):
        agent = PerigrapheAgent()
        content = "This plan has a clearly defined Scope."
        target = AuditTarget(content=content, target_type=AuditTargetType.PLAN)

        result = agent.audit(target)

        # Should not have P-010
        issue = next((i for i in result.issues if i.code == "P-010"), None)
        assert issue is None
