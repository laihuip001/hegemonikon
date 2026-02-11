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

# PURPOSE: Test suite validating theorem registry correctness
class TestTheoremRegistry:
    """THEOREM_REGISTRY 定数のテスト"""

    # PURPOSE: Verify total count behaves correctly
    def test_total_count(self):
        """Verify total count behavior."""
        assert len(THEOREM_REGISTRY) == 24

    # PURPOSE: Verify o series behaves correctly
    def test_o_series(self):
        """Verify o series behavior."""
        for tid in ["O1", "O2", "O3", "O4"]:
            assert tid in THEOREM_REGISTRY
            assert THEOREM_REGISTRY[tid]["series"] == "O"

    # PURPOSE: Verify s series behaves correctly
    def test_s_series(self):
        """Verify s series behavior."""
        for tid in ["S1", "S2", "S3", "S4"]:
            assert tid in THEOREM_REGISTRY
            assert THEOREM_REGISTRY[tid]["series"] == "S"

    # PURPOSE: Verify h series behaves correctly
    def test_h_series(self):
        """Verify h series behavior."""
        for tid in ["H1", "H2", "H3", "H4"]:
            assert tid in THEOREM_REGISTRY
            assert THEOREM_REGISTRY[tid]["series"] == "H"

    # PURPOSE: Verify p series behaves correctly
    def test_p_series(self):
        """Verify p series behavior."""
        for tid in ["P1", "P2", "P3", "P4"]:
            assert tid in THEOREM_REGISTRY
            assert THEOREM_REGISTRY[tid]["series"] == "P"

    # PURPOSE: Verify k series behaves correctly
    def test_k_series(self):
        """Verify k series behavior."""
        for tid in ["K1", "K2", "K3", "K4"]:
            assert tid in THEOREM_REGISTRY
            assert THEOREM_REGISTRY[tid]["series"] == "K"

    # PURPOSE: Verify a series behaves correctly
    def test_a_series(self):
        """Verify a series behavior."""
        for tid in ["A1", "A2", "A3", "A4"]:
            assert tid in THEOREM_REGISTRY
            assert THEOREM_REGISTRY[tid]["series"] == "A"

    # PURPOSE: Verify all have name behaves correctly
    def test_all_have_name(self):
        """Verify all have name behavior."""
        for tid, info in THEOREM_REGISTRY.items():
            assert "name" in info, f"{tid} missing name"
            assert len(info["name"]) > 0

    # PURPOSE: Verify all have wf behaves correctly
    def test_all_have_wf(self):
        """Verify all have wf behavior."""
        for tid, info in THEOREM_REGISTRY.items():
            assert "wf" in info, f"{tid} missing wf"
            assert info["wf"].startswith("/")

    # PURPOSE: Verify all have level behaves correctly
    def test_all_have_level(self):
        """Verify all have level behavior."""
        for tid, info in THEOREM_REGISTRY.items():
            assert "level" in info, f"{tid} missing level"
            assert info["level"].startswith("L")

    # PURPOSE: Verify all have series behaves correctly
    def test_all_have_series(self):
        """Verify all have series behavior."""
        for tid, info in THEOREM_REGISTRY.items():
            assert "series" in info, f"{tid} missing series"
            assert info["series"] in "OSHPKA"

    # ── Specific Theorem Names ──
    # PURPOSE: Verify o1 noesis behaves correctly
    def test_o1_noesis(self):
        """Verify o1 noesis behavior."""
        assert THEOREM_REGISTRY["O1"]["name"] == "Noēsis"

    # PURPOSE: Verify o2 boulesis behaves correctly
    def test_o2_boulesis(self):
        """Verify o2 boulesis behavior."""
        assert THEOREM_REGISTRY["O2"]["name"] == "Boulēsis"

    # PURPOSE: Verify o3 zetesis behaves correctly
    def test_o3_zetesis(self):
        """Verify o3 zetesis behavior."""
        assert THEOREM_REGISTRY["O3"]["name"] == "Zētēsis"

    # PURPOSE: Verify o4 energeia behaves correctly
    def test_o4_energeia(self):
        """Verify o4 energeia behavior."""
        assert THEOREM_REGISTRY["O4"]["name"] == "Energeia"

    # PURPOSE: Verify s1 metron behaves correctly
    def test_s1_metron(self):
        """Verify s1 metron behavior."""
        assert THEOREM_REGISTRY["S1"]["name"] == "Metron"

    # PURPOSE: Verify s2 mekhane behaves correctly
    def test_s2_mekhane(self):
        """Verify s2 mekhane behavior."""
        assert THEOREM_REGISTRY["S2"]["name"] == "Mekhanē"

    # PURPOSE: Verify h1 propatheia behaves correctly
    def test_h1_propatheia(self):
        """Verify h1 propatheia behavior."""
        assert THEOREM_REGISTRY["H1"]["name"] == "Propatheia"

    # PURPOSE: Verify k4 sophia behaves correctly
    def test_k4_sophia(self):
        """Verify k4 sophia behavior."""
        assert THEOREM_REGISTRY["K4"]["name"] == "Sophia"

    # PURPOSE: Verify a2 krisis behaves correctly
    def test_a2_krisis(self):
        """Verify a2 krisis behavior."""
        assert THEOREM_REGISTRY["A2"]["name"] == "Krisis"

    # PURPOSE: Verify a4 episteme behaves correctly
    def test_a4_episteme(self):
        """Verify a4 episteme behavior."""
        assert THEOREM_REGISTRY["A4"]["name"] == "Epistēmē"

    # ── WF Mapping ──
    # PURPOSE: Verify o1 wf behaves correctly
    def test_o1_wf(self):
        """Verify o1 wf behavior."""
        assert THEOREM_REGISTRY["O1"]["wf"] == "/noe"

    # PURPOSE: Verify s2 wf behaves correctly
    def test_s2_wf(self):
        """Verify s2 wf behavior."""
        assert THEOREM_REGISTRY["S2"]["wf"] == "/mek"

    # PURPOSE: Verify a2 wf behaves correctly
    def test_a2_wf(self):
        """Verify a2 wf behavior."""
        assert THEOREM_REGISTRY["A2"]["wf"] == "/dia"

    # PURPOSE: Verify k4 wf behaves correctly
    def test_k4_wf(self):
        """Verify k4 wf behavior."""
        assert THEOREM_REGISTRY["K4"]["wf"] == "/sop"

    # ── Level Consistency ──
    # PURPOSE: Verify o series levels behaves correctly
    def test_o_series_levels(self):
        """Verify o series levels behavior."""
        for tid in ["O1", "O2", "O3", "O4"]:
            assert THEOREM_REGISTRY[tid]["level"] == "L0"

    # PURPOSE: Verify s series levels behaves correctly
    def test_s_series_levels(self):
        """Verify s series levels behavior."""
        for tid in ["S1", "S2", "S3", "S4"]:
            assert THEOREM_REGISTRY[tid]["level"] == "L1"

    # PURPOSE: Verify k series levels behaves correctly
    def test_k_series_levels(self):
        """Verify k series levels behavior."""
        for tid in ["K1", "K2", "K3", "K4"]:
            assert THEOREM_REGISTRY[tid]["level"] == "L3"

    # PURPOSE: Verify a series levels behaves correctly
    def test_a_series_levels(self):
        """Verify a series levels behavior."""
        for tid in ["A1", "A2", "A3", "A4"]:
            assert THEOREM_REGISTRY[tid]["level"] == "L4"


# ── SERIES_INFO ──────────────────────────

# PURPOSE: Test suite validating series info correctness
class TestSeriesInfo:
    """SERIES_INFO 定数のテスト"""

    # PURPOSE: Verify total count behaves correctly
    def test_total_count(self):
        """Verify total count behavior."""
        assert len(SERIES_INFO) == 6

    # PURPOSE: Verify all series present behaves correctly
    def test_all_series_present(self):
        """Verify all series present behavior."""
        expected = {"O", "S", "H", "P", "K", "A"}
        assert set(SERIES_INFO.keys()) == expected

    # PURPOSE: Verify o label behaves correctly
    def test_o_label(self):
        """Verify o label behavior."""
        assert "Ousia" in SERIES_INFO["O"]

    # PURPOSE: Verify s label behaves correctly
    def test_s_label(self):
        """Verify s label behavior."""
        assert "Schema" in SERIES_INFO["S"]

    # PURPOSE: Verify h label behaves correctly
    def test_h_label(self):
        """Verify h label behavior."""
        assert "Hormē" in SERIES_INFO["H"]

    # PURPOSE: Verify p label behaves correctly
    def test_p_label(self):
        """Verify p label behavior."""
        assert "Perigraphē" in SERIES_INFO["P"]

    # PURPOSE: Verify k label behaves correctly
    def test_k_label(self):
        """Verify k label behavior."""
        assert "Kairos" in SERIES_INFO["K"]

    # PURPOSE: Verify a label behaves correctly
    def test_a_label(self):
        """Verify a label behavior."""
        assert "Akribeia" in SERIES_INFO["A"]

    # PURPOSE: Verify all have japanese behaves correctly
    def test_all_have_japanese(self):
        """Verify all have japanese behavior."""
        for key, label in SERIES_INFO.items():
            # Each label should contain Japanese characters
            assert "(" in label, f"{key} missing Japanese in parentheses"
