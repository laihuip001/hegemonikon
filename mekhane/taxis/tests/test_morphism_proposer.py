#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/taxis/tests/
# PURPOSE: Morphism Proposer (X-series射提案エンジン) の包括テスト
"""Morphism Proposer Tests"""

import pytest
from pathlib import Path
from mekhane.taxis.morphism_proposer import (
    parse_trigonon,
    format_proposal,
    SERIES_NAMES,
)


# PURPOSE: Verify wf dir behaves correctly
@pytest.fixture
def wf_dir(tmp_path):
    """Temporary workflows directory with test WFs"""
    return tmp_path


# PURPOSE: Verify noe wf behaves correctly
@pytest.fixture
def noe_wf(wf_dir):
    """O1 Noēsis WF with trigonon"""
    wf = wf_dir / "noe.md"
    wf.write_text("""---
description: Test WF
trigonon:
  series: O
  type: poiesis
  theorem: O1
  bridge: [S, H]
  anchor_via: [K]
  morphisms:
    ">>S": [/met, /mek]
    ">>H": [/pro, /pis]
---

# Test WF Content
""")
    return wf


# PURPOSE: Verify no trigonon wf behaves correctly
@pytest.fixture
def no_trigonon_wf(wf_dir):
    """WF without trigonon"""
    wf = wf_dir / "plain.md"
    wf.write_text("""---
description: Plain WF without trigonon
---

# Plain WF
""")
    return wf


# PURPOSE: Verify no frontmatter wf behaves correctly
@pytest.fixture
def no_frontmatter_wf(wf_dir):
    """WF without frontmatter"""
    wf = wf_dir / "no_fm.md"
    wf.write_text("# No frontmatter\n\nJust content.\n")
    return wf


# ── SERIES_NAMES ─────────────────────────

# PURPOSE: Test suite validating series names correctness
class TestSeriesNames:
    """Series 名称定数のテスト"""

    # PURPOSE: Verify all six series behaves correctly
    def test_all_six_series(self):
        """Verify all six series behavior."""
        expected = {"O", "S", "H", "P", "K", "A"}
        assert set(SERIES_NAMES.keys()) == expected

    # PURPOSE: Verify names are strings behaves correctly
    def test_names_are_strings(self):
        """Verify names are strings behavior."""
        for k, v in SERIES_NAMES.items():
            assert isinstance(v, str)
            assert len(v) > 0

    # PURPOSE: Verify ousia behaves correctly
    def test_ousia(self):
        """Verify ousia behavior."""
        assert "Ousia" in SERIES_NAMES["O"]

    # PURPOSE: Verify schema behaves correctly
    def test_schema(self):
        """Verify schema behavior."""
        assert "Schema" in SERIES_NAMES["S"]


# ── parse_trigonon ───────────────────────

# PURPOSE: Test suite validating parse trigonon correctness
class TestParseTrigonon:
    """Trigonon パーサーのテスト"""

    # PURPOSE: Verify parse valid behaves correctly
    def test_parse_valid(self, noe_wf):
        """Verify parse valid behavior."""
        result = parse_trigonon(noe_wf)
        assert result is not None
        assert result["series"] == "O"
        assert result["theorem"] == "O1"
        assert result["type"] == "poiesis"

    # PURPOSE: Verify parse bridges behaves correctly
    def test_parse_bridges(self, noe_wf):
        """Verify parse bridges behavior."""
        result = parse_trigonon(noe_wf)
        assert "S" in result["bridge"]
        assert "H" in result["bridge"]

    # PURPOSE: Verify parse anchors behaves correctly
    def test_parse_anchors(self, noe_wf):
        """Verify parse anchors behavior."""
        result = parse_trigonon(noe_wf)
        assert "K" in result["anchor_via"]

    # PURPOSE: Verify parse morphisms behaves correctly
    def test_parse_morphisms(self, noe_wf):
        """Verify parse morphisms behavior."""
        result = parse_trigonon(noe_wf)
        assert ">>S" in result["morphisms"]
        assert "/met" in result["morphisms"][">>S"]

    # PURPOSE: Verify parse no trigonon behaves correctly
    def test_parse_no_trigonon(self, no_trigonon_wf):
        """Verify parse no trigonon behavior."""
        result = parse_trigonon(no_trigonon_wf)
        assert result is None

    # PURPOSE: Verify parse no frontmatter behaves correctly
    def test_parse_no_frontmatter(self, no_frontmatter_wf):
        """Verify parse no frontmatter behavior."""
        result = parse_trigonon(no_frontmatter_wf)
        assert result is None

    # PURPOSE: Verify parse nonexistent file behaves correctly
    def test_parse_nonexistent_file(self, wf_dir):
        """Verify parse nonexistent file behavior."""
        result = parse_trigonon(wf_dir / "nonexistent.md")
        assert result is None


# ── format_proposal ──────────────────────

# PURPOSE: Test suite validating format proposal correctness
class TestFormatProposal:
    """射提案フォーマットのテスト"""

    # PURPOSE: Verify sample trigonon behaves correctly
    @pytest.fixture
    def sample_trigonon(self):
        """Verify sample trigonon behavior."""
        return {
            "series": "O",
            "theorem": "O1",
            "type": "poiesis",
            "bridge": ["S", "H"],
            "anchor_via": ["K"],
            "morphisms": {
                ">>S": ["/met", "/mek"],
                ">>H": ["/pro", "/pis"],
            },
        }

    # PURPOSE: Verify format contains series behaves correctly
    def test_format_contains_series(self, sample_trigonon):
        """Verify format contains series behavior."""
        result = format_proposal("noe", sample_trigonon)
        assert "O/O1" in result

    # PURPOSE: Verify format contains bridges behaves correctly
    def test_format_contains_bridges(self, sample_trigonon):
        """Verify format contains bridges behavior."""
        result = format_proposal("noe", sample_trigonon)
        assert "Bridge >> S" in result
        assert "Bridge >> H" in result

    # PURPOSE: Verify format contains anchors behaves correctly
    def test_format_contains_anchors(self, sample_trigonon):
        """Verify format contains anchors behavior."""
        result = format_proposal("noe", sample_trigonon)
        assert "Anchor >> K" in result

    # PURPOSE: Verify confidence high behaves correctly
    def test_confidence_high(self, sample_trigonon):
        """Verify confidence high behavior."""
        result = format_proposal("noe", sample_trigonon, confidence="high")
        assert "収束" in result or "Anchor 優先" in result

    # PURPOSE: Verify confidence low behaves correctly
    def test_confidence_low(self, sample_trigonon):
        """Verify confidence low behavior."""
        result = format_proposal("noe", sample_trigonon, confidence="low")
        assert "探索" in result or "Bridge 優先" in result

    # PURPOSE: Verify confidence neutral behaves correctly
    def test_confidence_neutral(self, sample_trigonon):
        """Verify confidence neutral behavior."""
        result = format_proposal("noe", sample_trigonon, confidence=None)
        assert "均衡" in result

    # PURPOSE: Verify format ends with question behaves correctly
    def test_format_ends_with_question(self, sample_trigonon):
        """Verify format ends with question behavior."""
        result = format_proposal("noe", sample_trigonon)
        assert "?" in result or "？" in result

    # PURPOSE: Verify format with morphism wfs behaves correctly
    def test_format_with_morphism_wfs(self, sample_trigonon):
        """Verify format with morphism wfs behavior."""
        result = format_proposal("noe", sample_trigonon)
        assert "/met" in result or "/mek" in result

    # PURPOSE: Verify format empty trigonon behaves correctly
    def test_format_empty_trigonon(self):
        """Verify format empty trigonon behavior."""
        result = format_proposal("test", {})
        assert "?" in result  # Should still have question


# ── Integration ──────────────────────────

# PURPOSE: Test suite validating integration correctness
class TestIntegration:
    """Parse → Format 統合テスト"""

    # PURPOSE: Verify parse then format behaves correctly
    def test_parse_then_format(self, noe_wf):
        """Verify parse then format behavior."""
        trigonon = parse_trigonon(noe_wf)
        assert trigonon is not None
        result = format_proposal("noe", trigonon, confidence="low")
        assert "O/O1" in result
        assert "Bridge" in result
