"""UML Phase 2 — SEL 統合テスト"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import os

from mekhane.fep.metacognitive_layer import (
    UMLStage,
    UMLReport,
    STAGE_QUESTIONS,
    STAGE_TO_THEOREM,
    generate_prompt_injection,
    generate_pre_injection,
    generate_post_injection,
    run_full_uml,
)
from mekhane.ccl.sel_validator import (
    SELValidator,
    SELRequirement,
    SELValidationResult,
)
from mekhane.fep.uml_sel_bridge import (
    validate_with_uml,
    UMLSELResult,
)


# =============================================================================
# 1. generate_prompt_injection テスト
# =============================================================================


# PURPOSE: Phase 2 プロンプト注入テスト
class TestPromptInjection:
    """Phase 2 プロンプト注入テスト"""

    # PURPOSE: Pre-understanding プロンプトに O1 定理が含まれる
    def test_pre_understanding_has_theorem(self):
        """Pre-understanding プロンプトに O1 定理が含まれる"""
        prompt = generate_prompt_injection("noe", UMLStage.PRE_UNDERSTANDING)
        assert "O1" in prompt
        assert "Pre-check" in prompt

    # PURPOSE: Pre-intuition プロンプトに A1 定理が含まれる
    def test_pre_intuition_has_theorem(self):
        """Pre-intuition プロンプトに A1 定理が含まれる"""
        prompt = generate_prompt_injection("dia", UMLStage.PRE_INTUITION)
        assert "A1" in prompt
        assert "Pre-check" in prompt

    # PURPOSE: Post-evaluation プロンプトに A2 定理が含まれる
    def test_post_evaluation_has_theorem(self):
        """Post-evaluation プロンプトに A2 定理が含まれる"""
        prompt = generate_prompt_injection("dia", UMLStage.POST_EVALUATION)
        assert "A2" in prompt
        assert "Post-check" in prompt

    # PURPOSE: Post-decision プロンプトに O4 定理が含まれる
    def test_post_decision_has_theorem(self):
        """Post-decision プロンプトに O4 定理が含まれる"""
        prompt = generate_prompt_injection("ene", UMLStage.POST_DECISION)
        assert "O4" in prompt

    # PURPOSE: Post-confidence プロンプトに A4 定理が含まれる
    def test_post_confidence_has_theorem(self):
        """Post-confidence プロンプトに A4 定理が含まれる"""
        prompt = generate_prompt_injection("epi", UMLStage.POST_CONFIDENCE)
        assert "A4" in prompt
        assert "32.5%" in prompt or "過信" in prompt

    # PURPOSE: PRE_UNDERSTANDING にコンテキストが含まれる
    def test_context_included_for_understanding(self):
        """PRE_UNDERSTANDING にコンテキストが含まれる"""
        ctx = "FEPに基づく Active Inference の実装"
        prompt = generate_prompt_injection("noe", UMLStage.PRE_UNDERSTANDING, ctx)
        assert "FEP" in prompt
        assert "入力の要約" in prompt

    # PURPOSE: PRE_UNDERSTANDING 以外にはコンテキストが含まれない
    def test_context_not_included_for_other_stages(self):
        """PRE_UNDERSTANDING 以外にはコンテキストが含まれない"""
        ctx = "テストコンテキスト"
        prompt = generate_prompt_injection("dia", UMLStage.POST_EVALUATION, ctx)
        assert "入力の要約" not in prompt

    # PURPOSE: WF名がプロンプトに含まれる
    def test_wf_name_in_prompt(self):
        """WF名がプロンプトに含まれる"""
        prompt = generate_prompt_injection("noe", UMLStage.PRE_UNDERSTANDING)
        assert "/noe" in prompt

    # PURPOSE: 全5段階が有効なプロンプトを生成
    def test_all_stages_produce_valid_prompts(self):
        """全5段階が有効なプロンプトを生成"""
        for stage in UMLStage:
            prompt = generate_prompt_injection("test", stage)
            assert len(prompt) > 50, f"Stage {stage} produced too short prompt"
            assert "❓" in prompt, f"Stage {stage} missing question mark"

    # PURPOSE: Pre-injection は Stage 1+2 を結合
    def test_pre_injection_combines_stages(self):
        """Pre-injection は Stage 1+2 を結合"""
        result = generate_pre_injection("noe", "テスト入力")
        assert "O1" in result
        assert "A1" in result
        assert "Pre-check" in result

    # PURPOSE: Post-injection は Stage 3+4+5 を結合
    def test_post_injection_combines_stages(self):
        """Post-injection は Stage 3+4+5 を結合"""
        result = generate_post_injection("dia")
        assert "A2" in result
        assert "O4" in result
        assert "A4" in result
        assert "Post-check" in result


# =============================================================================
# 2. SEL uml_requirements テスト
# =============================================================================


# PURPOSE: SELRequirement の uml_requirements フィールドテスト
class TestSELUMLRequirements:
    """SELRequirement の uml_requirements フィールドテスト"""

    # PURPOSE: uml_requirements 付きの SELRequirement
    def test_requirement_with_uml(self):
        """uml_requirements 付きの SELRequirement"""
        req = SELRequirement(
            description="test",
            minimum_requirements=["要点確認"],
            uml_requirements={
                "pre_understanding": "入力の多義性を認識",
                "post_confidence": "確信度と根拠を明示",
            },
        )
        assert len(req.uml_requirements) == 2
        assert "pre_understanding" in req.uml_requirements

    # PURPOSE: uml_requirements なしの既存 SELRequirement (後方互換)
    def test_requirement_without_uml(self):
        """uml_requirements なしの既存 SELRequirement (後方互換)"""
        req = SELRequirement(
            description="test",
            minimum_requirements=["要点確認"],
        )
        assert req.uml_requirements == {}

    # PURPOSE: SELValidationResult の UML フィールド
    def test_validation_result_uml_fields(self):
        """SELValidationResult の UML フィールド"""
        result = SELValidationResult(
            workflow="noe",
            operator="+",
            is_compliant=True,
            met_requirements=["a"],
            uml_met=["pre_understanding: 多義性"],
            uml_missing=["post_confidence: 確信度"],
            uml_score=0.5,
        )
        assert "UML: 1/2" in result.summary

    # PURPOSE: UML なしの場合は UML 部分が表示されない
    def test_validation_result_no_uml(self):
        """UML なしの場合は UML 部分が表示されない"""
        result = SELValidationResult(
            workflow="noe",
            operator="+",
            is_compliant=True,
            met_requirements=["a"],
        )
        assert "UML" not in result.summary


# =============================================================================
# 3. UML-SEL Bridge テスト
# =============================================================================


# PURPOSE: UML-SEL 統合検証テスト
class TestUMLSELBridge:
    """UML-SEL 統合検証テスト"""

    # PURPOSE: 基本的な統合検証が動作する
    def test_validate_with_uml_basic(self):
        """基本的な統合検証が動作する"""
        result = validate_with_uml(
            workflow="nonexistent_wf",
            operator="+",
            output="十分に長いテスト出力。要点を確認した上で判断を下しました。確信度は75%です。",
            context="テスト入力",
            confidence=75.0,
        )
        assert isinstance(result, UMLSELResult)
        assert isinstance(result.sel_result, SELValidationResult)
        assert isinstance(result.uml_report, UMLReport)
        assert 0 <= result.combined_score <= 1.0

    # PURPOSE: 統合スコアが正しい重みで計算される
    def test_combined_score_weights(self):
        """統合スコアが正しい重みで計算される"""
        result = validate_with_uml(
            workflow="nonexistent_wf",
            operator="+",
            output="テスト出力",
            context="テスト",
            confidence=50.0,
            sel_weight=0.6,
            uml_weight=0.4,
        )
        assert result.sel_weight == 0.6
        assert result.uml_weight == 0.4

    # PURPOSE: summary にワークフロー名が含まれる
    def test_summary_format(self):
        """summary にワークフロー名が含まれる"""
        result = validate_with_uml(
            workflow="test_wf",
            operator="+",
            output="テスト出力テスト出力テスト出力テスト出力テスト出力",
            context="入力",
            confidence=50.0,
        )
        assert "test_wf" in result.summary

    # PURPOSE: details がマルチラインで統合レポートを含む
    def test_details_multi_line(self):
        """details がマルチラインで統合レポートを含む"""
        result = validate_with_uml(
            workflow="test_wf",
            operator="+",
            output="テスト出力テスト出力テスト出力テスト出力テスト出力",
            context="入力",
            confidence=50.0,
        )
        details = result.details
        assert "統合スコア" in details
        assert "SEL" in details
        assert "UML" in details
