#!/usr/bin/env python3
"""Tests for gnosis_advisor.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.gnosis_advisor import (
    WF_TOPICS,
    PRIORITY_SOURCES,
    list_topics,
    search_for_wf,
)


class TestConfig:
    """設定のテスト"""

    def test_wf_topics_not_empty(self):
        """WF トピックマッピングが空でない"""
        assert len(WF_TOPICS) > 0

    def test_all_series_covered(self):
        """O/S/H/A/K の各 Series が含まれている"""
        # O-series
        assert "noe" in WF_TOPICS
        assert "bou" in WF_TOPICS
        assert "zet" in WF_TOPICS
        assert "ene" in WF_TOPICS
        # S-series
        assert "mek" in WF_TOPICS
        # H-series
        assert "pis" in WF_TOPICS
        # A-series
        assert "dia" in WF_TOPICS
        # K-series
        assert "sop" in WF_TOPICS

    def test_topics_are_lists(self):
        """各 WF のトピックがリスト"""
        for wf, topics in WF_TOPICS.items():
            assert isinstance(topics, list), f"/{wf} topics is not a list"
            assert len(topics) >= 1, f"/{wf} has no topics"

    def test_priority_sources(self):
        """学術系ソースが優先リストに含まれる"""
        assert "arxiv" in PRIORITY_SOURCES
        assert "research" in PRIORITY_SOURCES


class TestListTopics:
    """トピック一覧のテスト"""

    def test_output_not_empty(self):
        output = list_topics()
        assert len(output) > 0

    def test_contains_header(self):
        output = list_topics()
        assert "トピックマッピング" in output

    def test_contains_wf_names(self):
        output = list_topics()
        assert "/noe" in output
        assert "/dia" in output


class TestSearchForWf:
    """WF 検索のテスト"""

    def test_unknown_wf(self):
        """未定義 WF はエラーメッセージ"""
        result = search_for_wf("nonexistent")
        assert "トピック定義がありません" in result

    def test_known_wf_returns_string(self):
        """定義済み WF は文字列を返す"""
        result = search_for_wf("noe", limit=1)
        assert isinstance(result, str)
        assert len(result) > 0
