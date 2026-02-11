#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/synteleia/tests/
# PURPOSE: Synteleia 2層オーケストレーター + 基底クラスの包括テスト
"""Synteleia Audit System Tests"""

import pytest
from mekhane.synteleia.base import (
    AuditSeverity,
    AuditTargetType,
    AuditTarget,
    AuditIssue,
    AgentResult,
    AuditResult,
    AuditAgent,
)
from mekhane.synteleia.orchestrator import SynteleiaOrchestrator
from mekhane.synteleia.poiesis import OusiaAgent, SchemaAgent, HormeAgent
from mekhane.synteleia.dokimasia import (
    PerigrapheAgent,
    KairosAgent,
    OperatorAgent,
    LogicAgent,
    CompletenessAgent,
)


# ── AuditSeverity ────────────────────────

class TestAuditSeverity:
    """重大度 Enum のテスト"""

    def test_all_levels(self):
        levels = [s.value for s in AuditSeverity]
        assert "critical" in levels
        assert "high" in levels
        assert "medium" in levels
        assert "low" in levels
        assert "info" in levels

    def test_count(self):
        assert len(AuditSeverity) == 5


# ── AuditTargetType ──────────────────────

class TestAuditTargetType:
    """監査対象種類 Enum のテスト"""

    def test_ccl_output(self):
        assert AuditTargetType.CCL_OUTPUT.value == "ccl_output"

    def test_code(self):
        assert AuditTargetType.CODE.value == "code"

    def test_all_types(self):
        types = [t.value for t in AuditTargetType]
        assert "thought" in types
        assert "plan" in types
        assert "proof" in types
        assert "generic" in types


# ── AuditTarget ──────────────────────────

class TestAuditTarget:
    """監査対象データクラスのテスト"""

    def test_create_generic(self):
        t = AuditTarget(content="test content")
        assert t.target_type == AuditTargetType.GENERIC
        assert t.content == "test content"

    def test_create_with_type(self):
        t = AuditTarget(content="x", target_type=AuditTargetType.CODE)
        assert t.target_type == AuditTargetType.CODE

    def test_metadata_default(self):
        t = AuditTarget(content="x")
        assert t.metadata == {}

    def test_source_default_none(self):
        t = AuditTarget(content="x")
        assert t.source is None


# ── AuditIssue ───────────────────────────

class TestAuditIssue:
    """監査問題データクラスのテスト"""

    def test_create_issue(self):
        i = AuditIssue(
            agent="TestAgent",
            code="TEST-001",
            severity=AuditSeverity.MEDIUM,
            message="Test issue",
        )
        assert i.code == "TEST-001"
        assert i.severity == AuditSeverity.MEDIUM

    def test_with_suggestion(self):
        i = AuditIssue(
            agent="A", code="C", severity=AuditSeverity.LOW,
            message="msg", suggestion="fix this",
        )
        assert i.suggestion == "fix this"


# ── AgentResult ──────────────────────────

class TestAgentResult:
    """エージェント結果データクラスのテスト"""

    def test_passed(self):
        r = AgentResult(agent_name="test", passed=True)
        assert r.passed is True
        assert r.confidence == 1.0

    def test_failed(self):
        r = AgentResult(agent_name="test", passed=False)
        assert r.passed is False

    def test_with_issues(self):
        issues = [
            AuditIssue(agent="a", code="c", severity=AuditSeverity.HIGH, message="m")
        ]
        r = AgentResult(agent_name="test", passed=False, issues=issues)
        assert len(r.issues) == 1


# ── AuditResult ──────────────────────────

class TestAuditResult:
    """統合結果データクラスのテスト"""

    @pytest.fixture
    def target(self):
        return AuditTarget(content="test")

    def test_default_passed(self, target):
        r = AuditResult(target=target)
        assert r.passed is True

    def test_all_issues_aggregation(self, target):
        issue1 = AuditIssue(agent="a", code="c1", severity=AuditSeverity.HIGH, message="m1")
        issue2 = AuditIssue(agent="b", code="c2", severity=AuditSeverity.LOW, message="m2")
        r = AuditResult(
            target=target,
            agent_results=[
                AgentResult(agent_name="a", passed=False, issues=[issue1]),
                AgentResult(agent_name="b", passed=True, issues=[issue2]),
            ],
        )
        assert len(r.all_issues) == 2

    def test_critical_count(self, target):
        issue = AuditIssue(agent="a", code="c", severity=AuditSeverity.CRITICAL, message="m")
        r = AuditResult(
            target=target,
            agent_results=[AgentResult(agent_name="a", passed=False, issues=[issue])],
        )
        assert r.critical_count == 1

    def test_high_count(self, target):
        issue = AuditIssue(agent="a", code="c", severity=AuditSeverity.HIGH, message="m")
        r = AuditResult(
            target=target,
            agent_results=[AgentResult(agent_name="a", passed=False, issues=[issue])],
        )
        assert r.high_count == 1

    def test_no_issues(self, target):
        r = AuditResult(target=target, agent_results=[])
        assert r.critical_count == 0
        assert r.high_count == 0
        assert len(r.all_issues) == 0


# ── Poiēsis Agents ───────────────────────

class TestPoiesisAgents:
    """生成層エージェントのテスト"""

    @pytest.fixture
    def target(self):
        return AuditTarget(
            content="This is test content for auditing.",
            target_type=AuditTargetType.GENERIC,
        )

    def test_ousia_agent_exists(self):
        agent = OusiaAgent()
        assert agent.name is not None

    def test_ousia_agent_audits(self, target):
        agent = OusiaAgent()
        result = agent.audit(target)
        assert isinstance(result, AgentResult)

    def test_schema_agent_exists(self):
        agent = SchemaAgent()
        assert agent.name is not None

    def test_schema_agent_audits(self, target):
        agent = SchemaAgent()
        result = agent.audit(target)
        assert isinstance(result, AgentResult)

    def test_horme_agent_exists(self):
        agent = HormeAgent()
        assert agent.name is not None

    def test_horme_agent_audits(self, target):
        agent = HormeAgent()
        result = agent.audit(target)
        assert isinstance(result, AgentResult)


# ── Dokimasia Agents ─────────────────────

class TestDokimasiaAgents:
    """審査層エージェントのテスト"""

    @pytest.fixture
    def target(self):
        return AuditTarget(
            content="/noe+_/dia*~/s+",
            target_type=AuditTargetType.CCL_OUTPUT,
        )

    def test_perigraphe_agent(self, target):
        result = PerigrapheAgent().audit(target)
        assert isinstance(result, AgentResult)

    def test_kairos_agent(self, target):
        result = KairosAgent().audit(target)
        assert isinstance(result, AgentResult)

    def test_operator_agent(self, target):
        result = OperatorAgent().audit(target)
        assert isinstance(result, AgentResult)

    def test_logic_agent(self, target):
        result = LogicAgent().audit(target)
        assert isinstance(result, AgentResult)

    def test_completeness_agent(self, target):
        result = CompletenessAgent().audit(target)
        assert isinstance(result, AgentResult)


# ── SynteleiaOrchestrator ────────────────

class TestOrchestrator:
    """オーケストレーターのテスト"""

    @pytest.fixture
    def target(self):
        return AuditTarget(
            content="Test content for orchestrator audit.",
            target_type=AuditTargetType.GENERIC,
        )

    def test_default_initialization(self):
        o = SynteleiaOrchestrator()
        assert len(o.poiesis_agents) == 3
        assert len(o.dokimasia_agents) == 5

    def test_total_agents(self):
        o = SynteleiaOrchestrator()
        assert len(o.agents) == 8

    def test_custom_agents(self):
        o = SynteleiaOrchestrator(
            poiesis_agents=[OusiaAgent()],
            dokimasia_agents=[LogicAgent()],
        )
        assert len(o.agents) == 2

    def test_audit_returns_result(self, target):
        o = SynteleiaOrchestrator(parallel=False)
        result = o.audit(target)
        assert isinstance(result, AuditResult)
        assert result.summary != ""

    def test_audit_parallel(self, target):
        o = SynteleiaOrchestrator(parallel=True)
        result = o.audit(target)
        assert isinstance(result, AuditResult)

    def test_audit_sequential(self, target):
        o = SynteleiaOrchestrator(parallel=False)
        result = o.audit(target)
        assert isinstance(result, AuditResult)

    def test_format_report(self, target):
        o = SynteleiaOrchestrator(parallel=False)
        result = o.audit(target)
        report = o.format_report(result)
        assert "Audit Report" in report
        assert "Target:" in report

    def test_all_passed_summary(self, target):
        o = SynteleiaOrchestrator(parallel=False)
        result = o.audit(target)
        if result.passed:
            assert "PASS" in result.summary

    def test_agents_property(self):
        o = SynteleiaOrchestrator()
        assert isinstance(o.agents, list)
        assert all(isinstance(a, AuditAgent) for a in o.agents)


# ── L2 SemanticAgent (StubBackend) ───────

class TestSemanticAgentStub:
    """L2 SemanticAgent の StubBackend テスト"""

    @pytest.fixture
    def stub_agent(self):
        from mekhane.synteleia.dokimasia.semantic_agent import SemanticAgent, StubBackend
        return SemanticAgent(backend=StubBackend())

    @pytest.fixture
    def target_clean(self):
        return AuditTarget(
            content="This is well-structured content with clear intent.",
            target_type=AuditTargetType.GENERIC,
        )

    @pytest.fixture
    def target_code(self):
        return AuditTarget(
            content="def process(data):\n    result = eval(data)\n    return result",
            target_type=AuditTargetType.CODE,
        )

    def test_stub_audit_returns_result(self, stub_agent, target_clean):
        result = stub_agent.audit(target_clean)
        assert isinstance(result, AgentResult)
        assert result.agent_name == "SemanticAgent"

    def test_stub_audit_passes_clean(self, stub_agent, target_clean):
        result = stub_agent.audit(target_clean)
        assert result.passed is True
        assert len(result.issues) == 0

    def test_stub_confidence_is_low(self, stub_agent, target_clean):
        """StubBackend の confidence は 0.5 (デフォルト) であるべき"""
        result = stub_agent.audit(target_clean)
        assert result.confidence <= 0.5

    def test_stub_metadata_has_backend(self, stub_agent, target_clean):
        result = stub_agent.audit(target_clean)
        assert result.metadata.get("backend") == "StubBackend"

    def test_stub_with_issues_response(self):
        """StubBackend に Issue 付き JSON を渡した場合"""
        import json
        from mekhane.synteleia.dokimasia.semantic_agent import SemanticAgent, StubBackend

        response = json.dumps({
            "issues": [
                {
                    "code": "SEM-001",
                    "severity": "high",
                    "message": "設計意図との不整合: 関数名が処理内容と一致しない",
                    "location": "line 1",
                    "suggestion": "関数名を process_data に変更",
                }
            ],
            "summary": "1 issue found",
            "confidence": 0.85,
        })
        agent = SemanticAgent(backend=StubBackend(response=response))
        target = AuditTarget(content="def foo(): pass", target_type=AuditTargetType.CODE)
        result = agent.audit(target)

        assert result.passed is False  # HIGH issue → not passed
        assert len(result.issues) == 1
        assert result.issues[0].code == "SEM-001"
        assert result.issues[0].severity == AuditSeverity.HIGH
        assert result.confidence == 0.85

    def test_supports_ccl_output(self, stub_agent):
        assert stub_agent.supports(AuditTargetType.CCL_OUTPUT) is True

    def test_supports_thought(self, stub_agent):
        assert stub_agent.supports(AuditTargetType.THOUGHT) is True

    def test_supports_plan(self, stub_agent):
        assert stub_agent.supports(AuditTargetType.PLAN) is True

    def test_not_supports_code(self, stub_agent):
        """SemanticAgent は CODE をサポートしない (L1 が担当)"""
        assert stub_agent.supports(AuditTargetType.CODE) is False

    def test_not_supports_proof(self, stub_agent):
        assert stub_agent.supports(AuditTargetType.PROOF) is False


# ── L2 parse_llm_response ────────────────

class TestParseLlmResponse:
    """LLM レスポンスパーサーのテスト"""

    def test_json_response(self):
        import json
        from mekhane.synteleia.dokimasia.semantic_agent import parse_llm_response

        response = json.dumps({
            "issues": [
                {"code": "SEM-002", "severity": "medium", "message": "暗黙の前提あり"},
                {"code": "SEM-004", "severity": "high", "message": "論理の飛躍"},
            ],
            "summary": "2 issues",
            "confidence": 0.9,
        })
        issues = parse_llm_response(response, "SemanticAgent")
        assert len(issues) == 2
        assert issues[0].code == "SEM-002"
        assert issues[1].severity == AuditSeverity.HIGH

    def test_empty_issues(self):
        import json
        from mekhane.synteleia.dokimasia.semantic_agent import parse_llm_response

        response = json.dumps({"issues": [], "summary": "Clean", "confidence": 0.95})
        issues = parse_llm_response(response, "SemanticAgent")
        assert len(issues) == 0

    def test_markdown_fallback(self):
        from mekhane.synteleia.dokimasia.semantic_agent import parse_llm_response

        response = "- [HIGH] SEM-001: 設計意図との不整合\n- [LOW] SEM-005: 過度な抽象化"
        issues = parse_llm_response(response, "SemanticAgent")
        assert len(issues) == 2
        assert issues[0].severity == AuditSeverity.HIGH

    def test_invalid_json_returns_empty(self):
        from mekhane.synteleia.dokimasia.semantic_agent import parse_llm_response

        issues = parse_llm_response("not json at all", "SemanticAgent")
        assert len(issues) == 0


# ── L2 Backend availability ─────────────

class TestBackendAvailability:
    """各 Backend の is_available テスト"""

    def test_stub_always_available(self):
        from mekhane.synteleia.dokimasia.semantic_agent import StubBackend
        assert StubBackend().is_available() is True

    def test_openai_availability_depends_on_env(self):
        from mekhane.synteleia.dokimasia.semantic_agent import OpenAIBackend
        import os
        backend = OpenAIBackend()
        expected = bool(os.environ.get("OPENAI_API_KEY"))
        assert backend.is_available() == expected


# ── L2 Orchestrator Integration ──────────

class TestOrchestratorWithL2:
    """with_l2() 統合テスト"""

    @pytest.fixture
    def target(self):
        return AuditTarget(
            content="Synteleia monitors agent outputs for quality.",
            target_type=AuditTargetType.GENERIC,
        )

    def test_with_l2_creates_orchestrator(self):
        o = SynteleiaOrchestrator.with_l2()
        assert isinstance(o, SynteleiaOrchestrator)

    def test_with_l2_has_more_agents(self):
        o_l1 = SynteleiaOrchestrator()
        o_l2 = SynteleiaOrchestrator.with_l2()
        assert len(o_l2.dokimasia_agents) == len(o_l1.dokimasia_agents) + 1

    def test_with_l2_includes_semantic_agent(self):
        from mekhane.synteleia.dokimasia.semantic_agent import SemanticAgent
        o = SynteleiaOrchestrator.with_l2()
        semantic_agents = [a for a in o.dokimasia_agents if isinstance(a, SemanticAgent)]
        assert len(semantic_agents) == 1

    def test_with_l2_audit_runs(self, target):
        o = SynteleiaOrchestrator.with_l2()
        result = o.audit(target)
        assert isinstance(result, AuditResult)

    def test_with_l2_report_includes_semantic(self, target):
        o = SynteleiaOrchestrator.with_l2()
        result = o.audit(target)
        report = o.format_report(result)
        assert "SemanticAgent" in report

    def test_with_l2_wbc_alert_on_clean(self, target):
        """クリーンな入力では WBC アラートは None"""
        o = SynteleiaOrchestrator.with_l2()
        result = o.audit(target)
        alert = o.to_wbc_alert(result)
        # StubBackend はクリーンなので alert は None のはず
        if result.passed:
            assert alert is None
