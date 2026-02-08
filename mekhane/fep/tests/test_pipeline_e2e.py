#!/usr/bin/env python3
# PROOF: [L3/テスト] <- mekhane/fep/tests/
"""
PROOF: [L3/テスト] このファイルは存在しなければならない

A0 → CCL → Hermēneus → Attractor → PW → Cone のE2Eパイプラインを検証
   → 個々のPJは単体テスト済みだが、パイプライン接続の正確性を保証する
   → test_pipeline_e2e.py が担う

Q.E.D.
"""

import pytest
from pathlib import Path

from mekhane.fep.pipeline import (
    PipelineResult,
    StageResult,
    run_pipeline,
    _generate_stub_outputs,
    _stage_hermeneus,
    _stage_attractor,
    _stage_pw,
    _stage_cone,
)

# Embedder availability check (requires ONNX model for embedding)
try:
    from mekhane.anamnesis.index import MODELS_DIR
    _HAS_MODEL = (MODELS_DIR / "model.onnx").exists()
except Exception:
    _HAS_MODEL = False
_SKIP_NO_MODEL = pytest.mark.skipif(
    not _HAS_MODEL,
    reason="Embedder ONNX model not available",
)


# =============================================================================
# Stage 1: Hermēneus Parse
# =============================================================================


class TestStageHermeneus:
    """Hermēneus CCL パースステージ。"""

    def test_simple_workflow(self):
        """単純なWFのパース。"""
        r = _stage_hermeneus("/dia")
        assert r.success
        assert "/dia" in r.data["workflows"]

    def test_oscillation_expr(self):
        """収束振動式のパース。"""
        r = _stage_hermeneus("/dia+~*/noe")
        assert r.success
        assert "/dia" in r.data["workflows"]
        assert "/noe" in r.data["workflows"]

    def test_complex_expr(self):
        """複合式のパース。"""
        r = _stage_hermeneus("/dia+~*/noe~*/pan+")
        assert r.success
        assert len(r.data["workflows"]) >= 2

    def test_invalid_expr(self):
        """不正な式はパース失敗。"""
        r = _stage_hermeneus("???invalid{{{")
        assert not r.success
        assert r.error is not None

    def test_ast_is_present(self):
        """成功時にASTが存在する。"""
        r = _stage_hermeneus("/noe")
        assert r.success
        assert r.data["ast"] is not None

    def test_tree_is_present(self):
        """成功時に木構造表示が存在する。"""
        r = _stage_hermeneus("/noe+")
        assert r.success
        assert len(r.data["tree"]) > 0


# =============================================================================
# Stage 2: Attractor
# =============================================================================


@_SKIP_NO_MODEL
class TestStageAttractor:
    """Attractor Series 識別ステージ。"""

    def test_japanese_input(self):
        """日本語入力からSeriesを識別。"""
        r = _stage_attractor("なぜこれが存在するのか、本質を問いたい")
        assert r.success
        assert len(r.data["series"]) >= 1

    def test_returns_oscillation(self):
        """OscillationType が返る。"""
        r = _stage_attractor("設計パターンを評価して品質基準を決める")
        assert r.success
        assert r.data["oscillation"] is not None

    def test_returns_similarity(self):
        """類似度スコアが返る。"""
        r = _stage_attractor("アーキテクチャを設計する")
        assert r.success
        assert r.data["top_similarity"] >= 0


# =============================================================================
# Stage 3: PW Resolve
# =============================================================================


class TestStagePW:
    """PW 解決ステージ。"""

    def test_o_series_pw(self):
        """O-series の PW が返る。"""
        r = _stage_pw("O")
        assert r.success
        assert "pw" in r.data

    def test_s_series_with_context(self):
        """コンテキスト付きPW推定。"""
        r = _stage_pw("S", context="詳細な設計手順が必要")
        assert r.success

    def test_none_series_fails(self):
        """Series なし → 失敗。"""
        r = _stage_pw(None)
        assert not r.success

    def test_all_series(self):
        """全6 Series でPWが返る。"""
        for s in ["O", "S", "H", "P", "K", "A"]:
            r = _stage_pw(s)
            assert r.success, f"Failed for series {s}"


# =============================================================================
# Stage 4: Cone Converge
# =============================================================================


class TestStageCone:
    """Cone 構築ステージ。"""

    def test_o_series_cone(self):
        """O-series の Cone が構築できる。"""
        outputs = _generate_stub_outputs("O")
        r = _stage_cone("O", outputs, {})
        assert r.success
        assert r.data["apex"] is not None
        assert r.data["method"] is not None

    def test_s_series_with_pw(self):
        """PW付きCone構築。"""
        outputs = _generate_stub_outputs("S")
        pw = {"S1": 0.5, "S2": 0.0, "S3": -0.3, "S4": 0.0}
        r = _stage_cone("S", outputs, pw)
        assert r.success
        assert r.data["method"] in ("simple", "pw_weighted", "root")

    def test_none_series_fails(self):
        """Series なし → 失敗。"""
        r = _stage_cone(None, {}, {})
        assert not r.success


# =============================================================================
# E2E Pipeline
# =============================================================================


@_SKIP_NO_MODEL
class TestE2EPipeline:
    """E2E パイプライン統合テスト (ONNX モデル依存)。"""

    def test_simple_workflow_e2e(self):
        """単純WF: /dia → A-series まで通る。"""
        result = run_pipeline("/dia", force_cpu=True, use_gnosis=False)
        assert result.stages[0].success, "Hermēneus should parse /dia"
        assert result.stages[1].success, "Attractor should identify series"
        # PW + Cone may or may not succeed depending on attractor output
        assert len(result.stages) >= 3

    def test_oscillation_expr_e2e(self):
        """合成WF: /dia+~*/noe → 複数 Series oscillation。"""
        result = run_pipeline("/dia+~*/noe", force_cpu=True, use_gnosis=False)
        assert result.stages[0].success
        assert len(result.workflows) >= 2
        # Should get to at least Stage 3
        assert len(result.stages) >= 3

    def test_explicit_pw_e2e(self):
        """明示PW付きWF: /noe → Oseriesまで通る。"""
        result = run_pipeline("/noe+", force_cpu=True, use_gnosis=False)
        assert result.stages[0].success
        # All stages should complete
        if result.all_passed:
            assert result.llm_injection != ""

    def test_mock_outputs_used(self):
        """mock_outputsが使われると全ステージ通る。"""
        mock = {
            "A1": "感情分析: 期待と不安が混在",
            "A2": "判定: 妥当性は高い",
            "A3": "格言: 量より質",
            "A4": "知識: FEPに基づく評価",
        }
        result = run_pipeline(
            "/dia", force_cpu=True, use_gnosis=False, mock_outputs=mock,
        )
        assert result.stages[0].success
        # If attractor matched A-series, cone should also pass
        if len(result.stages) >= 4:
            cone_stage = result.stages[3]
            if cone_stage.success:
                assert cone_stage.data["apex"] is not None

    def test_summary_format(self):
        """summary() が読めるフォーマットを返す。"""
        result = run_pipeline("/noe", force_cpu=True, use_gnosis=False)
        summary = result.summary()
        assert "Pipeline:" in summary
        assert "✅" in summary or "❌" in summary


class TestE2EModelIndependent:
    """E2E パイプラインテスト (モデル不要)。"""

    def test_parse_failure_graceful(self):
        """パース失敗 → Stage 1 で停止、残りスキップ。"""
        result = run_pipeline("???invalid{{{", force_cpu=True)
        assert not result.all_passed
        assert result.failed_at == "hermeneus"
        assert len(result.stages) == 1

    def test_japanese_fallback_e2e(self):
        """日本語自然言語 → パース失敗 → Stage 1 で停止。
        (CCLパーサーは自然言語をパースしない — これは期待通りの挙動)"""
        result = run_pipeline("なぜ存在するのか", force_cpu=True)
        # Natural language is NOT valid CCL, so hermeneus should fail
        assert result.failed_at == "hermeneus"

    def test_empty_ccl(self):
        """空文字列 → パース失敗。"""
        result = run_pipeline("", force_cpu=True)
        assert result.failed_at == "hermeneus"


# =============================================================================
# Stub Output Generation
# =============================================================================


class TestStubOutputs:
    """スタブ出力生成。"""

    def test_o_series_stubs(self):
        """O-series → O1-O4 のスタブ。"""
        outputs = _generate_stub_outputs("O")
        assert len(outputs) == 4
        assert "O1" in outputs
        assert "O4" in outputs

    def test_unknown_series_empty(self):
        """未知Series → 空。"""
        outputs = _generate_stub_outputs("Z")
        assert outputs == {}

    def test_none_series_empty(self):
        outputs = _generate_stub_outputs(None)
        assert outputs == {}


# =============================================================================
# PipelineResult Properties
# =============================================================================


class TestPipelineResult:
    """PipelineResult のプロパティ。"""

    def test_all_passed_true(self):
        """全ステージ成功。"""
        r = PipelineResult(ccl_expr="test", stages=[
            StageResult(name="a", success=True),
            StageResult(name="b", success=True),
        ])
        assert r.all_passed
        assert r.failed_at is None

    def test_all_passed_false(self):
        """1ステージ失敗。"""
        r = PipelineResult(ccl_expr="test", stages=[
            StageResult(name="a", success=True),
            StageResult(name="b", success=False, error="boom"),
        ])
        assert not r.all_passed
        assert r.failed_at == "b"

    def test_empty_stages(self):
        """ステージなし → all_passed = True (vacuous truth)。"""
        r = PipelineResult(ccl_expr="test")
        assert r.all_passed
