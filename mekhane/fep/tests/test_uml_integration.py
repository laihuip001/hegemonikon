#!/usr/bin/env python3
# PROOF: [L3/テスト] <- mekhane/fep/tests/
"""
PROOF: [L3/テスト] このファイルは存在しなければならない

A0 → UML Phase 2 がパイプラインと postcheck に正しく統合されているか検証
   → Pipeline Stage 0/6 + wf_postcheck check_uml() のテスト
   → test_uml_integration.py が担う

Q.E.D.
"""

import pytest

from mekhane.fep.pipeline import (
    PipelineResult,
    StageResult,
    _stage_uml_pre,
    _stage_uml_post,
)


# =============================================================================
# Stage 0: UML Pre-check
# =============================================================================


# PURPOSE: UML Pre-check ステージ。
class TestStageUMLPre:
    """UML Pre-check ステージ。"""

    # PURPOSE: CCL式からWF名を抽出し、プロンプト生成。
    def test_simple_ccl(self):
        """CCL式からWF名を抽出し、プロンプト生成。"""
        r = _stage_uml_pre("/dia")
        assert r.success
        assert r.data["wf_name"] == "dia"
        assert "UML Pre-check" in r.data["prompt"]
        assert len(r.data["checks"]) == 2  # Stage 1 + Stage 2

    # PURPOSE: /dia+~*/noe → WF名は最初の dia。
    def test_complex_ccl(self):
        """/dia+~*/noe → WF名は最初の dia。"""
        r = _stage_uml_pre("/dia+~*/noe")
        assert r.success
        assert r.data["wf_name"] == "dia"

    # PURPOSE: コンテキスト付きで入力要約が含まれる。
    def test_context_in_prompt(self):
        """コンテキスト付きで入力要約が含まれる。"""
        r = _stage_uml_pre("/noe", context="本質を問いたい")
        assert r.success
        assert "本質" in r.data["prompt"]

    # PURPOSE: CCL以外の入力 → wf_name = unknown。
    def test_non_ccl_input(self):
        """CCL以外の入力 → wf_name = unknown。"""
        r = _stage_uml_pre("これは自然言語です")
        assert r.success
        assert r.data["wf_name"] == "unknown"

    # PURPOSE: Pre-checks は stage, passed, result を持つ。
    def test_pre_checks_structure(self):
        """Pre-checks は stage, passed, result を持つ。"""
        r = _stage_uml_pre("/dia", context="評価基準を決める")
        assert r.success
        for check in r.data["checks"]:
            assert "stage" in check
            assert "passed" in check
            assert "result" in check


# =============================================================================
# Stage 6: UML Post-check
# =============================================================================


# PURPOSE: UML Post-check ステージ。
class TestStageUMLPost:
    """UML Post-check ステージ。"""

    # PURPOSE: 基本的なポストチェック。
    def test_basic_post_check(self):
        """基本的なポストチェック。"""
        r = _stage_uml_post(
            wf_name="dia",
            context="/dia output",
            output="判定結果: この設計は妥当です。理由は...",
            confidence=75.0,
        )
        assert r.success
        assert r.data["report"] is not None
        assert r.data["total_count"] == 5  # All 5 stages

    # PURPOSE: 空出力 → UMLチェック自体は成功するが個別チェックは失敗。
    def test_empty_output_check(self):
        """空出力 → UMLチェック自体は成功するが個別チェックは失敗。"""
        r = _stage_uml_post(
            wf_name="noe",
            context="/noe output",
            output="",
        )
        assert r.success
        # Empty output should fail evaluation check
        assert not r.data["overall_pass"]

    # PURPOSE: 過信検知 (confidence > 90)。
    def test_overconfidence_detection(self):
        """過信検知 (confidence > 90)。"""
        r = _stage_uml_post(
            wf_name="dia",
            context="/dia output",
            output="これは絶対に正しいです。間違いありません。",
            confidence=95.0,
        )
        assert r.success
        # Overconfidence should trigger warning
        report = r.data["report"]
        confidence_checks = [
            c for c in report.all_checks
            if c.stage.value == "post_confidence"
        ]
        assert len(confidence_checks) > 0

    # PURPOSE: UMLReport の summary がフォーマットされている。
    def test_report_summary_format(self):
        """UMLReport の summary がフォーマットされている。"""
        r = _stage_uml_post(
            wf_name="mek",
            context="/mek output",
            output="設計パターンを3つ提示します。1. ファクトリー 2. ストラテジー 3. オブザーバー",
            confidence=60.0,
        )
        assert r.success
        summary = r.data["summary"]
        assert "UML" in summary or "PASS" in summary or "FAIL" in summary


# =============================================================================
# Pipeline UML Integration
# =============================================================================


# PURPOSE: Pipeline に UML が統合されているか。
class TestPipelineUMLIntegration:
    """Pipeline に UML が統合されているか。"""

    # PURPOSE: use_uml=True → uml_pre_prompt が設定される。
    def test_uml_pre_prompt_populated(self):
        """use_uml=True → uml_pre_prompt が設定される。"""
        from mekhane.fep.pipeline import run_pipeline

        # Use a parseable CCL expression
        result = run_pipeline("/noe", force_cpu=True, use_uml=True, use_gnosis=False)
        # UML pre should always succeed
        uml_pre_stage = result.stages[0]
        assert uml_pre_stage.name == "uml_pre"
        assert uml_pre_stage.success
        assert result.uml_pre_prompt != ""

    # PURPOSE: use_uml=False → UML ステージなし。
    def test_uml_disabled(self):
        """use_uml=False → UML ステージなし。"""
        from mekhane.fep.pipeline import run_pipeline

        result = run_pipeline("/noe", force_cpu=True, use_uml=False, use_gnosis=False)
        stage_names = [s.name for s in result.stages]
        assert "uml_pre" not in stage_names
        assert "uml_post" not in stage_names


# =============================================================================
# wf_postcheck check_uml Integration
# =============================================================================


# PURPOSE: wf_postcheck に check_uml が統合されているか。
class TestPostcheckUML:
    """wf_postcheck に check_uml が統合されているか。"""

    # PURPOSE: check_uml が UML チェック結果を返す。
    def test_check_uml_returns_checks(self):
        """check_uml が UML チェック結果を返す。"""
        from scripts.wf_postcheck import check_uml

        checks = check_uml("dia", "判定: 設計の妥当性を検証しました。結果は...")
        assert len(checks) == 3  # Post-check Stage 3-5
        for c in checks:
            assert "name" in c
            assert "passed" in c
            assert "detail" in c
            assert "UML" in c["name"]

    # PURPOSE: 空出力でも例外なし。
    def test_check_uml_empty_output(self):
        """空出力でも例外なし。"""
        from scripts.wf_postcheck import check_uml

        checks = check_uml("noe", "")
        assert isinstance(checks, list)

    # PURPOSE: postcheck 内で check_uml が呼ばれる (boot)。
    def test_check_uml_in_postcheck(self):
        """postcheck 内で check_uml が呼ばれる (boot)。"""
        from scripts.wf_postcheck import postcheck

        result = postcheck(
            "boot", "+",
            # Minimal boot output
            "## セッション状態\nIdentity Stack: loaded\n## 環境確認\nPKS: active\n"
            "## 今日のコンテキスト\n開発継続\n## 目的\nE2Eテスト完了\n"
            "## Creator補完: 提案\nUML Phase 2 を実装\n",
        )
        # Should have UML checks in the results
        uml_checks = [c for c in result["checks"] if "UML" in c.get("name", "")]
        assert len(uml_checks) >= 1


# =============================================================================
# Prompt Injection Content
# =============================================================================


# PURPOSE: 注入プロンプトの内容が適切か。
class TestPromptInjectionContent:
    """注入プロンプトの内容が適切か。"""

    # PURPOSE: Pre-prompt に2つの質問がある。
    def test_pre_prompt_has_questions(self):
        """Pre-prompt に2つの質問がある。"""
        r = _stage_uml_pre("/dia")
        prompt = r.data["prompt"]
        assert prompt.count("❓") >= 2

    # PURPOSE: Pre-prompt に WF 名が含まれる。
    def test_pre_prompt_has_wf_name(self):
        """Pre-prompt に WF 名が含まれる。"""
        r = _stage_uml_pre("/dia")
        assert "/dia" in r.data["prompt"]

    # PURPOSE: Pre-prompt にステージラベルがある。
    def test_pre_prompt_has_stage_labels(self):
        """Pre-prompt にステージラベルがある。"""
        r = _stage_uml_pre("/noe")
        prompt = r.data["prompt"]
        # Should contain O1 and A1 stage markers
        assert "O1" in prompt
        assert "A1" in prompt
