# PURPOSE: MultiSemanticAgent のテスト (Layer B: Nous)
"""
Tests for Multi-LLM Ensemble Audit Agent.

テスト範囲:
1. StubBackend × 3 でのアンサンブル生成
2. Majority voting ロジック
3. Persona 付きプロンプト生成
4. with_multi_l2() 統合テスト
5. 単一メンバーでの CRITICAL 採用
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from mekhane.synteleia.base import (
    AgentResult,
    AuditIssue,
    AuditSeverity,
    AuditTarget,
    AuditTargetType,
)
from mekhane.synteleia.dokimasia.semantic_agent import StubBackend
from mekhane.synteleia.dokimasia.multi_semantic_agent import (
    MultiSemanticAgent,
    EnsembleMember,
    PERSONAS,
    _severity_rank,
)


# =============================================================================
# Fixtures
# =============================================================================


def _make_target(content: str = "test content") -> AuditTarget:
    """テスト用 AuditTarget を生成。"""
    return AuditTarget(
        content=content,
        target_type=AuditTargetType.GENERIC,
        metadata={},
    )


def _stub_response(issues: list, confidence: float = 0.8) -> str:
    """テスト用 JSON レスポンスを生成。"""
    return json.dumps({
        "issues": issues,
        "summary": "Test summary",
        "confidence": confidence,
    })


def _issue(code: str = "SEM-001", severity: str = "medium", msg: str = "issue") -> dict:
    """テスト用 issue dict を生成。"""
    return {
        "code": code,
        "severity": severity,
        "message": msg,
        "suggestion": "fix it",
    }


# =============================================================================
# Test: EnsembleMember
# =============================================================================


class TestEnsembleMember:
    """EnsembleMember のテスト。"""

    def test_persona_prompt_contains_persona(self):
        """persona_prompt に persona 固有のテキストが含まれること。"""
        member = EnsembleMember(
            name="test", backend=StubBackend(), persona="critic"
        )
        prompt = member.persona_prompt
        assert "批判者" in prompt
        assert "Critic" in prompt

    def test_persona_prompt_contains_base_prompt(self):
        """persona_prompt にベース監査プロンプトが含まれること。"""
        member = EnsembleMember(
            name="test", backend=StubBackend(), persona="pragmatist"
        )
        prompt = member.persona_prompt
        assert "セマンティック" in prompt or "監査" in prompt


# =============================================================================
# Test: MultiSemanticAgent
# =============================================================================


class TestMultiSemanticAgent:
    """MultiSemanticAgent のテスト。"""

    def test_with_stubs_creates_3_members(self):
        """with_stubs() で 3 メンバーが生成されること。"""
        agent = MultiSemanticAgent.with_stubs()
        assert len(agent.members) == 3

    def test_with_stubs_covers_all_personas(self):
        """全 persona がカバーされること。"""
        agent = MultiSemanticAgent.with_stubs()
        personas = {m.persona for m in agent.members}
        assert personas == {"critic", "optimist", "pragmatist"}

    def test_audit_no_issues(self):
        """全メンバーが問題なしの場合、passed=True。"""
        agent = MultiSemanticAgent.with_stubs()
        result = agent.audit(_make_target())
        assert result.passed is True
        assert result.issues == []
        assert result.metadata["multi_llm"] is True

    def test_audit_unanimous_issue(self):
        """全メンバーが同じ issue を見つけた場合、採用される。"""
        issue = _issue(code="SEM-001", severity="high", msg="design flaw found")
        resp = _stub_response([issue], confidence=0.9)
        responses = {p: resp for p in PERSONAS}
        agent = MultiSemanticAgent.with_stubs(responses=responses)
        result = agent.audit(_make_target())

        assert result.passed is False  # HIGH → not passed
        assert len(result.issues) >= 1
        assert "3/3 votes" in result.issues[0].message

    def test_audit_majority_issue(self):
        """2/3 メンバーが同じ issue を見つけた場合、採用される。"""
        issue = _issue(code="SEM-002", severity="medium", msg="minor concern here")
        resp_with = _stub_response([issue], confidence=0.8)
        resp_without = _stub_response([], confidence=0.7)

        responses = {
            "critic": resp_with,
            "pragmatist": resp_with,
            "optimist": resp_without,
        }
        agent = MultiSemanticAgent.with_stubs(responses=responses)
        result = agent.audit(_make_target())

        assert len(result.issues) >= 1
        assert "2/3 votes" in result.issues[0].message

    def test_audit_single_non_critical_rejected(self):
        """1/3 メンバーのみの non-CRITICAL issue は除外される。"""
        issue = _issue(code="SEM-003", severity="low", msg="cosmetic issue only")
        resp_with = _stub_response([issue], confidence=0.6)
        resp_without = _stub_response([], confidence=0.8)

        responses = {
            "critic": resp_with,
            "pragmatist": resp_without,
            "optimist": resp_without,
        }
        agent = MultiSemanticAgent.with_stubs(responses=responses)
        result = agent.audit(_make_target())

        assert result.passed is True
        assert len(result.issues) == 0

    def test_audit_single_critical_accepted(self):
        """1/3 メンバーでも CRITICAL は採用される。"""
        issue = _issue(code="SEM-004", severity="critical", msg="security vulnerability")
        resp_with = _stub_response([issue], confidence=0.95)
        resp_without = _stub_response([], confidence=0.7)

        responses = {
            "critic": resp_with,
            "pragmatist": resp_without,
            "optimist": resp_without,
        }
        agent = MultiSemanticAgent.with_stubs(responses=responses)
        result = agent.audit(_make_target())

        assert result.passed is False  # CRITICAL → not passed
        assert len(result.issues) >= 1

    def test_audit_metadata_contains_member_info(self):
        """メタデータにメンバー情報が含まれること。"""
        agent = MultiSemanticAgent.with_stubs()
        result = agent.audit(_make_target())

        assert "members" in result.metadata
        assert len(result.metadata["members"]) == 3
        assert result.metadata["voting"] == "confidence-weighted majority"

    def test_supports_text_types(self):
        """テキスト系ターゲットをサポートすること。"""
        agent = MultiSemanticAgent.with_stubs()
        assert agent.supports(AuditTargetType.GENERIC) is True
        assert agent.supports(AuditTargetType.CCL_OUTPUT) is True

    def test_severity_rank(self):
        """severity 順序が正しいこと。"""
        assert _severity_rank(AuditSeverity.CRITICAL) > _severity_rank(AuditSeverity.HIGH)
        assert _severity_rank(AuditSeverity.HIGH) > _severity_rank(AuditSeverity.MEDIUM)
        assert _severity_rank(AuditSeverity.MEDIUM) > _severity_rank(AuditSeverity.LOW)
        assert _severity_rank(AuditSeverity.LOW) > _severity_rank(AuditSeverity.INFO)


# =============================================================================
# Test: Orchestrator Integration
# =============================================================================


class TestOrchestratorMultiL2:
    """orchestrator.with_multi_l2() の統合テスト。"""

    def test_with_multi_l2_creates_orchestrator(self):
        """with_multi_l2() がオーケストレータを生成すること。"""
        # OchemaBackend は LS 不在で失敗するので StubBackend にフォールバック
        o = __import__(
            "mekhane.synteleia.orchestrator",
            fromlist=["SynteleiaOrchestrator"],
        ).SynteleiaOrchestrator.with_multi_l2()
        assert o is not None

    def test_with_multi_l2_has_multi_agent(self):
        """with_multi_l2() に MultiSemanticAgent が含まれること。"""
        from mekhane.synteleia.orchestrator import SynteleiaOrchestrator

        o = SynteleiaOrchestrator.with_multi_l2()
        agent_names = [a.name for a in o.dokimasia_agents]
        assert "MultiSemanticAgent" in agent_names
