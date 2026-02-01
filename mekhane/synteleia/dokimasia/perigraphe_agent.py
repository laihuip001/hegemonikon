# PROOF: [L1/定理] P1 Khōra 境界画定エージェント
"""
Perigraphē Agent - Boundary Evaluation

「どこまでか」を問う境界評価エージェント。
スコープ逸脱、境界侵害を検出。

CCL: /p (P-series)
FEP: モデルの境界条件
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


class PerigrapheAgent(AuditAgent):
    """境界画定エージェント (P-Agent)"""

    name = "PerigrapheAgent"
    description = "スコープの妥当性を検証 — 「どこまでか」"

    # スコープ逸脱パターン
    SCOPE_CREEP_PATTERNS = [
        (r"\bついでに\b", "P-001", "「ついでに」はスコープ逸脱の兆候"),
        (r"\bwhile\s+(?:we're|I'm)\s+at\s+it\b", "P-002", "スコープ逸脱の兆候"),
        (r"\bまた(?:は|も)\b.*\bも\b", "P-003", "複数の目的が混在"),
        (r"\band\s+also\b", "P-004", "範囲が曖昧に拡大"),
    ]

    # 境界明示キーワード
    BOUNDARY_KEYWORDS = [
        "スコープ",
        "範囲",
        "対象外",
        "対象内",
        "scope",
        "out of scope",
        "in scope",
        "boundary",
        "limit",
    ]

    def audit(self, target: AuditTarget) -> AgentResult:
        """スコープの妥当性を監査"""
        issues: List[AuditIssue] = []
        content = target.content

        # スコープ逸脱パターンを検出
        issues.extend(self._check_scope_creep(content))

        # 計画には境界定義が必要
        if target.target_type == AuditTargetType.PLAN:
            issues.extend(self._check_boundary_definition(content))

        passed = not any(
            i.severity in (AuditSeverity.CRITICAL, AuditSeverity.HIGH) for i in issues
        )

        return AgentResult(
            agent_name=self.name,
            passed=passed,
            issues=issues,
            confidence=0.75,
        )

    def _check_scope_creep(self, content: str) -> List[AuditIssue]:
        """スコープ逸脱パターンを検出"""
        issues = []

        for pattern, code, message in self.SCOPE_CREEP_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code=code,
                        severity=AuditSeverity.LOW,
                        message=message,
                        location=f"position {match.start()}",
                        suggestion="スコープを明確に分離してください",
                    )
                )

        return issues

    def _check_boundary_definition(self, content: str) -> List[AuditIssue]:
        """境界定義の存在を検出（計画向け）"""
        issues = []
        content_lower = content.lower()

        # 境界キーワードの存在チェック
        has_boundary = any(kw in content_lower for kw in self.BOUNDARY_KEYWORDS)

        if not has_boundary:
            issues.append(
                AuditIssue(
                    agent=self.name,
                    code="P-010",
                    severity=AuditSeverity.MEDIUM,
                    message="計画にスコープ/境界が明示されていません",
                    suggestion="「スコープ:」「対象外:」で境界を明記",
                )
            )

        return issues

    def supports(self, target_type: AuditTargetType) -> bool:
        """全タイプをサポート（特に計画に有効）"""
        return True
