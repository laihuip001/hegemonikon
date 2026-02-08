#!/usr/bin/env python3
# PROOF: [L3/テスト] <- scripts/tests/
"""
PROOF: [L3/テスト] このファイルは存在しなければならない

A0 → wf_postcheck.py の naturality check が正しく機能することを検証
   → η/ε/η_MP の可換性テスト + boot post-check 統合テスト
   → test_naturality_postcheck.py が担う

Q.E.D.
"""

import pytest
import sys
import os

# scripts/ からの相対 import を可能にする
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from scripts.wf_postcheck import check_naturality


# PURPOSE: check_naturality() — 全自然変換の可換性検証。
class TestCheckNaturality:
    """check_naturality() — 全自然変換の可換性検証。"""

    # PURPOSE: check_naturality() はリストを返す。
    def test_returns_list(self):
        """check_naturality() はリストを返す。"""
        result = check_naturality()
        assert isinstance(result, list)

    # PURPOSE: 少なくとも 3 つのチェック (η, ε, η_MP) が返る。
    def test_has_checks(self):
        """少なくとも 3 つのチェック (η, ε, η_MP) が返る。"""
        result = check_naturality()
        assert len(result) >= 3

    # PURPOSE: η (boot⊣bye unit) のチェックが存在する。
    def test_eta_check_exists(self):
        """η (boot⊣bye unit) のチェックが存在する。"""
        result = check_naturality()
        names = [c["name"] for c in result]
        assert "naturality_eta" in names

    # PURPOSE: ε (boot⊣bye counit) のチェックが存在する。
    def test_epsilon_check_exists(self):
        """ε (boot⊣bye counit) のチェックが存在する。"""
        result = check_naturality()
        names = [c["name"] for c in result]
        assert "naturality_epsilon" in names

    # PURPOSE: η_MP (MP↔HGK) のチェックが存在する。
    def test_mp_hgk_check_exists(self):
        """η_MP (MP↔HGK) のチェックが存在する。"""
        result = check_naturality()
        names = [c["name"] for c in result]
        assert "naturality_mp_hgk" in names

    # PURPOSE: η_MP は natural と判定される。
    def test_mp_hgk_is_natural(self):
        """η_MP は natural と判定される。"""
        result = check_naturality()
        mp_check = next(c for c in result if c["name"] == "naturality_mp_hgk")
        assert mp_check["passed"]

    # PURPOSE: 全チェックに detail フィールドがある。
    def test_all_checks_have_detail(self):
        """全チェックに detail フィールドがある。"""
        result = check_naturality()
        for c in result:
            assert "detail" in c
            assert len(c["detail"]) > 0

    # PURPOSE: check_naturality の出力が postcheck のフォーマットと互換。
    def test_check_format_compatible_with_postcheck(self):
        """check_naturality の出力が postcheck のフォーマットと互換。"""
        result = check_naturality()
        for c in result:
            assert "name" in c
            assert "passed" in c
            assert "detail" in c
            assert isinstance(c["passed"], bool)
