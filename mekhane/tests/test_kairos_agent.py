
import pytest
from mekhane.synteleia.dokimasia.kairos_agent import KairosAgent
from mekhane.synteleia.base import AuditTarget, AuditTargetType, AuditSeverity

@pytest.fixture
def agent():
    return KairosAgent()

def test_timing_problems_detection(agent):
    # Using spaces to ensure \b matches
    content = "この機能は 後で 実装します。"
    target = AuditTarget(content=content, target_type=AuditTargetType.PLAN)
    result = agent.audit(target)

    # Severity is LOW, so passed should be True
    assert result.passed
    issues = result.issues
    codes = [i.code for i in issues]
    assert "K-001" in codes
    assert any("「後で」" in i.message for i in issues)

def test_premature_optimization_detection(agent):
    # Pattern: r"\b最適化\b.*\bまず\b" (Optimization ... first)
    content = " 最適化 してから まず 実装"
    target = AuditTarget(content=content, target_type=AuditTargetType.PLAN)
    result = agent.audit(target)

    # Severity is MEDIUM, so passed should be True
    assert result.passed
    issues = result.issues
    codes = [i.code for i in issues]
    assert "K-010" in codes

def test_no_issues(agent):
    content = "期限は明日です。具体的に進めましょう。"
    target = AuditTarget(content=content, target_type=AuditTargetType.PLAN)
    result = agent.audit(target)

    assert result.passed

    timing_codes = ["K-001", "K-002", "K-003", "K-004", "K-005", "K-006"]
    premature_codes = ["K-010", "K-011", "K-012"]

    issues = result.issues
    found_codes = [i.code for i in issues]

    for code in timing_codes:
        assert code not in found_codes
    for code in premature_codes:
        assert code not in found_codes

def test_case_insensitivity(agent):
    content = "We will do it LATER"
    target = AuditTarget(content=content, target_type=AuditTargetType.PLAN)
    result = agent.audit(target)

    issues = result.issues
    codes = [i.code for i in issues]
    assert "K-004" in codes

def test_temporal_context(agent):
    content = "No time info here."
    target = AuditTarget(content=content, target_type=AuditTargetType.PLAN)
    result = agent.audit(target)

    issues = result.issues
    codes = [i.code for i in issues]
    assert "K-020" in codes
