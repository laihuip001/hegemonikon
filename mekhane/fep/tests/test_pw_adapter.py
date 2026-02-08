"""Tests for pw_adapter.py — L1↔L2 PW bridge."""

import pytest
from unittest.mock import MagicMock

from mekhane.fep.pw_adapter import (
    parse_pw_spec,
    infer_pw,
    derive_pw,
    resolve_pw,
    describe_pw,
    is_uniform,
    is_phase2_ready,
    PHASE2_BASIN_THRESHOLD,
    SERIES_THEOREMS,
)


# =============================================================================
# Strategy 1: parse_pw_spec
# =============================================================================


class TestParsePwSpec:
    """Explicit PW spec parsing."""

    def test_single_plus(self):
        pw = parse_pw_spec("S1+", "S")
        assert pw["S1"] == 0.5
        assert pw["S2"] == 0.0

    def test_single_minus(self):
        pw = parse_pw_spec("S3-", "S")
        assert pw["S3"] == -0.5

    def test_double_plus(self):
        pw = parse_pw_spec("S1++", "S")
        assert pw["S1"] == 1.0

    def test_double_minus(self):
        pw = parse_pw_spec("S3--", "S")
        assert pw["S3"] == -1.0

    def test_equals_format(self):
        pw = parse_pw_spec("S1=0.3, S3=-0.7", "S")
        assert pw["S1"] == pytest.approx(0.3)
        assert pw["S3"] == pytest.approx(-0.7)

    def test_bare_theorem_defaults_positive(self):
        pw = parse_pw_spec("S2", "S")
        assert pw["S2"] == 0.5

    def test_multiple_specs(self):
        pw = parse_pw_spec("S1+, S3-, S4++", "S")
        assert pw["S1"] == 0.5
        assert pw["S2"] == 0.0
        assert pw["S3"] == -0.5
        assert pw["S4"] == 1.0

    def test_clamps_to_range(self):
        pw = parse_pw_spec("S1=1.5", "S")
        assert pw["S1"] == 1.0

    def test_invalid_series_returns_empty(self):
        pw = parse_pw_spec("X1+", "X")
        assert pw == {}

    def test_ignores_invalid_theorem_ids(self):
        pw = parse_pw_spec("Z9+", "S")
        assert all(v == 0.0 for v in pw.values())

    def test_all_series(self):
        """Verify parse works for every series."""
        for series, theorems in SERIES_THEOREMS.items():
            spec = f"{theorems[0]}+"
            pw = parse_pw_spec(spec, series)
            assert pw[theorems[0]] == 0.5


# =============================================================================
# Strategy 2: infer_pw
# =============================================================================


class TestInferPw:
    """Context-based PW inference."""

    # S-series
    def test_s_new_design(self):
        pw = infer_pw("S", "新規設計 フロントエンド")
        assert pw["S2"] > 0  # Mekhanē emphasized

    def test_s_refactor(self):
        pw = infer_pw("S", "リファクタリング 整理")
        assert pw["S1"] > 0  # Metron
        assert pw["S3"] > 0  # Stathmos

    def test_s_implement(self):
        pw = infer_pw("S", "実装フェーズ コーディング")
        assert pw["S4"] > 0  # Praxis

    def test_s_default_uniform(self):
        pw = infer_pw("S", "neutral test input")
        assert is_uniform(pw)

    # O-series
    def test_o_uncertainty(self):
        pw = infer_pw("O", "不確実な状況 探求が必要")
        assert pw["O3"] > 0  # Zētēsis

    def test_o_bias(self):
        pw = infer_pw("O", "バイアス警告が出ている")
        assert pw["O1"] < 0  # suppress bias source

    # K-series
    def test_k_urgent(self):
        pw = infer_pw("K", "緊急の対応が必要")
        assert pw["K1"] > 0  # Eukairia
        assert pw["K2"] > 0  # Chronos

    def test_k_strategy(self):
        pw = infer_pw("K", "長期戦略を検討")
        assert pw["K3"] > 0  # Telos
        assert pw["K4"] > 0  # Sophia

    # H-series
    def test_h_emotional(self):
        pw = infer_pw("H", "感情が強い文脈")
        assert pw["H1"] > 0  # Propatheia

    # P-series
    def test_p_scoping(self):
        pw = infer_pw("P", "スコープを決定する")
        assert pw["P1"] > 0  # Khōra

    # A-series
    def test_a_emotional(self):
        pw = infer_pw("A", "感情が判断を歪めている")
        assert pw["A1"] < 0  # suppress emotion
        assert pw["A2"] > 0  # emphasize judgment

    def test_a_knowledge(self):
        pw = infer_pw("A", "知識の確定が必要")
        assert pw["A4"] > 0  # Epistēmē

    def test_invalid_series(self):
        pw = infer_pw("X", "test")
        assert pw == {}


# =============================================================================
# Strategy 3: derive_pw
# =============================================================================


class TestDerivePw:
    """Agent-derived PW (L1→L2 natural transformation)."""

    def _make_agent(self, context=0.5, urgency=0.5, confidence=0.5):
        agent = MagicMock()
        agent.precision_weights = {
            "context": context,
            "urgency": urgency,
            "confidence": confidence,
        }
        return agent

    def test_neutral_agent_gives_zero(self):
        """All modalities at 0.5 → all theorems at 0.0."""
        agent = self._make_agent(0.5, 0.5, 0.5)
        pw = derive_pw("S", agent)
        assert all(abs(v) < 1e-6 for v in pw.values())

    def test_high_context_emphasizes_cognitive(self):
        """High context precision → cognitive theorems emphasized."""
        agent = self._make_agent(context=1.0, urgency=0.5, confidence=0.5)
        pw = derive_pw("S", agent)
        assert pw["S1"] > 0  # Metron (context)
        assert pw["S2"] > 0  # Mekhanē (context)
        assert pw["S4"] == pytest.approx(0.0, abs=1e-6)  # Praxis (urgency)

    def test_high_urgency_emphasizes_action(self):
        """High urgency → action theorems emphasized."""
        agent = self._make_agent(context=0.5, urgency=1.0, confidence=0.5)
        pw = derive_pw("S", agent)
        assert pw["S4"] > 0  # Praxis (urgency)
        assert pw["S1"] == pytest.approx(0.0, abs=1e-6)  # Metron (context)

    def test_high_confidence_emphasizes_judgment(self):
        """High confidence → judgment theorems emphasized."""
        agent = self._make_agent(context=0.5, urgency=0.5, confidence=1.0)
        pw = derive_pw("S", agent)
        assert pw["S3"] > 0  # Stathmos (confidence)

    def test_low_modality_suppresses(self):
        """Low modality precision → negative PW (suppress)."""
        agent = self._make_agent(context=0.0, urgency=0.5, confidence=0.5)
        pw = derive_pw("S", agent)
        assert pw["S1"] < 0  # Metron suppressed
        assert pw["S2"] < 0  # Mekhanē suppressed

    def test_all_series(self):
        """derive_pw works for every series."""
        agent = self._make_agent(0.8, 0.3, 0.6)
        for series in SERIES_THEOREMS:
            pw = derive_pw(series, agent)
            assert len(pw) == 4

    def test_invalid_series(self):
        agent = self._make_agent()
        pw = derive_pw("X", agent)
        assert pw == {}


# =============================================================================
# resolve_pw cascade
# =============================================================================


class TestResolvePw:
    """Priority cascade: explicit > context > agent > default."""

    def test_explicit_wins(self):
        """pw_spec takes priority over everything."""
        agent = MagicMock()
        agent.precision_weights = {"context": 1.0, "urgency": 1.0, "confidence": 1.0}
        pw = resolve_pw("S", pw_spec="S1+", context="設計", agent=agent)
        assert pw["S1"] == 0.5  # from spec, not agent

    def test_context_wins_over_agent(self):
        """Context inference beats agent derivation."""
        agent = MagicMock()
        agent.precision_weights = {"context": 0.0, "urgency": 0.0, "confidence": 0.0}
        pw = resolve_pw("S", context="新規設計", agent=agent)
        assert pw["S2"] > 0  # from context rule, not agent suppression

    def test_agent_fallback(self):
        """Agent used when no spec/context match."""
        agent = MagicMock()
        agent.precision_weights = {"context": 1.0, "urgency": 0.5, "confidence": 0.5}
        pw = resolve_pw("S", context="neutral test input", agent=agent)
        assert pw["S1"] > 0  # from agent (high context)

    def test_default_uniform(self):
        """No inputs → uniform PW."""
        pw = resolve_pw("S")
        assert is_uniform(pw)

    def test_invalid_series(self):
        pw = resolve_pw("X")
        assert pw == {}


# =============================================================================
# Utilities
# =============================================================================


class TestUtilities:
    def test_describe_pw(self):
        desc = describe_pw({"S1": 0.5, "S2": 0.0, "S3": -0.3, "S4": 0.0})
        assert "S1=+0.5" in desc
        assert "S3=-0.3" in desc

    def test_is_uniform_true(self):
        assert is_uniform({"S1": 0.0, "S2": 0.0})

    def test_is_uniform_false(self):
        assert not is_uniform({"S1": 0.5, "S2": 0.0})

    def test_is_uniform_empty(self):
        assert is_uniform({})


# =============================================================================
# E1: Compound keyword tests (sum mode)
# =============================================================================


class TestInferPwCompound:
    """Verify that multiple matching rules are summed, not first-match."""

    def test_s_design_and_refactor(self):
        """'新規設計をリファクタリング' should activate BOTH rules."""
        pw = infer_pw("S", "新規設計をリファクタリングする")
        assert pw["S2"] > 0  # from design rule
        assert pw["S1"] > 0  # from refactor rule
        assert pw["S3"] > 0  # from refactor rule

    def test_s_all_three_contexts(self):
        """All 3 S-series rules match → S1+S2+S3+S4 all positive."""
        pw = infer_pw("S", "新規設計 リファクタリング 実装フェーズ")
        assert pw["S1"] > 0
        assert pw["S2"] > 0
        assert pw["S3"] > 0
        assert pw["S4"] > 0

    def test_o_bias_and_uncertainty(self):
        """Bias + uncertainty → O1 negative, O3 positive (cancel out if same)."""
        pw = infer_pw("O", "不確実な状態 バイアス警告")
        assert pw["O3"] > 0  # uncertainty → O3+
        assert pw["O1"] < 0  # bias → O1-

    def test_clamping_on_accumulation(self):
        """Even if many rules match, clamp to [-1, +1]."""
        # K-series: urgent + priority both boost K1
        pw = infer_pw("K", "緊急 優先順位判定")
        assert pw["K1"] <= 1.0
        assert pw["K1"] > 0


# =============================================================================
# E4: Parse error protection tests
# =============================================================================


class TestParsePwSpecEdgeCases:
    """Parse protection for malformed inputs."""

    def test_empty_string(self):
        pw = parse_pw_spec("", "S")
        assert is_uniform(pw)

    def test_whitespace_only(self):
        pw = parse_pw_spec("   ", "S")
        assert is_uniform(pw)

    def test_malformed_equals(self):
        """'S1=abc' should not crash, just skip the bad part."""
        pw = parse_pw_spec("S1=abc", "S")
        # Will fail float() conversion, so S1 stays 0
        assert pw["S1"] == 0.0

    def test_mixed_valid_invalid(self):
        """Valid specs work even with garbage mixed in."""
        pw = parse_pw_spec("S1+, garbage, S3-", "S")
        assert pw["S1"] == 0.5
        assert pw["S3"] == -0.5

    def test_cross_series_theorem(self):
        """O1+ in S-series should be ignored."""
        pw = parse_pw_spec("O1+", "S")
        assert is_uniform(pw)


# =============================================================================
# E5: Integration tests with converge()
# =============================================================================


class TestConvergeIntegration:
    """Integration: converge() + pw_adapter cascade."""

    def test_converge_with_context_infers_pw(self):
        """converge() with context= should auto-derive PW via adapter."""
        from mekhane.fep.cone_builder import converge
        from mekhane.fep.category import Series

        cone = converge(
            Series.S,
            {"S1": "Meso scale", "S2": "Composition", "S3": "Test-driven", "S4": "Production"},
            context="新規設計 アーキテクチャ",
        )
        assert cone.pw.get("S2", 0.0) > 0  # design context → S2+

    def test_converge_with_agent_derives_pw(self):
        """converge() with agent= should auto-derive PW from modality."""
        from mekhane.fep.cone_builder import converge
        from mekhane.fep.category import Series

        agent = MagicMock()
        agent.precision_weights = {"context": 1.0, "urgency": 0.5, "confidence": 0.5}

        cone = converge(
            Series.S,
            {"S1": "Meso", "S2": "Composition", "S3": "Standard", "S4": "Production"},
            agent=agent,
        )
        assert cone.pw.get("S1", 0.0) > 0  # high context → S1+
        assert cone.pw.get("S2", 0.0) > 0  # high context → S2+

    def test_converge_explicit_pw_overrides(self):
        """Explicit pw= should bypass adapter entirely."""
        from mekhane.fep.cone_builder import converge
        from mekhane.fep.category import Series

        cone = converge(
            Series.S,
            {"S1": "A", "S2": "B", "S3": "C", "S4": "D"},
            pw={"S4": 1.0},
            context="新規設計",  # would infer S2+ if pw was None
        )
        assert cone.pw.get("S4", 0.0) == 1.0
        assert cone.pw.get("S2", 0.0) == 0.0  # context ignored

    def test_converge_no_adapter_kwargs(self):
        """converge() without context/agent/pw → empty pw (backward compat)."""
        from mekhane.fep.cone_builder import converge
        from mekhane.fep.category import Series

        cone = converge(
            Series.O,
            {"O1": "deep", "O2": "strong", "O3": "sharp", "O4": "decisive"},
        )
        # All pw should be 0 (uniform)
        for v in cone.pw.values():
            assert abs(v) < 1e-6


# =============================================================================
# Phase 2 transition check
# =============================================================================


class TestPhase2Transition:
    """Phase 2 migration condition checks."""

    def test_phase2_not_ready_by_default(self):
        """With no BasinLogger data, Phase 2 is not ready."""
        assert is_phase2_ready() is False

    def test_phase2_ready_with_sufficient_data(self):
        """When BasinLogger has >= threshold entries, Phase 2 is ready."""
        from unittest.mock import patch, MagicMock

        mock_bias = MagicMock()
        mock_bias.total_count = PHASE2_BASIN_THRESHOLD  # exactly at threshold

        mock_logger = MagicMock()
        mock_logger.biases = {"S": mock_bias}

        with patch("mekhane.fep.basin_logger.BasinLogger", return_value=mock_logger):
            from mekhane.fep import pw_adapter
            result = pw_adapter.is_phase2_ready()
            assert result is True

    def test_phase2_not_ready_below_threshold(self):
        """When BasinLogger has < threshold entries, Phase 2 is not ready."""
        from unittest.mock import patch, MagicMock

        mock_bias = MagicMock()
        mock_bias.total_count = 10  # well below threshold

        mock_logger = MagicMock()
        mock_logger.biases = {"S": mock_bias}

        with patch("mekhane.fep.basin_logger.BasinLogger", return_value=mock_logger):
            from mekhane.fep import pw_adapter
            result = pw_adapter.is_phase2_ready()
            assert result is False
