# PROOF: [L3/テスト] 対象モジュールが存在→検証が必要
"""Tests for quality_gate.py"""

import pytest
from mekhane.quality_gate import QualityGate, MetrikaResult, ChreosItem, PalimpsestItem


class TestMetrika:
    """Metrika 5門テスト"""

    def test_syntomia_pass(self):
        """ネスト3以下はPass"""
        gate = QualityGate()
        lines = [
            "def foo():",
            "    if True:",
            "        for i in range(10):",
            "            print(i)",  # ネスト3
        ]
        result = gate.check_metrika(lines)
        assert result.syntomia is True

    def test_syntomia_fail(self):
        """ネスト4以上はFail"""
        gate = QualityGate()
        lines = [
            "def foo():",
            "    if True:",
            "        for i in range(10):",
            "            if i > 0:",
            "                while True:",
            "                    print(i)",  # ネスト5
        ]
        result = gate.check_metrika(lines)
        assert result.syntomia is False

    def test_atomos_pass(self):
        """120行以下はPass"""
        gate = QualityGate()
        lines = ["line"] * 100
        result = gate.check_metrika(lines)
        assert result.atomos is True

    def test_atomos_fail(self):
        """120行超はFail"""
        gate = QualityGate()
        lines = ["line"] * 150
        result = gate.check_metrika(lines)
        assert result.atomos is False


class TestChreos:
    """Chreos 技術負債テスト"""

    def test_valid_todo(self):
        """正しい形式のTODO"""
        gate = QualityGate()
        lines = ["# TODO(Creator, 2026-03-01): Implement feature"]
        items = gate.check_chreos(lines)
        assert len(items) == 1
        assert items[0].owner == "Creator"
        assert items[0].status == "healthy"

    def test_invalid_todo(self):
        """不正形式のTODOは腐敗扱い"""
        gate = QualityGate()
        lines = ["# TODO: fix later"]
        items = gate.check_chreos(lines)
        assert len(items) == 1
        assert items[0].status == "rotten"


class TestPalimpsest:
    """Palimpsest コード考古学テスト"""

    def test_hack_detection(self):
        """HACKパターン検出"""
        gate = QualityGate()
        lines = ["# HACK: temporary fix"]
        items = gate.check_palimpsest(lines)
        assert any(p.pattern == "HACK" for p in items)

    def test_fixme_detection(self):
        """FIXMEパターン検出"""
        gate = QualityGate()
        lines = ["# FIXME: this is broken"]
        items = gate.check_palimpsest(lines)
        assert any(p.pattern == "FIXME" for p in items)


class TestIntegration:
    """統合テスト"""

    def test_check_file_self(self):
        """自己検証が動作する"""
        gate = QualityGate()
        result = gate.check_file("mekhane/quality_gate.py")
        assert "metrika" in result
        assert "chreos" in result
        assert "palimpsest" in result
