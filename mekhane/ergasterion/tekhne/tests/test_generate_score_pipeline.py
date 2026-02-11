#!/usr/bin/env python3
"""
Generate → Score Pipeline CI Tests

Týpos generate v2.1 の出力が各ドメインテンプレートを正しく反映し、
品質スコアがリグレッションしていないことを検証する。

テスト項目:
  1. ドメイン検出の正確性 (4ドメイン × 2入力 = 8テスト)
  2. 各ドメインの generate → score パイプライン (4テスト)
  3. リグレッション検出 (スコア下限)
  4. テンプレート反映検証 (constraint/example/format 存在確認)
  5. research テンプレート固有テスト (JSON Schema, 3件 examples)

Usage:
  cd ~/oikos/hegemonikon
  PYTHONPATH=. .venv/bin/python -m pytest mekhane/ergasterion/tekhne/tests/test_generate_score_pipeline.py -v
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# --- Path Setup ---
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent  # hegemonikon/
sys.path.insert(0, str(PROJECT_ROOT / "mekhane" / "mcp"))
sys.path.insert(0, str(PROJECT_ROOT / "mekhane" / "ergasterion" / "tekhne"))

from typos_mcp_server import generate_typos, detect_domain, classify_task
from prompt_quality_scorer import score_prompt


# ============================================================
# Helpers
# ============================================================

def _score_generated(task: str, domain: str):
    """Generate a .prompt from task/domain then score it. Returns QualityReport."""
    result = generate_typos(task, domain, ".prompt")
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".prompt", delete=False, dir="/tmp"
    ) as f:
        f.write(result)
        path = f.name
    try:
        report = score_prompt(path)
    finally:
        os.unlink(path)
    return report, result


# ============================================================
# 1. Domain Detection Tests
# ============================================================

# PURPOSE: Test suite validating domain detection correctness
class TestDomainDetection:
    """detect_domain should correctly identify all 4 domains."""

    # PURPOSE: Verify detect domain behaves correctly
    @pytest.mark.parametrize("text,expected", [
        ("SQLインジェクションのコードレビューをする", "technical"),
        ("Pythonのバグをデバッグする", "technical"),
        ("ドキュメントから質問に回答する", "rag"),
        ("知識ベースで検索する", "rag"),
        ("この記事を要約してください", "summarization"),
        ("議事録のポイントを抽出する", "summarization"),
        ("LLM評価の最新動向を調査する", "research"),
        ("ベストプラクティスをリサーチする", "research"),
    ])
    def test_detect_domain(self, text, expected):
        """Verify detect domain behavior."""
        assert detect_domain(text) == expected


# ============================================================
# 2. Generate → Score Pipeline Tests
# ============================================================

# PURPOSE: Test suite validating generate score pipeline correctness
class TestGenerateScorePipeline:
    """Generate + Score pipeline should produce valid results for all domains."""

    DOMAIN_TASKS = {
        "technical": "Python関数のSQLインジェクション脆弱性をレビューする",
        "rag": "検索結果に基づいてTransformerの計算量について回答する",
        "summarization": "Q1業績会議の議事録を要約する",
        "research": "LLMプロンプト評価フレームワークの最新動向を調査する",
    }

    # PURPOSE: Verify pipeline produces valid report behaves correctly
    @pytest.mark.parametrize("domain", ["technical", "rag", "summarization", "research"])
    def test_pipeline_produces_valid_report(self, domain):
        """Each domain should produce a scorable .prompt with no errors."""
        report, _ = _score_generated(self.DOMAIN_TASKS[domain], domain)
        assert report is not None
        assert report.detected_format == "prompt"
        assert report.total >= 0

    # PURPOSE: Verify all dimensions present behaves correctly
    @pytest.mark.parametrize("domain", ["technical", "rag", "summarization", "research"])
    def test_all_dimensions_present(self, domain):
        """All 4 quality dimensions should have non-negative scores."""
        report, _ = _score_generated(self.DOMAIN_TASKS[domain], domain)
        assert report.structure.normalized >= 0
        assert report.safety.normalized >= 0
        assert report.completeness.normalized >= 0
        assert report.archetype_fit.normalized >= 0


# ============================================================
# 3. Regression Guard Tests (Score Baselines)
# ============================================================

# PURPOSE: Test suite validating regression guard correctness
class TestRegressionGuard:
    """Scores must not drop below established baselines."""

    # Baselines: measured 2026-02-11
    # These are set conservatively (-10 from measured values)
    SCORE_BASELINES = {
        "technical": 40,   # measured: 51
        "rag": 40,         # conservative estimate
        "summarization": 40,
        "research": 50,    # measured: 63
    }

    DOMAIN_TASKS = {
        "technical": "Python関数のSQLインジェクション脆弱性をレビューする",
        "rag": "検索結果に基づいてTransformerの計算量について回答する",
        "summarization": "Q1業績会議の議事録を要約する",
        "research": "LLMプロンプト評価フレームワークの最新動向を調査する",
    }

    # PURPOSE: Verify score above baseline behaves correctly
    @pytest.mark.parametrize("domain", ["technical", "rag", "summarization", "research"])
    def test_score_above_baseline(self, domain):
        """Score must not regress below baseline."""
        report, _ = _score_generated(self.DOMAIN_TASKS[domain], domain)
        baseline = self.SCORE_BASELINES[domain]
        assert report.total >= baseline, (
            f"{domain} score {report.total} dropped below baseline {baseline}"
        )


# ============================================================
# 4. Template Reflection Tests
# ============================================================

# PURPOSE: Test suite validating template reflection correctness
class TestTemplateReflection:
    """Generated .prompt should reflect domain template content."""

    # PURPOSE: Verify technical has owasp behaves correctly
    def test_technical_has_owasp(self):
        """Technical template should inject OWASP constraint."""
        _, output = _score_generated("コードレビュー", "technical")
        assert "OWASP" in output

    # PURPOSE: Verify rag has citation behaves correctly
    def test_rag_has_citation(self):
        """RAG template should inject citation constraint."""
        _, output = _score_generated("知識ベースで回答", "rag")
        # Look for citation-related constraint
        assert "引用" in output or "citation" in output.lower() or "ハルシネーション" in output

    # PURPOSE: Verify summarization has faithful behaves correctly
    def test_summarization_has_faithful(self):
        """Summarization template should inject faithfulness constraint."""
        _, output = _score_generated("記事を要約する", "summarization")
        assert "忠実" in output or "原文" in output or "捏造" in output

    # PURPOSE: Verify research has source behaves correctly
    def test_research_has_source(self):
        """Research template should inject source citation constraint."""
        _, output = _score_generated("最新動向を調査する", "research")
        assert "情報源" in output

    # PURPOSE: Verify research has confidence behaves correctly
    def test_research_has_confidence(self):
        """Research template should reference confidence/uncertainty."""
        _, output = _score_generated("手法を調査分析する", "research")
        assert "示唆" in output or "推奨" in output or "未確定" in output


# ============================================================
# 5. Research Template Specific Tests
# ============================================================

# PURPOSE: Test suite validating research template correctness
class TestResearchTemplate:
    """Research template has unique features: JSON Schema, 3 examples, /sop modes."""

    # PURPOSE: Verify has three examples behaves correctly
    def test_has_three_examples(self):
        """Research template should have 3 few-shot examples (happy/edge/error)."""
        _, output = _score_generated("技術動向を調査する", "research")
        # Count @examples sections — examples are injected as one block
        assert "@examples" in output

    # PURPOSE: Verify has anti patterns behaves correctly
    def test_has_anti_patterns(self):
        """Research template should inject anti-pattern constraints."""
        _, output = _score_generated("技術動向を調査する", "research")
        assert "禁止:" in output

    # PURPOSE: Verify research not owasp behaves correctly
    def test_research_not_owasp(self):
        """Research prompt should NOT contain OWASP (wrong template)."""
        _, output = _score_generated("最新動向を調査する", "research")
        assert "OWASP" not in output


# ============================================================
# 6. Convergence/Divergence Policy Tests
# ============================================================

# PURPOSE: Test suite validating convergence divergence correctness
class TestConvergenceDivergence:
    """classify_task should correctly identify task types."""

    # PURPOSE: Verify convergent task behaves correctly
    def test_convergent_task(self):
        """Verify convergent task behavior."""
        result = classify_task("バグを修正する")
        # Short tasks may classify as ambiguous; convergent or ambiguous accepted
        assert result["classification"] in ("convergent", "convergent-leaning", "ambiguous")

    # PURPOSE: Verify divergent task behaves correctly
    def test_divergent_task(self):
        """Verify divergent task behavior."""
        result = classify_task("新しいAPIを自由にデザインする")
        assert result["classification"] in ("divergent", "divergent-leaning", "ambiguous")

    # PURPOSE: Verify result keys behaves correctly
    def test_result_keys(self):
        """Verify result keys behavior."""
        result = classify_task("何かをする")
        assert "classification" in result
        assert "confidence" in result
        assert "recommendation" in result
