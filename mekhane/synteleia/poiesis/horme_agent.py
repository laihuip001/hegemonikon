# PROOF: [L1/定理] <- mekhane/synteleia/poiesis/ H3 Orexis 動機評価エージェント
"""
Hormē Agent - Motivation Evaluation

「なぜこれを望むか」を問う動機評価エージェント。
動機の不整合、目的の欠如を検出。

CCL: /h (H-series)
FEP: 行動選択の駆動力（精密化の方向）
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


class HormeAgent(AuditAgent):
    """動機評価エージェント (H-Agent)"""

    name = "HormeAgent"
    description = "動機の明確さを検証 — 「なぜこれを望むか」"

    # 動機・目的キーワード
    PURPOSE_KEYWORDS = [
        "目的",
        "理由",
        "なぜ",
        "ために",
        "purpose",
        "goal",
        "objective",
        "why",
        "because",
        "in order to",
    ]

    # 動機が不明確なパターン
    UNCLEAR_MOTIVATION_PATTERNS = [
        (r"\bとりあえず\b", "H-001", "「とりあえず」は動機が不明確"),
        (r"\b一応\b", "H-002", "「一応」は動機が弱い"),
        (r"\bなんとなく\b", "H-003", "「なんとなく」は動機が欠如"),
        (r"\bjust\s+(?:do|try|make)\b", "H-004", "目的なき行動"),
        (r"\bmaybe\s+we\s+should\b", "H-005", "動機が曖昧"),
    ]

    def audit(self, target: AuditTarget) -> AgentResult:
        """動機の明確さを監査"""
        issues: List[AuditIssue] = []
        content = target.content

        # 動機不明確パターンを検出
        issues.extend(self._check_unclear_motivation(content))

        # 計画には目的が必要
        if target.target_type == AuditTargetType.PLAN:
            issues.extend(self._check_purpose_presence(content))

        passed = not any(
            i.severity in (AuditSeverity.CRITICAL, AuditSeverity.HIGH) for i in issues
        )

        return AgentResult(
            agent_name=self.name,
            passed=passed,
            issues=issues,
            confidence=0.70,  # 動機判定は主観的
        )

    def _check_unclear_motivation(self, content: str) -> List[AuditIssue]:
        """動機が不明確なパターンを検出"""
        issues = []

        for pattern, code, message in self.UNCLEAR_MOTIVATION_PATTERNS:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code=code,
                        severity=AuditSeverity.LOW,
                        message=message,
                        location=f"position {match.start()}",
                        suggestion="明確な目的を述べてください",
                    )
                )

        return issues

    def _check_purpose_presence(self, content: str) -> List[AuditIssue]:
        """目的の存在を検出（計画向け）"""
        issues = []
        content_lower = content.lower()

        # 目的キーワードの存在チェック
        has_purpose = any(kw in content_lower for kw in self.PURPOSE_KEYWORDS)

        if not has_purpose:
            issues.append(
                AuditIssue(
                    agent=self.name,
                    code="H-010",
                    severity=AuditSeverity.MEDIUM,
                    message="計画に目的が明示されていません",
                    suggestion="「目的:」「なぜ:」などで動機を明記",
                )
            )

        return issues

    def supports(self, target_type: AuditTargetType) -> bool:
        """全タイプをサポート（特に計画に有効）"""
        return True
