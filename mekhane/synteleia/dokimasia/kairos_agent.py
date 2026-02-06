# PROOF: [L1/定理] <- mekhane/synteleia/dokimasia/ K1 Eukairia 時宜判断エージェント
"""
Kairos Agent - Timing Evaluation

「今か」を問う時宜判断エージェント。
タイミング違反、時宜の誤りを検出。

CCL: /k (K-series)
FEP: 時間的文脈での精密化
"""

import re
from typing import List

from ..base import (
    AgentResult,
    AuditAgent,
    AuditIssue,
    AuditSeverity,
    AuditTarget,
    AuditTargetType,
)


class KairosAgent(AuditAgent):
    """時宜判断エージェント (K-Agent)"""

    name = "KairosAgent"
    description = "タイミングの妥当性を検証 — 「今か」"

    # タイミング問題パターン
    TIMING_PROBLEMS = [
        (re.compile(r"\b後で\b", re.IGNORECASE), "K-001", "「後で」は先延ばしの兆候"),
        (re.compile(r"\bいつか\b", re.IGNORECASE), "K-002", "「いつか」は時宜が不明確"),
        (re.compile(r"\bそのうち\b", re.IGNORECASE), "K-003", "「そのうち」は時宜が不明確"),
        (re.compile(r"\blater\b(?!\s+than)", re.IGNORECASE), "K-004", "「later」は先延ばしの兆候"),
        (re.compile(r"\bsomeday\b", re.IGNORECASE), "K-005", "「someday」は時宜が不明確"),
        (re.compile(r"\beventually\b", re.IGNORECASE), "K-006", "「eventually」は時宜が曖昧"),
    ]

    # 時間的コンテキストキーワード
    TEMPORAL_KEYWORDS = [
        "期限",
        "deadline",
        "due",
        "by",
        "until",
        "before",
        "after",
        "when",
        "今日",
        "明日",
        "今週",
        "今月",
    ]

    # 早すぎる最適化パターン
    PREMATURE_PATTERNS = [
        (re.compile(r"\b最適化\b.*\bまず\b", re.IGNORECASE), "K-010", "早すぎる最適化の兆候"),
        (re.compile(r"\boptimiz\w*\b.*\bfirst\b", re.IGNORECASE), "K-011", "Premature optimization detected"),
        (re.compile(r"\bパフォーマンス\b.*\b前に\b", re.IGNORECASE), "K-012", "機能完成前のパフォーマンス議論"),
    ]

    def audit(self, target: AuditTarget) -> AgentResult:
        """タイミングの妥当性を監査"""
        issues: List[AuditIssue] = []
        content = target.content

        # タイミング問題パターンを検出
        issues.extend(self._check_timing_problems(content))

        # 早すぎる最適化を検出
        issues.extend(self._check_premature_optimization(content))

        # 計画には時間的コンテキストが必要
        if target.target_type == AuditTargetType.PLAN:
            issues.extend(self._check_temporal_context(content))

        passed = not any(
            i.severity in (AuditSeverity.CRITICAL, AuditSeverity.HIGH) for i in issues
        )

        return AgentResult(
            agent_name=self.name,
            passed=passed,
            issues=issues,
            confidence=0.70,  # タイミング判定は文脈依存
        )

    def _check_timing_problems(self, content: str) -> List[AuditIssue]:
        """タイミング問題パターンを検出"""
        issues = []

        for pattern, code, message in self.TIMING_PROBLEMS:
            for match in pattern.finditer(content):
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code=code,
                        severity=AuditSeverity.LOW,
                        message=message,
                        location=f"position {match.start()}",
                        suggestion="具体的な時期を明記してください",
                    )
                )

        return issues

    def _check_premature_optimization(self, content: str) -> List[AuditIssue]:
        """早すぎる最適化を検出"""
        issues = []

        for pattern, code, message in self.PREMATURE_PATTERNS:
            for match in pattern.finditer(content):
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code=code,
                        severity=AuditSeverity.MEDIUM,
                        message=message,
                        location=f"position {match.start()}",
                        suggestion="まず動くものを作り、その後最適化",
                    )
                )

        return issues

    def _check_temporal_context(self, content: str) -> List[AuditIssue]:
        """時間的コンテキストの存在を検出（計画向け）"""
        issues = []
        content_lower = content.lower()

        # 時間キーワードの存在チェック
        has_temporal = any(kw in content_lower for kw in self.TEMPORAL_KEYWORDS)

        if not has_temporal:
            issues.append(
                AuditIssue(
                    agent=self.name,
                    code="K-020",
                    severity=AuditSeverity.INFO,
                    message="計画に時間的コンテキストがありません",
                    suggestion="期限や時間枠を明記すると計画が具体化します",
                )
            )

        return issues

    def supports(self, target_type: AuditTargetType) -> bool:
        """全タイプをサポート（特に計画に有効）"""
        return True
