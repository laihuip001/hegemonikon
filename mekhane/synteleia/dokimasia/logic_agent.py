# PROOF: [L1/定理] A2.ration 論理矛盾検出エージェント
"""
Logic Consistency Agent

論理的矛盾を検出する高速エージェント。
対立する主張、循環論法、自己参照矛盾を検出。

CCL: /dia-
"""

import re
from typing import List, Set, Tuple

from ..base import (
    AgentResult,
    AuditAgent,
    AuditIssue,
    AuditSeverity,
    AuditTarget,
    AuditTargetType,
)


class LogicAgent(AuditAgent):
    """論理矛盾検出エージェント"""

    name = "LogicAgent"
    description = "論理的矛盾を高速検出"

    # 対立キーワードペア
    CONTRADICTION_PAIRS = [
        ("必須", "任意"),
        ("常に", "決して"),
        ("全て", "一部"),
        ("must", "may"),
        ("always", "never"),
        ("required", "optional"),
        ("all", "none"),
        ("enable", "disable"),
        ("true", "false"),
    ]

    # 論理的に危険なパターン
    LOGIC_PATTERNS = [
        (r"\bif\s+True\b", "LOG-001", "if True は常に実行される無意味な条件"),
        (r"\bif\s+False\b", "LOG-002", "if False は決して実行されない"),
        (r"\bwhile\s+True\b.*\bbreak\b", None, None),  # OK パターン（breakあり）
        (r"\bwhile\s+True\b(?!.*\bbreak\b)", "LOG-003", "無限ループの可能性"),
        (r"\breturn\b.*\n.*\breturn\b", "LOG-004", "到達不能な return 文の可能性"),
    ]

    def audit(self, target: AuditTarget) -> AgentResult:
        """論理矛盾を監査"""
        issues: List[AuditIssue] = []

        content = target.content

        # 対立キーワードの共存検出
        issues.extend(self._check_contradictions(content))

        # 論理パターンチェック
        issues.extend(self._check_logic_patterns(content))

        # 自己否定チェック
        issues.extend(self._check_self_negation(content))

        passed = not any(
            i.severity in (AuditSeverity.CRITICAL, AuditSeverity.HIGH) for i in issues
        )

        return AgentResult(
            agent_name=self.name,
            passed=passed,
            issues=issues,
            confidence=0.80,
        )

    def _check_contradictions(self, content: str) -> List[AuditIssue]:
        """対立キーワードの共存を検出"""
        issues = []
        content_lower = content.lower()

        for word1, word2 in self.CONTRADICTION_PAIRS:
            if word1.lower() in content_lower and word2.lower() in content_lower:
                # 同じ段落内での共存をチェック
                paragraphs = content.split("\n\n")
                for i, para in enumerate(paragraphs):
                    para_lower = para.lower()
                    if word1.lower() in para_lower and word2.lower() in para_lower:
                        issues.append(
                            AuditIssue(
                                agent=self.name,
                                code="LOG-010",
                                severity=AuditSeverity.MEDIUM,
                                message=f"対立する概念が同一段落に共存: '{word1}' vs '{word2}'",
                                location=f"paragraph {i + 1}",
                                suggestion="意図的な対比か確認してください",
                            )
                        )

        return issues

    def _check_logic_patterns(self, content: str) -> List[AuditIssue]:
        """論理パターンをチェック"""
        issues = []

        for pattern, code, message in self.LOGIC_PATTERNS:
            if code is None:
                continue  # OK パターンはスキップ

            matches = list(re.finditer(pattern, content, re.MULTILINE | re.DOTALL))
            for match in matches:
                # while True + break は OK なのでスキップ
                if "while True" in pattern and "break" in content[match.start() : match.start() + 200]:
                    continue

                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code=code,
                        severity=AuditSeverity.MEDIUM,
                        message=message,
                        location=f"position {match.start()}",
                    )
                )

        return issues

    def _check_self_negation(self, content: str) -> List[AuditIssue]:
        """自己否定パターンを検出"""
        issues = []

        # "X is not X" パターン
        self_negation_pattern = r"\b(\w+)\s+is\s+not\s+\1\b"
        for match in re.finditer(self_negation_pattern, content):
            issues.append(
                AuditIssue(
                    agent=self.name,
                    code="LOG-020",
                    severity=AuditSeverity.HIGH,
                    message=f"自己否定: '{match.group(1)} is not {match.group(1)}'",
                    location=f"position {match.start()}",
                )
            )

        # "X != X" パターン
        self_neq_pattern = r"\b(\w+)\s*!=\s*\1\b"
        for match in re.finditer(self_neq_pattern, content):
            issues.append(
                AuditIssue(
                    agent=self.name,
                    code="LOG-021",
                    severity=AuditSeverity.HIGH,
                    message=f"自己不等: '{match.group(1)} != {match.group(1)}'",
                    location=f"position {match.start()}",
                )
            )

        return issues

    def supports(self, target_type: AuditTargetType) -> bool:
        """全タイプをサポート"""
        return True
