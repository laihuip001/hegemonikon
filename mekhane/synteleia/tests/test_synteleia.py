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
