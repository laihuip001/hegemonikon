#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/symploke/tests/
# PURPOSE: Boot THEOREM_REGISTRY の包括テスト — 96要素体系の Boot 時参照を検証
"""Boot THEOREM_REGISTRY Tests"""

import pytest
from mekhane.symploke.boot_integration import (
    THEOREM_REGISTRY,
    SERIES_INFO,
)


# ── THEOREM_REGISTRY ─────────────────────

class TestTheoremRegistry:
    """THEOREM_REGISTRY 定数のテスト"""

    def test_total_count(self):
        assert len(THEOREM_REGISTRY) == 24

    def test_o_series(self):
        for tid in ["O1", "O2", "O3", "O4"]:
            assert tid in THEOREM_REGISTRY
            assert THEOREM_REGISTRY[tid]["series"] == "O"

    def test_s_series(self):
        for tid in ["S1", "S2", "S3", "S4"]:
            assert tid in THEOREM_REGISTRY
            assert THEOREM_REGISTRY[tid]["series"] == "S"

    def test_h_series(self):
        for tid in ["H1", "H2", "H3", "H4"]:
            assert tid in THEOREM_REGISTRY
            assert THEOREM_REGISTRY[tid]["series"] == "H"

    def test_p_series(self):
        for tid in ["P1", "P2", "P3", "P4"]:
            assert tid in THEOREM_REGISTRY
            assert THEOREM_REGISTRY[tid]["series"] == "P"

    def test_k_series(self):
        for tid in ["K1", "K2", "K3", "K4"]:
            assert tid in THEOREM_REGISTRY
            assert THEOREM_REGISTRY[tid]["series"] == "K"

    def test_a_series(self):
        for tid in ["A1", "A2", "A3", "A4"]:
            assert tid in THEOREM_REGISTRY
            assert THEOREM_REGISTRY[tid]["series"] == "A"

    def test_all_have_name(self):
        for tid, info in THEOREM_REGISTRY.items():
            assert "name" in info, f"{tid} missing name"
            assert len(info["name"]) > 0

    def test_all_have_wf(self):
        for tid, info in THEOREM_REGISTRY.items():
            assert "wf" in info, f"{tid} missing wf"
            assert info["wf"].startswith("/")

    def test_all_have_level(self):
        for tid, info in THEOREM_REGISTRY.items():
            assert "level" in info, f"{tid} missing level"
            assert info["level"].startswith("L")

    def test_all_have_series(self):
        for tid, info in THEOREM_REGISTRY.items():
            assert "series" in info, f"{tid} missing series"
            assert info["series"] in "OSHPKA"

    # ── Specific Theorem Names ──
    def test_o1_noesis(self):
        assert THEOREM_REGISTRY["O1"]["name"] == "Noēsis"

    def test_o2_boulesis(self):
        assert THEOREM_REGISTRY["O2"]["name"] == "Boulēsis"

    def test_o3_zetesis(self):
        assert THEOREM_REGISTRY["O3"]["name"] == "Zētēsis"

    def test_o4_energeia(self):
        assert THEOREM_REGISTRY["O4"]["name"] == "Energeia"

    def test_s1_metron(self):
        assert THEOREM_REGISTRY["S1"]["name"] == "Metron"

    def test_s2_mekhane(self):
        assert THEOREM_REGISTRY["S2"]["name"] == "Mekhanē"

    def test_h1_propatheia(self):
        assert THEOREM_REGISTRY["H1"]["name"] == "Propatheia"

    def test_k4_sophia(self):
        assert THEOREM_REGISTRY["K4"]["name"] == "Sophia"

    def test_a2_krisis(self):
        assert THEOREM_REGISTRY["A2"]["name"] == "Krisis"

    def test_a4_episteme(self):
        assert THEOREM_REGISTRY["A4"]["name"] == "Epistēmē"

    # ── WF Mapping ──
    def test_o1_wf(self):
        assert THEOREM_REGISTRY["O1"]["wf"] == "/noe"

    def test_s2_wf(self):
        assert THEOREM_REGISTRY["S2"]["wf"] == "/mek"

    def test_a2_wf(self):
        assert THEOREM_REGISTRY["A2"]["wf"] == "/dia"

    def test_k4_wf(self):
        assert THEOREM_REGISTRY["K4"]["wf"] == "/sop"

    # ── Level Consistency ──
    def test_o_series_levels(self):
        for tid in ["O1", "O2", "O3", "O4"]:
            assert THEOREM_REGISTRY[tid]["level"] == "L0"

    def test_s_series_levels(self):
        for tid in ["S1", "S2", "S3", "S4"]:
            assert THEOREM_REGISTRY[tid]["level"] == "L1"

    def test_k_series_levels(self):
        for tid in ["K1", "K2", "K3", "K4"]:
            assert THEOREM_REGISTRY[tid]["level"] == "L3"

    def test_a_series_levels(self):
        for tid in ["A1", "A2", "A3", "A4"]:
            assert THEOREM_REGISTRY[tid]["level"] == "L4"


# ── SERIES_INFO ──────────────────────────

class TestSeriesInfo:
    """SERIES_INFO 定数のテスト"""

    def test_total_count(self):
        assert len(SERIES_INFO) == 6

    def test_all_series_present(self):
        expected = {"O", "S", "H", "P", "K", "A"}
        assert set(SERIES_INFO.keys()) == expected

    def test_o_label(self):
        assert "Ousia" in SERIES_INFO["O"]

    def test_s_label(self):
        assert "Schema" in SERIES_INFO["S"]

    def test_h_label(self):
        assert "Hormē" in SERIES_INFO["H"]

    def test_p_label(self):
        assert "Perigraphē" in SERIES_INFO["P"]

    def test_k_label(self):
        assert "Kairos" in SERIES_INFO["K"]

    def test_a_label(self):
        assert "Akribeia" in SERIES_INFO["A"]

    def test_all_have_japanese(self):
        for key, label in SERIES_INFO.items():
            # Each label should contain Japanese characters
            assert "(" in label, f"{key} missing Japanese in parentheses"
