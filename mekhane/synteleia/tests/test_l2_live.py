#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/synteleia/tests/
# PURPOSE: L2 SemanticAgent 実弾テスト (OpenAI Backend)
"""L2 Live Fire Tests — OpenAI Backend で実 HGK ドキュメントを監査"""

import json
import os

import pytest

from mekhane.synteleia.base import (
    AgentResult,
    AuditIssue,
    AuditSeverity,
    AuditTarget,
    AuditTargetType,
)
from mekhane.synteleia.dokimasia.semantic_agent import (
    OpenAIBackend,
    SemanticAgent,
    parse_llm_response,
)

# All tests in this module require OPENAI_API_KEY
HAS_OPENAI = bool(os.environ.get("OPENAI_API_KEY"))
pytestmark = pytest.mark.skipif(not HAS_OPENAI, reason="OPENAI_API_KEY not set")


# ═══ Fixtures ═══════════════════════════════════════════════


@pytest.fixture(scope="module")
def backend():
    """OpenAI Backend (module scope for cost efficiency)"""
    return OpenAIBackend(model="gpt-4o-mini")


@pytest.fixture(scope="module")
def agent(backend):
    """SemanticAgent with OpenAI backend"""
    return SemanticAgent(backend=backend)


# ═══ Test 1: Backend Connectivity ═══════════════════════════


class TestOpenAIConnectivity:
    """OpenAI Backend 疎通テスト"""

    def test_backend_is_available(self, backend):
        """API key が設定されていれば利用可能"""
        assert backend.is_available()

    def test_backend_query_returns_json(self, backend):
        """簡単なクエリで JSON 応答を返す"""
        response = backend.query(
            prompt="Return a JSON object: {\"status\": \"ok\"}",
            context="ping",
        )
        data = json.loads(response)
        assert "status" in data


# ═══ Test 2: Real Document Audit ═══════════════════════════


# Intentionally clean HGK text — should produce no critical issues
CLEAN_HGK_TEXT = """\
Hegemonikón は FEP (Free Energy Principle) に基づく認知ハイパーバイザーフレームワークである。
7つの公理（FEP, Flow, Value, Scale, Function, Valence, Precision）から
24の定理を導出し、108の関係で相互接続する。
第零原則「意志より環境」: 自分を信じないことが最も信頼できる自分を作る。
"""


class TestRealDocumentAudit:
    """実 HGK ドキュメントの L2 監査"""

    def test_clean_document_audit(self, agent):
        """実ドキュメントの L2 監査が AgentResult を返す"""
        target = AuditTarget(
            content=CLEAN_HGK_TEXT,
            target_type=AuditTargetType.THOUGHT,
        )
        result = agent.audit(target)
        assert isinstance(result, AgentResult)
        assert result.agent_name == "SemanticAgent"
        assert result.confidence > 0.0
        assert result.metadata.get("backend") == "OpenAIBackend"
        assert result.metadata.get("l2") is True
        # LLM output is non-deterministic; verify structure not exact content
        for issue in result.issues:
            assert isinstance(issue, AuditIssue)
            assert issue.code.startswith("SEM-")
            assert issue.severity in (
                AuditSeverity.CRITICAL, AuditSeverity.HIGH,
                AuditSeverity.MEDIUM, AuditSeverity.LOW,
                AuditSeverity.INFO,
            )


# ═══ Test 3: Intentional Defect Detection ═══════════════════


DEFECTIVE_TEXT = """\
## 目的
Hegemonikón は美しいフレームワークである。

## 構造
24の定理はそれぞれ独立に機能する。
FEP は必要ないが、念のため採用した。
直感的に正しいので、数学的な証明は省略する。
"""


class TestDefectDetection:
    """意図的欠陥文書の SEM 検出テスト"""

    def test_detects_semantic_issues(self, agent):
        """論理飛躍・設計不整合を含む文書から issues を検出"""
        target = AuditTarget(
            content=DEFECTIVE_TEXT,
            target_type=AuditTargetType.THOUGHT,
        )
        result = agent.audit(target)
        assert isinstance(result, AgentResult)
        # Defective text should produce at least one issue
        assert len(result.issues) >= 1, "Expected at least 1 issue for defective text"
        # Should detect relevant SEM codes
        codes = {i.code for i in result.issues}
        # At least one of the expected issues should be detected
        expected_any = {"SEM-001", "SEM-004", "SEM-005"}
        assert codes & expected_any, f"Expected at least one of {expected_any}, got {codes}"

    def test_defective_has_lower_pass_or_issues(self, agent):
        """欠陥文書は clean 文書と異なる結果を返す"""
        clean_target = AuditTarget(
            content=CLEAN_HGK_TEXT, target_type=AuditTargetType.THOUGHT,
        )
        defective_target = AuditTarget(
            content=DEFECTIVE_TEXT, target_type=AuditTargetType.THOUGHT,
        )
        clean_result = agent.audit(clean_target)
        defective_result = agent.audit(defective_target)
        # Defective should have more issues or lower pass rate
        assert (
            len(defective_result.issues) > len(clean_result.issues)
            or defective_result.passed != clean_result.passed
        ), "L2 should distinguish clean from defective text"
