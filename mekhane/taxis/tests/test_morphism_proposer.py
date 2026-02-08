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


@pytest.fixture
def wf_dir(tmp_path):
    """Temporary workflows directory with test WFs"""
    return tmp_path


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


@pytest.fixture
def no_frontmatter_wf(wf_dir):
    """WF without frontmatter"""
    wf = wf_dir / "no_fm.md"
    wf.write_text("# No frontmatter\n\nJust content.\n")
    return wf


# ── SERIES_NAMES ─────────────────────────

class TestSeriesNames:
    """Series 名称定数のテスト"""

    def test_all_six_series(self):
        expected = {"O", "S", "H", "P", "K", "A"}
        assert set(SERIES_NAMES.keys()) == expected

    def test_names_are_strings(self):
        for k, v in SERIES_NAMES.items():
            assert isinstance(v, str)
            assert len(v) > 0

    def test_ousia(self):
        assert "Ousia" in SERIES_NAMES["O"]

    def test_schema(self):
        assert "Schema" in SERIES_NAMES["S"]


# ── parse_trigonon ───────────────────────

class TestParseTrigonon:
    """Trigonon パーサーのテスト"""

    def test_parse_valid(self, noe_wf):
        result = parse_trigonon(noe_wf)
        assert result is not None
        assert result["series"] == "O"
        assert result["theorem"] == "O1"
        assert result["type"] == "poiesis"

    def test_parse_bridges(self, noe_wf):
        result = parse_trigonon(noe_wf)
        assert "S" in result["bridge"]
        assert "H" in result["bridge"]

    def test_parse_anchors(self, noe_wf):
        result = parse_trigonon(noe_wf)
        assert "K" in result["anchor_via"]

    def test_parse_morphisms(self, noe_wf):
        result = parse_trigonon(noe_wf)
        assert ">>S" in result["morphisms"]
        assert "/met" in result["morphisms"][">>S"]

    def test_parse_no_trigonon(self, no_trigonon_wf):
        result = parse_trigonon(no_trigonon_wf)
        assert result is None

    def test_parse_no_frontmatter(self, no_frontmatter_wf):
        result = parse_trigonon(no_frontmatter_wf)
        assert result is None

    def test_parse_nonexistent_file(self, wf_dir):
        result = parse_trigonon(wf_dir / "nonexistent.md")
        assert result is None


# ── format_proposal ──────────────────────

class TestFormatProposal:
    """射提案フォーマットのテスト"""

    @pytest.fixture
    def sample_trigonon(self):
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

    def test_format_contains_series(self, sample_trigonon):
        result = format_proposal("noe", sample_trigonon)
        assert "O/O1" in result

    def test_format_contains_bridges(self, sample_trigonon):
        result = format_proposal("noe", sample_trigonon)
        assert "Bridge >> S" in result
        assert "Bridge >> H" in result

    def test_format_contains_anchors(self, sample_trigonon):
        result = format_proposal("noe", sample_trigonon)
        assert "Anchor >> K" in result

    def test_confidence_high(self, sample_trigonon):
        result = format_proposal("noe", sample_trigonon, confidence="high")
        assert "収束" in result or "Anchor 優先" in result

    def test_confidence_low(self, sample_trigonon):
        result = format_proposal("noe", sample_trigonon, confidence="low")
        assert "探索" in result or "Bridge 優先" in result

    def test_confidence_neutral(self, sample_trigonon):
        result = format_proposal("noe", sample_trigonon, confidence=None)
        assert "均衡" in result

    def test_format_ends_with_question(self, sample_trigonon):
        result = format_proposal("noe", sample_trigonon)
        assert "?" in result or "？" in result

    def test_format_with_morphism_wfs(self, sample_trigonon):
        result = format_proposal("noe", sample_trigonon)
        assert "/met" in result or "/mek" in result

    def test_format_empty_trigonon(self):
        result = format_proposal("test", {})
        assert "?" in result  # Should still have question


# ── Integration ──────────────────────────

class TestIntegration:
    """Parse → Format 統合テスト"""

    def test_parse_then_format(self, noe_wf):
        trigonon = parse_trigonon(noe_wf)
        assert trigonon is not None
        result = format_proposal("noe", trigonon, confidence="low")
        assert "O/O1" in result
        assert "Bridge" in result
