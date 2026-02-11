"""
Tests for SemanticAgent (L2)
"""

import json
import pytest

from mekhane.synteleia.base import (
    AuditIssue,
    AuditSeverity,
    AuditTarget,
    AuditTargetType,
)
from mekhane.synteleia.dokimasia.semantic_agent import (
    LMQLBackend,
    SemanticAgent,
    StubBackend,
    parse_llm_response,
    _parse_severity,
)


# =============================================================================
# parse_llm_response tests
# =============================================================================


# PURPOSE: Test suite validating parse l l m response correctness
class TestParseLLMResponse:
    """LLM レスポンスパーサーのテスト"""

    # PURPOSE: Verify parse json response behaves correctly
    def test_parse_json_response(self):
        """JSON 形式のレスポンスをパースできる"""
        response = json.dumps(
            {
                "issues": [
                    {
                        "code": "SEM-001",
                        "severity": "high",
                        "message": "設計意図との不整合",
                        "location": "paragraph 2",
                        "suggestion": "目的を明確化",
                    }
                ],
                "summary": "1件検出",
                "confidence": 0.85,
            }
        )
        issues = parse_llm_response(response, "TestAgent")
        assert len(issues) == 1
        assert issues[0].code == "SEM-001"
        assert issues[0].severity == AuditSeverity.HIGH
        assert issues[0].message == "設計意図との不整合"
        assert issues[0].location == "paragraph 2"
        assert issues[0].suggestion == "目的を明確化"

    # PURPOSE: Verify parse json no issues behaves correctly
    def test_parse_json_no_issues(self):
        """問題なしの JSON レスポンス"""
        response = json.dumps(
            {"issues": [], "summary": "No issues", "confidence": 0.9}
        )
        issues = parse_llm_response(response, "TestAgent")
        assert len(issues) == 0

    # PURPOSE: Verify parse json multiple issues behaves correctly
    def test_parse_json_multiple_issues(self):
        """複数の問題を含む JSON レスポンス"""
        response = json.dumps(
            {
                "issues": [
                    {"code": "SEM-001", "severity": "critical", "message": "致命的"},
                    {"code": "SEM-002", "severity": "low", "message": "軽微"},
                ],
                "summary": "2件",
                "confidence": 0.75,
            }
        )
        issues = parse_llm_response(response, "TestAgent")
        assert len(issues) == 2
        assert issues[0].severity == AuditSeverity.CRITICAL
        assert issues[1].severity == AuditSeverity.LOW

    # PURPOSE: Verify parse markdown fallback behaves correctly
    def test_parse_markdown_fallback(self):
        """Markdown リスト形式のフォールバックパース"""
        response = "- [HIGH] SEM-001: 設計意図との不整合が検出されました\n- [LOW] SEM-002: 前提条件が不明確です"
        issues = parse_llm_response(response, "TestAgent")
        assert len(issues) == 2
        assert issues[0].code == "SEM-001"
        assert issues[0].severity == AuditSeverity.HIGH
        assert issues[1].code == "SEM-002"

    # PURPOSE: Verify parse unparseable response behaves correctly
    def test_parse_unparseable_response(self):
        """パースできないレスポンスは空リスト"""
        response = "This is just plain text without any structured output."
        issues = parse_llm_response(response, "TestAgent")
        assert len(issues) == 0

    # PURPOSE: Verify parse severity behaves correctly
    def test_parse_severity(self):
        """severity 文字列変換"""
        assert _parse_severity("critical") == AuditSeverity.CRITICAL
        assert _parse_severity("HIGH") == AuditSeverity.HIGH
        assert _parse_severity("medium") == AuditSeverity.MEDIUM
        assert _parse_severity("low") == AuditSeverity.LOW
        assert _parse_severity("info") == AuditSeverity.INFO
        assert _parse_severity("unknown") == AuditSeverity.MEDIUM  # default


# =============================================================================
# StubBackend tests
# =============================================================================


# PURPOSE: Test suite validating stub backend correctness
class TestStubBackend:
    """スタブバックエンドのテスト"""

    # PURPOSE: Verify default response behaves correctly
    def test_default_response(self):
        """デフォルトレスポンス（問題なし）"""
        backend = StubBackend()
        response = backend.query("prompt", "context")
        data = json.loads(response)
        assert data["issues"] == []
        assert backend.is_available()

    # PURPOSE: Verify custom response behaves correctly
    def test_custom_response(self):
        """カスタムレスポンス"""
        custom = json.dumps(
            {
                "issues": [
                    {"code": "SEM-001", "severity": "high", "message": "test issue"}
                ]
            }
        )
        backend = StubBackend(response=custom)
        response = backend.query("prompt", "context")
        data = json.loads(response)
        assert len(data["issues"]) == 1


# =============================================================================
# SemanticAgent tests
# =============================================================================


# PURPOSE: Test suite validating semantic agent correctness
class TestSemanticAgent:
    """SemanticAgent のテスト"""

    # PURPOSE: Verify stub no issues behaves correctly
    def test_stub_no_issues(self):
        """スタブモードで問題なし"""
        agent = SemanticAgent(backend=StubBackend())
        target = AuditTarget(content="This is a valid document.", source="test.md")
        result = agent.audit(target)
        assert result.passed
        assert result.agent_name == "SemanticAgent"
        assert result.metadata.get("backend") == "StubBackend"
        assert result.metadata.get("l2") is True

    # PURPOSE: Verify stub with issues behaves correctly
    def test_stub_with_issues(self):
        """スタブモードで問題検出"""
        response = json.dumps(
            {
                "issues": [
                    {
                        "code": "SEM-001",
                        "severity": "high",
                        "message": "Design intent mismatch",
                    }
                ],
                "confidence": 0.8,
            }
        )
        agent = SemanticAgent(backend=StubBackend(response=response))
        target = AuditTarget(content="Problematic content")
        result = agent.audit(target)
        assert not result.passed  # HIGH issue → not passed
        assert len(result.issues) == 1
        assert result.issues[0].code == "SEM-001"

    # PURPOSE: Verify stub critical issue behaves correctly
    def test_stub_critical_issue(self):
        """CRITICAL 検出時は passed=False"""
        response = json.dumps(
            {
                "issues": [
                    {
                        "code": "SEM-003",
                        "severity": "critical",
                        "message": "Critical issue",
                    }
                ],
                "confidence": 0.9,
            }
        )
        agent = SemanticAgent(backend=StubBackend(response=response))
        result = agent.audit(AuditTarget(content="test"))
        assert not result.passed
        assert result.issues[0].severity == AuditSeverity.CRITICAL

    # PURPOSE: Verify error handling behaves correctly
    def test_error_handling(self):
        """エラー時のフォールバック"""

        # PURPOSE: Test suite validating error backend correctness
        class ErrorBackend(StubBackend):
            """Test suite for error backend."""
            # PURPOSE: Verify query behaves correctly
            def query(self, prompt, context):
                """Verify query behavior."""
                raise RuntimeError("LLM connection failed")

        agent = SemanticAgent(backend=ErrorBackend())
        result = agent.audit(AuditTarget(content="test"))
        assert result.passed  # エラー時は安全側（passed=True）
        assert result.confidence == 0.0
        assert any(i.code == "SEM-ERR" for i in result.issues)

    # PURPOSE: Verify supports text types behaves correctly
    def test_supports_text_types(self):
        """テキスト系ターゲットのみサポート"""
        agent = SemanticAgent(backend=StubBackend())
        assert agent.supports(AuditTargetType.CCL_OUTPUT)
        assert agent.supports(AuditTargetType.THOUGHT)
        assert agent.supports(AuditTargetType.PLAN)
        assert agent.supports(AuditTargetType.GENERIC)
        assert not agent.supports(AuditTargetType.CODE)  # コードは L1 が担当

    # PURPOSE: Verify confidence extraction behaves correctly
    def test_confidence_extraction(self):
        """レスポンスから confidence が抽出される"""
        response = json.dumps(
            {"issues": [], "confidence": 0.92}
        )
        agent = SemanticAgent(backend=StubBackend(response=response))
        result = agent.audit(AuditTarget(content="test"))
        assert result.confidence == 0.92


# =============================================================================
# Integration with Orchestrator
# =============================================================================


# PURPOSE: Test suite validating orchestrator integration correctness
class TestOrchestratorIntegration:
    """オーケストレータとの統合テスト"""

    # PURPOSE: Verify semantic agent in orchestrator behaves correctly
    def test_semantic_agent_in_orchestrator(self):
        """SemanticAgent をオーケストレータに組み込める"""
        from mekhane.synteleia.orchestrator import SynteleiaOrchestrator

        agent = SemanticAgent(backend=StubBackend())
        orchestrator = SynteleiaOrchestrator(
            poiesis_agents=[],
            dokimasia_agents=[agent],
            parallel=False,
        )
        target = AuditTarget(content="Test content for L2 audit")
        result = orchestrator.audit(target)
        assert result is not None
        assert len(result.agent_results) == 1
        assert result.agent_results[0].agent_name == "SemanticAgent"

    # PURPOSE: Verify l1 l2 combined behaves correctly
    def test_l1_l2_combined(self):
        """L1 + L2 の統合実行"""
        from mekhane.synteleia.dokimasia.logic_agent import LogicAgent
        from mekhane.synteleia.orchestrator import SynteleiaOrchestrator

        orchestrator = SynteleiaOrchestrator(
            poiesis_agents=[],
            dokimasia_agents=[LogicAgent(), SemanticAgent(backend=StubBackend())],
            parallel=False,
        )
        target = AuditTarget(content="if True: pass")
        result = orchestrator.audit(target)
        assert len(result.agent_results) == 2
        agent_names = [r.agent_name for r in result.agent_results]
        assert "LogicAgent" in agent_names
        assert "SemanticAgent" in agent_names
