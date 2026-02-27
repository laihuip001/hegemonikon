#!/usr/bin/env python3
# PROOF: [L2/Mekhane] <- mekhane/symploke/ A0->Auto->AddedByCI
# PROOF: [L2/データフロー] <- mekhane/symploke/ S2→issue→specialist ルーティング
# PURPOSE: AIAuditor issue コード → Specialist カテゴリ 自動マッチング
"""
Audit-Specialist Auto Matcher

AIAuditor が検出した issue のコードに基づき、
最適な Specialist カテゴリを自動選択する。
ランダムサンプリングを adaptive に変換する F7 基盤。

Integration:
    - jules_daily_scheduler.py: --pre-audit 時に run_slot_batch() 内で自動発動
    - run_slot_batch(audit_issue_codes=[...]) で issue ベースの specialist 選択が有効化

Usage:
    from audit_specialist_matcher import AuditSpecialistMatcher, match_issues_to_specialists

    matcher = AuditSpecialistMatcher()
    specialists = matcher.select_for_issues(issues, total_budget=20)
"""

from dataclasses import dataclass
from typing import Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))


# PURPOSE: AIAuditor コード → Specialist カテゴリの静的マッピング
# AIAuditor codes are defined in mekhane/basanos/ai_auditor.py
AUDIT_CODE_TO_SPECIALIST_CATEGORIES: dict[str, list[str]] = {
    "AI-001": ["naming", "code_review"],           # Naming Hallucination
    "AI-002": ["api_design", "type_safety"],        # API Misuse
    "AI-003": ["type_safety", "code_review"],       # Type Confusion
    "AI-004": ["edge_case", "code_review"],         # Logic Hallucination
    "AI-005": ["code_review", "error_handling"],    # Incomplete Code
    "AI-006": ["cognitive", "documentation"],       # Context Drift
    "AI-007": ["aesthetics", "code_review"],        # Pattern Inconsistency
    "AI-008": ["code_review", "documentation"],     # Self-Contradiction
    "AI-009": ["security"],                         # Security Vulnerabilities
    "AI-010": ["edge_case", "error_handling"],      # Input Validation Omission
    "AI-011": ["edge_case", "testing"],             # Boundary Condition Error
    "AI-012": ["async", "performance"],             # Async Misuse
    "AI-013": ["async", "performance"],             # Concurrency Issues
    "AI-014": ["error_handling"],                   # Error Handling Gaps
    "AI-015": ["performance"],                      # Resource Leak
    "AI-016": ["documentation"],                    # Docstring Mismatch
    "AI-017": ["testing"],                          # Missing Tests
    "AI-018": ["database"],                         # SQL Injection / DB issues
    "AI-019": ["api_design"],                       # Import Issues
    "AI-020": ["hegemonikon"],                      # HGK-specific issues
    "AI-021": ["code_review", "ai_generated"],      # AI-Generated Code smell
    "AI-022": ["code_review"],                      # Complexity Issues
}

# Category priority weights (higher = more important when allocating budget)
CATEGORY_PRIORITY: dict[str, float] = {
    "security": 3.0,
    "async": 2.0,
    "error_handling": 2.0,
    "type_safety": 1.8,
    "edge_case": 1.5,
    "performance": 1.5,
    "api_design": 1.3,
    "testing": 1.2,
    "naming": 1.0,
    "code_review": 1.0,
    "documentation": 0.8,
    "aesthetics": 0.7,
    "cognitive": 0.7,
    "database": 1.5,
    "hegemonikon": 1.0,
    "ai_generated": 1.2,
    "class_design": 1.0,
    "function_design": 1.0,
    "git": 0.5,
    "japanese": 0.5,
    "ultimate": 0.5,
}


# PURPOSE: issue の集計からカテゴリ別の必要スペシャリスト数を算出
@dataclass
class CategoryAllocation:
    """カテゴリへのスペシャリスト割り当て。"""
    category: str
    raw_score: float     # issue 数 × priority weight
    allocated: int       # 割り当てスペシャリスト数
    source_codes: list[str]  # この割り当ての元になった AI-xxx コード


class AuditSpecialistMatcher:
    """AIAuditor issue → Specialist カテゴリの adaptive マッチャー。"""

    def __init__(self, mapping: Optional[dict[str, list[str]]] = None):
        self._mapping = mapping or AUDIT_CODE_TO_SPECIALIST_CATEGORIES

    def get_categories_for_code(self, code: str) -> list[str]:
        """AI-xxx コード → 関連カテゴリリスト。"""
        return self._mapping.get(code, ["code_review"])  # fallback: code_review

    def score_categories(self, issue_codes: list[str]) -> dict[str, float]:
        """Issue コードの集合からカテゴリ別スコアを算出。

        スコア = 出現回数 × カテゴリ priority weight
        """
        cat_counts: dict[str, float] = {}
        cat_sources: dict[str, list[str]] = {}

        for code in issue_codes:
            categories = self.get_categories_for_code(code)
            for cat in categories:
                weight = CATEGORY_PRIORITY.get(cat, 1.0)
                cat_counts[cat] = cat_counts.get(cat, 0.0) + weight
                if cat not in cat_sources:
                    cat_sources[cat] = []
                if code not in cat_sources[cat]:
                    cat_sources[cat].append(code)

        return cat_counts

    def allocate_budget(
        self,
        issue_codes: list[str],
        total_budget: int = 20,
        min_per_category: int = 1,
    ) -> list[CategoryAllocation]:
        """Issue コードに基づいてスペシャリスト budget を配分。

        Args:
            issue_codes: 検出された AI-xxx コードのリスト (重複可)
            total_budget: 割り当てスペシャリスト総数
            min_per_category: カテゴリあたりの最小割り当て

        Returns:
            カテゴリ別の割り当てリスト (スコア降順)
        """
        if not issue_codes:
            return []

        cat_scores = self.score_categories(issue_codes)

        if not cat_scores:
            return []

        # スコアの合計
        total_score = sum(cat_scores.values())

        # 比例配分 (少なくとも min_per_category)
        allocations = []
        remaining = total_budget

        # source codes tracking
        cat_sources: dict[str, list[str]] = {}
        for code in issue_codes:
            for cat in self.get_categories_for_code(code):
                if cat not in cat_sources:
                    cat_sources[cat] = []
                if code not in cat_sources[cat]:
                    cat_sources[cat].append(code)

        sorted_cats = sorted(cat_scores.items(), key=lambda x: x[1], reverse=True)

        for cat, score in sorted_cats:
            if remaining <= 0:
                break
            proportion = score / total_score
            allocated = max(min_per_category, round(proportion * total_budget))
            allocated = min(allocated, remaining)
            allocations.append(CategoryAllocation(
                category=cat,
                raw_score=score,
                allocated=allocated,
                source_codes=cat_sources.get(cat, []),
            ))
            remaining -= allocated

        return allocations

    def select_for_issues(
        self,
        issue_codes: list[str],
        total_budget: int = 20,
    ) -> list[str]:
        """Issue コードから最適な specialist カテゴリを選択し、カテゴリ名リストを返す。

        Usage with specialist_v2:
            categories = matcher.select_for_issues(["AI-009", "AI-012"], total_budget=10)
            specialists = []
            for cat in categories:
                pool = get_specialists_by_category(cat)
                specialists.extend(random.sample(pool, min(per_cat, len(pool))))
        """
        allocations = self.allocate_budget(issue_codes, total_budget)
        result = []
        for alloc in allocations:
            result.extend([alloc.category] * alloc.allocated)
        return result


def match_issues_to_specialists(issue_codes: list[str], budget: int = 20) -> list[CategoryAllocation]:
    """Convenience function: issue codes → category allocations."""
    matcher = AuditSpecialistMatcher()
    return matcher.allocate_budget(issue_codes, budget)
