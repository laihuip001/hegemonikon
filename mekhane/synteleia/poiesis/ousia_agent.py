# PROOF: [L1/定理] O1 Noēsis 本質洞察エージェント
"""
Ousia Agent - Essence Recognition

「これは何か」を問う本質洞察エージェント。
定義の曖昧さ、本質の不明確さを検出。

CCL: /o (O-series)
FEP: 世界モデルの構築・認識
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


class OusiaAgent(AuditAgent):
    """本質洞察エージェント (O-Agent)"""

    name = "OusiaAgent"
    description = "本質の明確さを検証 — 「これは何か」"

    # 本質が不明確なパターン
    VAGUE_PATTERNS = [
        (r"\bこれ\b(?!は)", "O-001", "「これ」の指示対象が不明確"),
        (r"\bそれ\b(?!は)", "O-002", "「それ」の指示対象が不明確"),
        (r"\bあれ\b", "O-003", "「あれ」の指示対象が不明確"),
        (r"\b(?:something|anything|nothing)\b", "O-004", "不定代名詞の使用"),
        (r"\betc\.?\b", "O-005", "etc. は本質を曖昧にする"),
        (r"\.\.\.(?!\s*\])", "O-006", "省略記号は本質を隠す"),
    ]

    # 定義の欠如パターン
    UNDEFINED_PATTERNS = [
        (r"\b\w+\s+(?:とは|is|means)\b", None, None),  # 定義あり = OK
        (r"def\s+\w+\([^)]*\):", None, None),  # 関数定義あり = OK
        (r"class\s+\w+[^:]*:", None, None),  # クラス定義あり = OK
    ]

    def audit(self, target: AuditTarget) -> AgentResult:
        """本質の明確さを監査"""
        issues: List[AuditIssue] = []
        content = target.content

        # 曖昧な指示を検出
        issues.extend(self._check_vague_references(content))

        # 概念の定義有無を検出（計画・思考ログ向け）
        if target.target_type in (AuditTargetType.PLAN, AuditTargetType.THOUGHT):
            issues.extend(self._check_concept_definition(content))

        passed = not any(
            i.severity in (AuditSeverity.CRITICAL, AuditSeverity.HIGH) for i in issues
        )

        return AgentResult(
            agent_name=self.name,
            passed=passed,
            issues=issues,
            confidence=0.75,  # 本質判定は主観的要素が大きい
        )

    def _check_vague_references(self, content: str) -> List[AuditIssue]:
        """曖昧な参照を検出"""
        issues = []

        for pattern, code, message in self.VAGUE_PATTERNS:
            if code is None:
                continue
            for match in re.finditer(pattern, content, re.IGNORECASE):
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code=code,
                        severity=AuditSeverity.LOW,
                        message=message,
                        location=f"position {match.start()}",
                        suggestion="具体的な名称に置き換えてください",
                    )
                )

        return issues

    def _check_concept_definition(self, content: str) -> List[AuditIssue]:
        """概念の定義有無を検出"""
        issues = []

        # 大文字で始まる専門用語を抽出
        technical_terms = set(re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b", content))

        # 各用語に定義があるかチェック
        for term in technical_terms:
            definition_pattern = rf"\b{term}\s+(?:とは|is|means|=)"
            if not re.search(definition_pattern, content, re.IGNORECASE):
                # 定義がない場合は INFO レベルで報告
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code="O-010",
                        severity=AuditSeverity.INFO,
                        message=f"用語 '{term}' の定義が見つかりません",
                        suggestion=f"'{term} とは...' の形式で定義を追加",
                    )
                )

        return issues

    def supports(self, target_type: AuditTargetType) -> bool:
        """全タイプをサポート（特に計画・思考ログに有効）"""
        return True
