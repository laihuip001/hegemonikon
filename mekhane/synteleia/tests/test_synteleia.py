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

# PURPOSE: Test suite validating audit severity correctness
class TestAuditSeverity:
    """重大度 Enum のテスト"""

    # PURPOSE: Verify all levels behaves correctly
    def test_all_levels(self):
        """Verify all levels behavior."""
        levels = [s.value for s in AuditSeverity]
        assert "critical" in levels
        assert "high" in levels
        assert "medium" in levels
        assert "low" in levels
        assert "info" in levels

    # PURPOSE: Verify count behaves correctly
    def test_count(self):
        """Verify count behavior."""
        assert len(AuditSeverity) == 5


# ── AuditTargetType ──────────────────────

# PURPOSE: Test suite validating audit target type correctness
class TestAuditTargetType:
    """監査対象種類 Enum のテスト"""

    # PURPOSE: Verify ccl output behaves correctly
    def test_ccl_output(self):
        """Verify ccl output behavior."""
        assert AuditTargetType.CCL_OUTPUT.value == "ccl_output"

    # PURPOSE: Verify code behaves correctly
    def test_code(self):
        """Verify code behavior."""
        assert AuditTargetType.CODE.value == "code"

    # PURPOSE: Verify all types behaves correctly
    def test_all_types(self):
        """Verify all types behavior."""
        types = [t.value for t in AuditTargetType]
        assert "thought" in types
        assert "plan" in types
        assert "proof" in types
        assert "generic" in types


# ── AuditTarget ──────────────────────────

# PURPOSE: Test suite validating audit target correctness
class TestAuditTarget:
    """監査対象データクラスのテスト"""

    # PURPOSE: Verify create generic behaves correctly
    def test_create_generic(self):
        """Verify create generic behavior."""
        t = AuditTarget(content="test content")
        assert t.target_type == AuditTargetType.GENERIC
        assert t.content == "test content"

    # PURPOSE: Verify create with type behaves correctly
    def test_create_with_type(self):
        """Verify create with type behavior."""
        t = AuditTarget(content="x", target_type=AuditTargetType.CODE)
        assert t.target_type == AuditTargetType.CODE

    # PURPOSE: Verify metadata default behaves correctly
    def test_metadata_default(self):
        """Verify metadata default behavior."""
        t = AuditTarget(content="x")
        assert t.metadata == {}

    # PURPOSE: Verify source default none behaves correctly
    def test_source_default_none(self):
        """Verify source default none behavior."""
        t = AuditTarget(content="x")
        assert t.source is None


# ── AuditIssue ───────────────────────────

# PURPOSE: Test suite validating audit issue correctness
class TestAuditIssue:
    """監査問題データクラスのテスト"""

    # PURPOSE: Verify create issue behaves correctly
    def test_create_issue(self):
        """Verify create issue behavior."""
        i = AuditIssue(
            agent="TestAgent",
            code="TEST-001",
            severity=AuditSeverity.MEDIUM,
            message="Test issue",
        )
        assert i.code == "TEST-001"
        assert i.severity == AuditSeverity.MEDIUM

    # PURPOSE: Verify with suggestion behaves correctly
    def test_with_suggestion(self):
        """Verify with suggestion behavior."""
        i = AuditIssue(
            agent="A", code="C", severity=AuditSeverity.LOW,
            message="msg", suggestion="fix this",
        )
        assert i.suggestion == "fix this"


# ── AgentResult ──────────────────────────

# PURPOSE: Test suite validating agent result correctness
class TestAgentResult:
    """エージェント結果データクラスのテスト"""

    # PURPOSE: Verify passed behaves correctly
    def test_passed(self):
        """Verify passed behavior."""
        r = AgentResult(agent_name="test", passed=True)
        assert r.passed is True
        assert r.confidence == 1.0

    # PURPOSE: Verify failed behaves correctly
    def test_failed(self):
        """Verify failed behavior."""
        r = AgentResult(agent_name="test", passed=False)
        assert r.passed is False

    # PURPOSE: Verify with issues behaves correctly
    def test_with_issues(self):
        """Verify with issues behavior."""
        issues = [
            AuditIssue(agent="a", code="c", severity=AuditSeverity.HIGH, message="m")
        ]
        r = AgentResult(agent_name="test", passed=False, issues=issues)
        assert len(r.issues) == 1


# ── AuditResult ──────────────────────────

# PURPOSE: Test suite validating audit result correctness
class TestAuditResult:
    """統合結果データクラスのテスト"""

    # PURPOSE: Verify target behaves correctly
    @pytest.fixture
    def target(self):
        """Verify target behavior."""
        return AuditTarget(content="test")

    # PURPOSE: Verify default passed behaves correctly
    def test_default_passed(self, target):
        """Verify default passed behavior."""
        r = AuditResult(target=target)
        assert r.passed is True

    # PURPOSE: Verify all issues aggregation behaves correctly
    def test_all_issues_aggregation(self, target):
        """Verify all issues aggregation behavior."""
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

    # PURPOSE: Verify critical count behaves correctly
    def test_critical_count(self, target):
        """Verify critical count behavior."""
        issue = AuditIssue(agent="a", code="c", severity=AuditSeverity.CRITICAL, message="m")
        r = AuditResult(
            target=target,
            agent_results=[AgentResult(agent_name="a", passed=False, issues=[issue])],
        )
        assert r.critical_count == 1

    # PURPOSE: Verify high count behaves correctly
    def test_high_count(self, target):
        """Verify high count behavior."""
        issue = AuditIssue(agent="a", code="c", severity=AuditSeverity.HIGH, message="m")
        r = AuditResult(
            target=target,
            agent_results=[AgentResult(agent_name="a", passed=False, issues=[issue])],
        )
        assert r.high_count == 1

    # PURPOSE: Verify no issues behaves correctly
    def test_no_issues(self, target):
        """Verify no issues behavior."""
        r = AuditResult(target=target, agent_results=[])
        assert r.critical_count == 0
        assert r.high_count == 0
        assert len(r.all_issues) == 0


# ── Poiēsis Agents ───────────────────────

# PURPOSE: Test suite validating poiesis agents correctness
class TestPoiesisAgents:
    """生成層エージェントのテスト"""

    # PURPOSE: Verify target behaves correctly
    @pytest.fixture
    def target(self):
        """Verify target behavior."""
        return AuditTarget(
            content="This is test content for auditing.",
            target_type=AuditTargetType.GENERIC,
        )

    # PURPOSE: Verify ousia agent exists behaves correctly
    def test_ousia_agent_exists(self):
        """Verify ousia agent exists behavior."""
        agent = OusiaAgent()
        assert agent.name is not None

    # PURPOSE: Verify ousia agent audits behaves correctly
    def test_ousia_agent_audits(self, target):
        """Verify ousia agent audits behavior."""
        agent = OusiaAgent()
        result = agent.audit(target)
        assert isinstance(result, AgentResult)

    # PURPOSE: Verify schema agent exists behaves correctly
    def test_schema_agent_exists(self):
        """Verify schema agent exists behavior."""
        agent = SchemaAgent()
        assert agent.name is not None

    # PURPOSE: Verify schema agent audits behaves correctly
    def test_schema_agent_audits(self, target):
        """Verify schema agent audits behavior."""
        agent = SchemaAgent()
        result = agent.audit(target)
        assert isinstance(result, AgentResult)

    # PURPOSE: Verify horme agent exists behaves correctly
    def test_horme_agent_exists(self):
        """Verify horme agent exists behavior."""
        agent = HormeAgent()
        assert agent.name is not None

    # PURPOSE: Verify horme agent audits behaves correctly
    def test_horme_agent_audits(self, target):
        """Verify horme agent audits behavior."""
        agent = HormeAgent()
        result = agent.audit(target)
        assert isinstance(result, AgentResult)


# ── Dokimasia Agents ─────────────────────

# PURPOSE: Test suite validating dokimasia agents correctness
class TestDokimasiaAgents:
    """審査層エージェントのテスト"""

    # PURPOSE: Verify target behaves correctly
    @pytest.fixture
    def target(self):
        """Verify target behavior."""
        return AuditTarget(
            content="/noe+_/dia*~/s+",
            target_type=AuditTargetType.CCL_OUTPUT,
        )

    # PURPOSE: Verify perigraphe agent behaves correctly
    def test_perigraphe_agent(self, target):
        """Verify perigraphe agent behavior."""
        result = PerigrapheAgent().audit(target)
        assert isinstance(result, AgentResult)

    # PURPOSE: Verify kairos agent behaves correctly
    def test_kairos_agent(self, target):
        """Verify kairos agent behavior."""
        result = KairosAgent().audit(target)
        assert isinstance(result, AgentResult)

    # PURPOSE: Verify operator agent behaves correctly
    def test_operator_agent(self, target):
        """Verify operator agent behavior."""
        result = OperatorAgent().audit(target)
        assert isinstance(result, AgentResult)

    # PURPOSE: Verify logic agent behaves correctly
    def test_logic_agent(self, target):
        """Verify logic agent behavior."""
        result = LogicAgent().audit(target)
        assert isinstance(result, AgentResult)

    # PURPOSE: Verify completeness agent behaves correctly
    def test_completeness_agent(self, target):
        """Verify completeness agent behavior."""
        result = CompletenessAgent().audit(target)
        assert isinstance(result, AgentResult)


# ── SynteleiaOrchestrator ────────────────

# PURPOSE: Test suite validating orchestrator correctness
class TestOrchestrator:
    """オーケストレーターのテスト"""

    # PURPOSE: Verify target behaves correctly
    @pytest.fixture
    def target(self):
        """Verify target behavior."""
        return AuditTarget(
            content="Test content for orchestrator audit.",
            target_type=AuditTargetType.GENERIC,
        )

    # PURPOSE: Verify default initialization behaves correctly
    def test_default_initialization(self):
        """Verify default initialization behavior."""
        o = SynteleiaOrchestrator()
        assert len(o.poiesis_agents) == 3
        assert len(o.dokimasia_agents) == 5

    # PURPOSE: Verify total agents behaves correctly
    def test_total_agents(self):
        """Verify total agents behavior."""
        o = SynteleiaOrchestrator()
        assert len(o.agents) == 8

    # PURPOSE: Verify custom agents behaves correctly
    def test_custom_agents(self):
        """Verify custom agents behavior."""
        o = SynteleiaOrchestrator(
            poiesis_agents=[OusiaAgent()],
            dokimasia_agents=[LogicAgent()],
        )
        assert len(o.agents) == 2

    # PURPOSE: Verify audit returns result behaves correctly
    def test_audit_returns_result(self, target):
        """Verify audit returns result behavior."""
        o = SynteleiaOrchestrator(parallel=False)
        result = o.audit(target)
        assert isinstance(result, AuditResult)
        assert result.summary != ""

    # PURPOSE: Verify audit parallel behaves correctly
    def test_audit_parallel(self, target):
        """Verify audit parallel behavior."""
        o = SynteleiaOrchestrator(parallel=True)
        result = o.audit(target)
        assert isinstance(result, AuditResult)

    # PURPOSE: Verify audit sequential behaves correctly
    def test_audit_sequential(self, target):
        """Verify audit sequential behavior."""
        o = SynteleiaOrchestrator(parallel=False)
        result = o.audit(target)
        assert isinstance(result, AuditResult)

    # PURPOSE: Verify format report behaves correctly
    def test_format_report(self, target):
        """Verify format report behavior."""
        o = SynteleiaOrchestrator(parallel=False)
        result = o.audit(target)
        report = o.format_report(result)
        assert "Audit Report" in report
        assert "Target:" in report

    # PURPOSE: Verify all passed summary behaves correctly
    def test_all_passed_summary(self, target):
        """Verify all passed summary behavior."""
        o = SynteleiaOrchestrator(parallel=False)
        result = o.audit(target)
        if result.passed:
            assert "PASS" in result.summary

    # PURPOSE: Verify agents property behaves correctly
    def test_agents_property(self):
        """Verify agents property behavior."""
        o = SynteleiaOrchestrator()
        assert isinstance(o.agents, list)
        assert all(isinstance(a, AuditAgent) for a in o.agents)


# ── L2 SemanticAgent (StubBackend) ───────

# PURPOSE: Test suite validating semantic agent stub correctness
class TestSemanticAgentStub:
    """L2 SemanticAgent の StubBackend テスト"""

    # PURPOSE: Verify stub agent behaves correctly
    @pytest.fixture
    def stub_agent(self):
        """Verify stub agent behavior."""
        from mekhane.synteleia.dokimasia.semantic_agent import SemanticAgent, StubBackend
        return SemanticAgent(backend=StubBackend())

    # PURPOSE: Verify target clean behaves correctly
    @pytest.fixture
    def target_clean(self):
        """Verify target clean behavior."""
        return AuditTarget(
            content="This is well-structured content with clear intent.",
            target_type=AuditTargetType.GENERIC,
        )

    # PURPOSE: Verify target code behaves correctly
    @pytest.fixture
    def target_code(self):
        """Verify target code behavior."""
        return AuditTarget(
            content="def process(data):\n    result = eval(data)\n    return result",
            target_type=AuditTargetType.CODE,
        )

    # PURPOSE: Verify stub audit returns result behaves correctly
    def test_stub_audit_returns_result(self, stub_agent, target_clean):
        """Verify stub audit returns result behavior."""
        result = stub_agent.audit(target_clean)
        assert isinstance(result, AgentResult)
        assert result.agent_name == "SemanticAgent"

    # PURPOSE: Verify stub audit passes clean behaves correctly
    def test_stub_audit_passes_clean(self, stub_agent, target_clean):
        """Verify stub audit passes clean behavior."""
        result = stub_agent.audit(target_clean)
        assert result.passed is True
        assert len(result.issues) == 0

    # PURPOSE: Verify stub confidence is low behaves correctly
    def test_stub_confidence_is_low(self, stub_agent, target_clean):
        """StubBackend の confidence は 0.5 (デフォルト) であるべき"""
        result = stub_agent.audit(target_clean)
        assert result.confidence <= 0.5

    # PURPOSE: Verify stub metadata has backend behaves correctly
    def test_stub_metadata_has_backend(self, stub_agent, target_clean):
        """Verify stub metadata has backend behavior."""
        result = stub_agent.audit(target_clean)
        assert result.metadata.get("backend") == "StubBackend"

    # PURPOSE: Verify stub with issues response behaves correctly
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

    # PURPOSE: Verify supports ccl output behaves correctly
    def test_supports_ccl_output(self, stub_agent):
        """Verify supports ccl output behavior."""
        assert stub_agent.supports(AuditTargetType.CCL_OUTPUT) is True

    # PURPOSE: Verify supports thought behaves correctly
    def test_supports_thought(self, stub_agent):
        """Verify supports thought behavior."""
        assert stub_agent.supports(AuditTargetType.THOUGHT) is True

    # PURPOSE: Verify supports plan behaves correctly
    def test_supports_plan(self, stub_agent):
        """Verify supports plan behavior."""
        assert stub_agent.supports(AuditTargetType.PLAN) is True

    # PURPOSE: Verify not supports code behaves correctly
    def test_not_supports_code(self, stub_agent):
        """SemanticAgent は CODE をサポートしない (L1 が担当)"""
        assert stub_agent.supports(AuditTargetType.CODE) is False

    # PURPOSE: Verify not supports proof behaves correctly
    def test_not_supports_proof(self, stub_agent):
        """Verify not supports proof behavior."""
        assert stub_agent.supports(AuditTargetType.PROOF) is False


# ── L2 parse_llm_response ────────────────

# PURPOSE: Test suite validating parse llm response correctness
class TestParseLlmResponse:
    """LLM レスポンスパーサーのテスト"""

    # PURPOSE: Verify json response behaves correctly
    def test_json_response(self):
        """Verify json response behavior."""
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

    # PURPOSE: Verify empty issues behaves correctly
    def test_empty_issues(self):
        """Verify empty issues behavior."""
        import json
        from mekhane.synteleia.dokimasia.semantic_agent import parse_llm_response

        response = json.dumps({"issues": [], "summary": "Clean", "confidence": 0.95})
        issues = parse_llm_response(response, "SemanticAgent")
        assert len(issues) == 0

    # PURPOSE: Verify markdown fallback behaves correctly
    def test_markdown_fallback(self):
        """Verify markdown fallback behavior."""
        from mekhane.synteleia.dokimasia.semantic_agent import parse_llm_response

        response = "- [HIGH] SEM-001: 設計意図との不整合\n- [LOW] SEM-005: 過度な抽象化"
        issues = parse_llm_response(response, "SemanticAgent")
        assert len(issues) == 2
        assert issues[0].severity == AuditSeverity.HIGH

    # PURPOSE: Verify invalid json returns empty behaves correctly
    def test_invalid_json_returns_empty(self):
        """Verify invalid json returns empty behavior."""
        from mekhane.synteleia.dokimasia.semantic_agent import parse_llm_response

        issues = parse_llm_response("not json at all", "SemanticAgent")
        assert len(issues) == 0


# ── L2 Backend availability ─────────────

# PURPOSE: Test suite validating backend availability correctness
class TestBackendAvailability:
    """各 Backend の is_available テスト"""

    # PURPOSE: Verify stub always available behaves correctly
    def test_stub_always_available(self):
        """Verify stub always available behavior."""
        from mekhane.synteleia.dokimasia.semantic_agent import StubBackend
        assert StubBackend().is_available() is True

    # PURPOSE: Verify openai availability depends on env behaves correctly
    def test_openai_availability_depends_on_env(self):
        """Verify openai availability depends on env behavior."""
        from mekhane.synteleia.dokimasia.semantic_agent import OpenAIBackend
        import os
        backend = OpenAIBackend()
        expected = bool(os.environ.get("OPENAI_API_KEY"))
        assert backend.is_available() == expected


# ── L2 Orchestrator Integration ──────────

# PURPOSE: Test suite validating orchestrator with l2 correctness
class TestOrchestratorWithL2:
    """with_l2() 統合テスト"""

    # PURPOSE: Verify target behaves correctly
    @pytest.fixture
    def target(self):
        """Verify target behavior."""
        return AuditTarget(
            content="Synteleia monitors agent outputs for quality.",
            target_type=AuditTargetType.GENERIC,
        )

    # PURPOSE: Verify with l2 creates orchestrator behaves correctly
    def test_with_l2_creates_orchestrator(self):
        """Verify with l2 creates orchestrator behavior."""
        o = SynteleiaOrchestrator.with_l2()
        assert isinstance(o, SynteleiaOrchestrator)

    # PURPOSE: Verify with l2 has more agents behaves correctly
    def test_with_l2_has_more_agents(self):
        """Verify with l2 has more agents behavior."""
        o_l1 = SynteleiaOrchestrator()
        o_l2 = SynteleiaOrchestrator.with_l2()
        assert len(o_l2.dokimasia_agents) == len(o_l1.dokimasia_agents) + 1

    # PURPOSE: Verify with l2 includes semantic agent behaves correctly
    def test_with_l2_includes_semantic_agent(self):
        """Verify with l2 includes semantic agent behavior."""
        from mekhane.synteleia.dokimasia.semantic_agent import SemanticAgent
        o = SynteleiaOrchestrator.with_l2()
        semantic_agents = [a for a in o.dokimasia_agents if isinstance(a, SemanticAgent)]
        assert len(semantic_agents) == 1

    # PURPOSE: Verify with l2 audit runs behaves correctly
    def test_with_l2_audit_runs(self, target):
        """Verify with l2 audit runs behavior."""
        o = SynteleiaOrchestrator.with_l2()
        result = o.audit(target)
        assert isinstance(result, AuditResult)

    # PURPOSE: Verify with l2 report includes semantic behaves correctly
    def test_with_l2_report_includes_semantic(self, target):
        """Verify with l2 report includes semantic behavior."""
        o = SynteleiaOrchestrator.with_l2()
        result = o.audit(target)
        report = o.format_report(result)
        assert "SemanticAgent" in report

    # PURPOSE: Verify with l2 wbc alert on clean behaves correctly
    def test_with_l2_wbc_alert_on_clean(self, target):
        """クリーンな入力では WBC アラートは None"""
        o = SynteleiaOrchestrator.with_l2()
        result = o.audit(target)
        alert = o.to_wbc_alert(result)
        # StubBackend はクリーンなので alert は None のはず
        if result.passed:
            assert alert is None
