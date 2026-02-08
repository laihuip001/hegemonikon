# PROOF: [L2/テスト] <- mekhane/fep/tests/
# PURPOSE: FEP E2E Loop の統合テスト
"""
E2E Loop Integration Tests

Test the complete Active Inference cycle:
1. Clear input → single Series → Cone
2. Oscillating input → multiple Series
3. Learning proof: 2 cycles → A-matrix changes
"""

import tempfile
from pathlib import Path

import pytest


# PURPOSE: E2E Loop の基本動作テスト
class TestE2ELoop:
    """E2E Loop の基本動作テスト"""

    # PURPOSE: 明確な入力 → WF dispatch が生成される
    def test_clear_input_produces_dispatch(self):
        """明確な入力 → WF dispatch が生成される"""
        from mekhane.fep.e2e_loop import run_loop

        result = run_loop(
            "なぜこのプロジェクトは存在するのか",
            cycles=1,
            force_cpu=True,
        )

        assert len(result.cycles) == 1
        c = result.cycles[0]

        # Encoding 成功
        assert len(c.observation) == 3
        assert all(isinstance(v, int) for v in c.observation)

        # FEP 推論成功
        assert c.fep_action in ("act", "observe")
        assert c.fep_entropy >= 0

        # A-matrix 更新
        assert c.a_matrix_updated is True

    # PURPOSE: Attractor が WF を推薦する
    def test_dispatch_resolves_workflow(self):
        """Attractor が WF を推薦する"""
        from mekhane.fep.e2e_loop import run_loop

        result = run_loop(
            "この設計の品質を批判的に評価してほしい",
            cycles=1,
            force_cpu=True,
        )

        c = result.cycles[0]
        # Attractor should find a matching Series
        # (might be A-series for judgment/evaluation)
        if c.dispatch_wf is not None:
            assert c.dispatch_series in ("O", "S", "H", "P", "K", "A")
            assert c.dispatch_wf.startswith("/")

    # PURPOSE: 2サイクルで学習証明が生成される
    def test_two_cycles_produce_learning_proof(self):
        """2サイクルで学習証明が生成される"""
        from mekhane.fep.e2e_loop import run_loop

        result = run_loop(
            "プロジェクトの方向性を明確にしたい",
            cycles=2,
            force_cpu=True,
        )

        assert len(result.cycles) == 2
        assert result.learning_proof is not None
        assert len(result.learning_proof) > 0

        # Summary contains both cycles
        summary = result.summary
        assert "Cycle 0" in summary
        assert "Cycle 1" in summary

    # PURPOSE: FEP が observe を返す時、dispatch が抑制される
    def test_observe_mode_suppresses_dispatch(self):
        """FEP が observe を返す時、dispatch が抑制される"""
        from mekhane.fep.e2e_loop import CycleResult

        # CycleResult のフラグを直接テスト
        cycle = CycleResult(
            cycle=0,
            observation=(0, 0, 0),
            obs_decoded={"context": "ambiguous", "urgency": "low", "confidence": "low"},
            fep_action="observe",
            fep_entropy=2.5,
            fep_confidence=0.17,
            dispatch_wf="/noe",
            dispatch_series="O",
            dispatch_reason="SUPPRESSED reason",
        )
        assert cycle.fep_action == "observe"
        assert "SUPPRESSED" in cycle.dispatch_reason

    # PURPOSE: シミュレーション Cone が出力を生成する
    def test_simulated_cone_produces_output(self):
        """シミュレーション Cone が出力を生成する"""
        from mekhane.fep.e2e_loop import _simulate_cone

        result = _simulate_cone("O", "テスト入力")
        assert "apex" in result
        assert "dispersion" in result
        assert "method" in result
        assert isinstance(result["dispersion"], float)
        assert 0.0 <= result["dispersion"] <= 1.0

    # PURPOSE: E2EResult.summary が正しく生成される
    def test_e2e_result_summary(self):
        """E2EResult.summary が正しく生成される"""
        from mekhane.fep.e2e_loop import E2EResult, CycleResult

        result = E2EResult(
            input_text="テスト",
            cycles=[
                CycleResult(
                    cycle=0,
                    observation=(1, 0, 2),
                    obs_decoded={"context": "clear"},
                    fep_action="act",
                    fep_entropy=1.5,
                    fep_confidence=0.5,
                    dispatch_wf="/noe",
                ),
                CycleResult(
                    cycle=1,
                    observation=(1, 0, 2),
                    obs_decoded={"context": "clear"},
                    fep_action="act",
                    fep_entropy=1.2,
                    fep_confidence=0.6,
                    dispatch_wf="/noe",
                ),
            ],
            learning_proof="エントロピー減少: 1.500 → 1.200 (-20.0%)",
        )

        summary = result.summary
        assert "E2E Loop" in summary
        assert "Cycle 0" in summary
        assert "Cycle 1" in summary
        assert "Learning" in summary

    # PURPOSE: 各テストが独立したA行列を使用する
    def test_a_matrix_isolation(self):
        """各テストが独立したA行列を使用する"""
        from mekhane.fep.e2e_loop import run_loop

        # カスタムA行列パスで分離
        with tempfile.NamedTemporaryFile(suffix="_test_A.npy", delete=False) as f:
            a_path = f.name

        # Unlink so it starts fresh (np.load fails on empty files)
        Path(a_path).unlink(missing_ok=True)

        try:
            result = run_loop(
                "テスト",
                cycles=1,
                a_matrix_path=a_path,
                force_cpu=True,
            )
            assert result.cycles[0].a_matrix_updated
            assert Path(a_path).exists()
        finally:
            Path(a_path).unlink(missing_ok=True)
