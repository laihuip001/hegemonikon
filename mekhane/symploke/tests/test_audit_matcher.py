#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/symploke/tests/
# PURPOSE: F7/F8 のユニットテスト
"""Tests for Audit-Specialist Matcher and Dynamic Perspective Generator."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from audit_specialist_matcher import (
    AuditSpecialistMatcher,
    CategoryAllocation,
    match_issues_to_specialists,
)
from dynamic_perspective_generator import (
    DynamicPerspectiveGenerator,
    FileProfile,
)


class TestAuditSpecialistMatcher:
    """F7: AIAuditor → Specialist マッチングテスト。"""

    @pytest.fixture
    def matcher(self):
        return AuditSpecialistMatcher()

    def test_known_code_returns_categories(self, matcher):
        """既知のコードはカテゴリを返す。"""
        cats = matcher.get_categories_for_code("AI-009")
        assert "security" in cats

    def test_unknown_code_returns_fallback(self, matcher):
        """未知のコードは code_review にフォールバック。"""
        cats = matcher.get_categories_for_code("AI-999")
        assert cats == ["code_review"]

    def test_score_categories(self, matcher):
        """スコアリング — security は priority 3.0。"""
        scores = matcher.score_categories(["AI-009", "AI-009"])
        assert scores["security"] == pytest.approx(6.0)  # 2 × 3.0

    def test_allocate_budget_basic(self, matcher):
        """Budget 配分 — 単一カテゴリ。"""
        allocs = matcher.allocate_budget(["AI-009"], total_budget=5)
        assert len(allocs) >= 1
        total_allocated = sum(a.allocated for a in allocs)
        assert total_allocated <= 5

    def test_allocate_budget_mixed(self, matcher):
        """Budget 配分 — 複数カテゴリ。"""
        allocs = matcher.allocate_budget(
            ["AI-009", "AI-012", "AI-001"],
            total_budget=10,
        )
        assert len(allocs) >= 2
        total_allocated = sum(a.allocated for a in allocs)
        assert total_allocated <= 10

    def test_allocate_budget_empty(self, matcher):
        """空の issue → 空の配分。"""
        allocs = matcher.allocate_budget([], total_budget=10)
        assert allocs == []

    def test_select_for_issues(self, matcher):
        """select_for_issues はカテゴリ名のリストを返す。"""
        result = matcher.select_for_issues(["AI-009", "AI-012"], total_budget=10)
        assert isinstance(result, list)
        assert len(result) <= 10
        assert all(isinstance(c, str) for c in result)

    def test_convenience_function(self):
        """match_issues_to_specialists 関数。"""
        allocs = match_issues_to_specialists(["AI-009"], budget=5)
        assert isinstance(allocs, list)
        assert all(isinstance(a, CategoryAllocation) for a in allocs)


class TestDynamicPerspectiveGenerator:
    """F8: 動的 Perspective 生成テスト。"""

    @pytest.fixture
    def generator(self):
        return DynamicPerspectiveGenerator(max_perspectives=10)

    def test_profile_nonexistent_file(self, generator):
        """存在しないファイルのプロファイル。"""
        profile = generator.profile_file("/nonexistent/file.py")
        assert profile.lines == 0
        assert profile.detected_domains == []

    def test_profile_real_file(self, generator):
        """実在するファイルのプロファイル。"""
        # 自分自身をテスト
        this_file = str(Path(__file__).resolve())
        profile = generator.profile_file(this_file)
        assert profile.lines > 0
        assert profile.language == "python"

    def test_generate_for_nonexistent(self, generator):
        """存在しないファイルでも universal perspective は生成される。"""
        perspectives = generator.generate_for_file("/nonexistent/file.py")
        assert len(perspectives) >= 1  # Universal perspectives

    def test_generate_with_audit_issues(self, generator):
        """Audit issues 付きの dynamic perspective。"""
        this_file = str(Path(__file__).resolve())
        perspectives = generator.generate_for_file(
            this_file,
            audit_issues=["AI-009", "AI-012"],
        )
        # security/async 関連の perspective が含まれるはず
        domains = [p.domain for p in perspectives]
        assert len(perspectives) >= 2

    def test_max_perspectives_limit(self):
        """max_perspectives の制限。"""
        gen = DynamicPerspectiveGenerator(max_perspectives=3)
        this_file = str(Path(__file__).resolve())
        perspectives = gen.generate_for_file(
            this_file,
            audit_issues=["AI-009", "AI-012", "AI-001", "AI-002", "AI-003"],
        )
        assert len(perspectives) <= 3

    def test_severity_ordering(self, generator):
        """critical > high > medium > low の順序。"""
        this_file = str(Path(__file__).resolve())
        perspectives = generator.generate_for_file(
            this_file,
            audit_issues=["AI-009"],  # critical
        )
        if len(perspectives) >= 2:
            severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
            for i in range(len(perspectives) - 1):
                assert severity_order.get(perspectives[i].severity, 4) <= \
                       severity_order.get(perspectives[i+1].severity, 4)
