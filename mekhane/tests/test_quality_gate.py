# PROOF: [L3/テスト] <- mekhane/tests/ 対象モジュールが存在→検証が必要
"""Tests for quality_gate.py"""

import pytest
from mekhane.quality_gate import QualityGate, MetrikaResult, ChreosItem, PalimpsestItem


# PURPOSE: Metrika 5門テスト
class TestMetrika:
    """Metrika 5門テスト"""

    # PURPOSE: ネスト3以下はPass
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

    # PURPOSE: ネスト4以上はFail
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

    # PURPOSE: 120行以下はPass
    def test_atomos_pass(self):
        """120行以下はPass"""
        gate = QualityGate()
        lines = ["line"] * 100
        result = gate.check_metrika(lines)
        assert result.atomos is True

    # PURPOSE: 120行超はFail
    def test_atomos_fail(self):
        """120行超はFail"""
        gate = QualityGate()
        lines = ["line"] * 150
        result = gate.check_metrika(lines)
        assert result.atomos is False


# PURPOSE: Chreos 技術負債テスト
class TestChreos:
    """Chreos 技術負債テスト"""

    # PURPOSE: 正しい形式のTODO
    def test_valid_todo(self):
        """正しい形式のTODO"""
        gate = QualityGate()
        lines = ["# TODO(Creator, 2026-03-01): Implement feature"]
        items = gate.check_chreos(lines)
        assert len(items) == 1
        assert items[0].owner == "Creator"
        assert items[0].status == "healthy"

    # PURPOSE: 不正形式のTODOは腐敗扱い
    def test_invalid_todo(self):
        """不正形式のTODOは腐敗扱い"""
        gate = QualityGate()
        lines = ["# TODO: fix later"]
        items = gate.check_chreos(lines)
        assert len(items) == 1
        assert items[0].status == "rotten"


# PURPOSE: Palimpsest コード考古学テスト
class TestPalimpsest:
    """Palimpsest コード考古学テスト"""

    # PURPOSE: HACKパターン検出
    def test_hack_detection(self):
        """HACKパターン検出"""
        gate = QualityGate()
        lines = ["# HACK: temporary fix"]
        items = gate.check_palimpsest(lines)
        assert any(p.pattern == "HACK" for p in items)

    # PURPOSE: FIXMEパターン検出
    def test_fixme_detection(self):
        """FIXMEパターン検出"""
        gate = QualityGate()
        lines = ["# FIXME: this is broken"]
        items = gate.check_palimpsest(lines)
        assert any(p.pattern == "FIXME" for p in items)


# PURPOSE: 統合テスト
class TestIntegration:
    """統合テスト"""

    # PURPOSE: 自己検証が動作する
    def test_check_file_self(self):
        """自己検証が動作する"""
        gate = QualityGate()
        result = gate.check_file("mekhane/quality_gate.py")
        assert "metrika" in result
        assert "chreos" in result
        assert "palimpsest" in result
