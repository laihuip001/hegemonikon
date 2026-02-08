# PROOF: [L2/FEP] <- mekhane/fep/tests/
# PURPOSE: TheoremAttractor のユニットテスト — suggest/flow/basins
"""
TheoremAttractor Tests

24 定理レベル attractor の動作検証。
GPU 非搭載環境でも CPU fallback で動作可能。
"""

from __future__ import annotations

import pytest

from mekhane.fep.theorem_attractor import (
    MORPHISM_MAP,
    THEOREM_DEFINITIONS,
    THEOREM_KEYS,
    BasinResult,
    FlowResult,
    FlowState,
    TheoremAttractor,
    TheoremResult,
)


# ---------------------------------------------------------------------------
# Fixture: 共有インスタンス (embedding は重いので session scope)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def attractor() -> TheoremAttractor:
    return TheoremAttractor()


# ---------------------------------------------------------------------------
# Constants / Data Integrity
# ---------------------------------------------------------------------------

class TestDefinitions:
    """24 定理の定義データの整合性"""

    def test_24_theorems_defined(self):
        assert len(THEOREM_DEFINITIONS) == 24

    def test_24_keys(self):
        assert len(THEOREM_KEYS) == 24

    def test_all_keys_in_definitions(self):
        for key in THEOREM_KEYS:
            assert key in THEOREM_DEFINITIONS, f"{key} missing from definitions"

    def test_all_series_covered(self):
        series = {d["series"] for d in THEOREM_DEFINITIONS.values()}
        assert series == {"O", "S", "H", "P", "K", "A"}

    def test_each_series_has_4_theorems(self):
        for s in ("O", "S", "H", "P", "K", "A"):
            count = sum(1 for d in THEOREM_DEFINITIONS.values() if d["series"] == s)
            assert count == 4, f"Series {s} has {count} theorems, expected 4"

    def test_morphism_map_complete(self):
        assert len(MORPHISM_MAP) == 24

    def test_morphisms_per_theorem(self):
        for key, targets in MORPHISM_MAP.items():
            assert len(targets) == 8, f"{key} has {len(targets)} morphisms, expected 8"

    def test_no_self_morphism(self):
        for key, targets in MORPHISM_MAP.items():
            assert key not in targets, f"{key} has self-morphism"


# ---------------------------------------------------------------------------
# Suggest
# ---------------------------------------------------------------------------

class TestSuggest:
    """定理レベル suggest"""

    def test_returns_list(self, attractor):
        results = attractor.suggest("認識の本質を考える")
        assert isinstance(results, list)

    def test_top_k_default_5(self, attractor):
        results = attractor.suggest("認識の本質を考える")
        assert len(results) == 5

    def test_top_k_custom(self, attractor):
        results = attractor.suggest("認識の本質を考える", top_k=3)
        assert len(results) == 3

    def test_all_24(self, attractor):
        results = attractor.suggest("認識の本質を考える", top_k=24)
        assert len(results) == 24

    def test_result_type(self, attractor):
        results = attractor.suggest("何を作るべきか")
        for r in results:
            assert isinstance(r, TheoremResult)

    def test_similarity_range(self, attractor):
        results = attractor.suggest("何を作るべきか", top_k=24)
        for r in results:
            assert -1.0 <= r.similarity <= 1.0, f"{r.theorem}: sim={r.similarity}"

    def test_sorted_descending(self, attractor):
        results = attractor.suggest("設計パターンの選択", top_k=24)
        for i in range(len(results) - 1):
            assert results[i].similarity >= results[i + 1].similarity

    def test_each_result_has_fields(self, attractor):
        results = attractor.suggest("テスト", top_k=1)
        r = results[0]
        assert r.theorem in THEOREM_KEYS
        assert r.name
        assert r.series in ("O", "S", "H", "P", "K", "A")
        assert r.command.startswith("/")

    def test_noesis_for_deep_question(self, attractor):
        """深い「なぜ」の質問では O1 Noēsis が上位に来るべき"""
        results = attractor.suggest("Why does this truly exist?", top_k=5)
        top_theorems = [r.theorem for r in results]
        assert "O1" in top_theorems, f"O1 not in top 5: {top_theorems}"

    def test_praxis_for_implementation(self, attractor):
        """実装系の質問では S4 Praxis が上位に来るべき"""
        results = attractor.suggest("How to implement and deliver this feature", top_k=5)
        top_theorems = [r.theorem for r in results]
        assert "S4" in top_theorems or "O4" in top_theorems, \
            f"S4/O4 not in top 5: {top_theorems}"


# ---------------------------------------------------------------------------
# Flow Simulation
# ---------------------------------------------------------------------------

class TestFlow:
    """X-series flow simulation"""

    def test_returns_flow_result(self, attractor):
        result = attractor.simulate_flow("設計の本質")
        assert isinstance(result, FlowResult)

    def test_states_list(self, attractor):
        result = attractor.simulate_flow("設計の本質", steps=5)
        assert len(result.states) >= 2  # at least step 0 + step 1

    def test_step_0_is_initial(self, attractor):
        result = attractor.simulate_flow("何かを問う")
        assert result.states[0].step == 0

    def test_activation_shape(self, attractor):
        result = attractor.simulate_flow("探求する")
        for state in result.states:
            assert state.activation.shape == (24,)

    def test_activation_normalized(self, attractor):
        """各 step の activation は確率分布 (合計≈1)"""
        result = attractor.simulate_flow("判定する")
        for state in result.states:
            total = state.activation.sum()
            assert abs(total - 1.0) < 0.01, f"Step {state.step}: sum={total}"

    def test_top_theorems_not_empty(self, attractor):
        result = attractor.simulate_flow("基準を設定する")
        for state in result.states:
            assert len(state.top_theorems) > 0

    def test_convergence(self, attractor):
        """10 steps で収束するはず"""
        result = attractor.simulate_flow("目的を問う", steps=10)
        assert result.converged_at >= 0, "Flow did not converge in 10 steps"

    def test_initial_similarities_present(self, attractor):
        result = attractor.simulate_flow("テスト")
        assert len(result.initial_similarities) == 24

    def test_final_theorems_present(self, attractor):
        result = attractor.simulate_flow("テスト")
        assert len(result.final_theorems) > 0


# ---------------------------------------------------------------------------
# Basin Detection
# ---------------------------------------------------------------------------

class TestBasins:
    """Monte Carlo basin detection"""

    def test_returns_basin_result(self, attractor):
        result = attractor.detect_basins(n_samples=100)
        assert isinstance(result, BasinResult)

    def test_fractions_sum_to_1(self, attractor):
        result = attractor.detect_basins(n_samples=1000)
        total = sum(result.basin_fractions.values())
        assert abs(total - 1.0) < 0.01, f"Fractions sum to {total}"

    def test_multiple_basins(self, attractor):
        """少なくとも 3 つの定理に分散すべき"""
        result = attractor.detect_basins(n_samples=1000)
        nonzero = sum(1 for v in result.basin_fractions.values() if v > 0)
        assert nonzero >= 3, f"Only {nonzero} basins (expected >= 3)"

    def test_no_100_percent_basin(self, attractor):
        """1 定理が 100% を占めてはならない"""
        result = attractor.detect_basins(n_samples=1000)
        for theorem, frac in result.basin_fractions.items():
            assert frac < 0.5, f"{theorem} has {frac:.1%} of basin (too dominant)"

    def test_elapsed_recorded(self, attractor):
        result = attractor.detect_basins(n_samples=100)
        assert result.elapsed >= 0

    def test_n_samples_correct(self, attractor):
        result = attractor.detect_basins(n_samples=500)
        total = sum(result.basin_sizes.values())
        assert total == 500

    def test_gpu_speed(self, attractor):
        """10,000 samples は 5 秒以内で完了すべき"""
        result = attractor.detect_basins(n_samples=10000)
        assert result.elapsed < 5.0, f"Basin detection took {result.elapsed:.2f}s"
