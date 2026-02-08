# PROOF: [L1/定理] <- mekhane/synteleia/poiesis/ S2 Mekhanē 構造設計エージェント
"""
Schema Agent - Structure Evaluation

「どう構造化するか」を問う構造評価エージェント。
構造の歪み、設計の不備を検出。

CCL: /s (S-series)
FEP: 世界モデルの構造化
"""

import re
from typing import List, Dict

from ..base import (
    AgentResult,
    AuditAgent,
    AuditIssue,
    AuditSeverity,
    AuditTarget,
    AuditTargetType,
)


# PURPOSE: 構造設計エージェント (S-Agent)
class SchemaAgent(AuditAgent):
    """構造設計エージェント (S-Agent)"""

    name = "SchemaAgent"
    description = "構造の妥当性を検証 — 「どう組むか」"

    # 構造的問題パターン
    STRUCTURE_PROBLEMS = [
        (r"(?:^|\n)#{1,6}\s+.+\n(?:^|\n)#{1,6}\s+.+\n(?:^|\n)#{1,6}\s+", 
         "S-001", "見出しが連続 — 本文が欠落している可能性"),
        (r"\n{4,}", "S-002", "過剰な空行 — 構造を見直してください"),
        (r"(?:^|\n)-\s+.{200,}", "S-003", "リスト項目が長すぎる — 分割を検討"),
    ]

    # 階層構造の問題
    HIERARCHY_PROBLEMS = [
        (r"(?:^|\n)###\s+(?!.*\n##\s+)", "S-010", "h3 が h2 なしに出現"),
        (r"(?:^|\n)####\s+(?!.*\n###\s+)", "S-011", "h4 が h3 なしに出現"),
    ]

    # PURPOSE: 構造の妥当性を監査
    def audit(self, target: AuditTarget) -> AgentResult:
        """構造の妥当性を監査"""
        issues: List[AuditIssue] = []
        content = target.content

        # 構造的問題を検出
        issues.extend(self._check_structure_problems(content))

        # マークダウンの階層をチェック
        if target.target_type in (AuditTargetType.PLAN, AuditTargetType.GENERIC):
            issues.extend(self._check_markdown_hierarchy(content))

        # コードの構造をチェック
        if target.target_type == AuditTargetType.CODE:
            issues.extend(self._check_code_structure(content))

        passed = not any(
            i.severity in (AuditSeverity.CRITICAL, AuditSeverity.HIGH) for i in issues
        )

        return AgentResult(
            agent_name=self.name,
            passed=passed,
            issues=issues,
            confidence=0.80,
        )

    def _check_structure_problems(self, content: str) -> List[AuditIssue]:
        """構造的問題を検出"""
        issues = []

        for pattern, code, message in self.STRUCTURE_PROBLEMS:
            for match in re.finditer(pattern, content, re.MULTILINE):
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code=code,
                        severity=AuditSeverity.LOW,
                        message=message,
                        location=f"position {match.start()}",
                    )
                )

        return issues

    def _check_markdown_hierarchy(self, content: str) -> List[AuditIssue]:
        """マークダウンの階層構造をチェック"""
        issues = []
        lines = content.split("\n")
        
        current_level = 0
        for i, line in enumerate(lines):
            header_match = re.match(r"^(#{1,6})\s+", line)
            if header_match:
                level = len(header_match.group(1))
                # 階層が2以上飛んでいないか
                if current_level > 0 and level > current_level + 1:
                    issues.append(
                        AuditIssue(
                            agent=self.name,
                            code="S-020",
                            severity=AuditSeverity.MEDIUM,
                            message=f"見出し階層が飛躍: h{current_level} → h{level}",
                            location=f"line {i + 1}",
                            suggestion=f"h{current_level + 1} を追加",
                        )
                    )
                current_level = level

        return issues

    def _check_code_structure(self, content: str) -> List[AuditIssue]:
        """コードの構造をチェック"""
        issues = []

        # 関数が長すぎる（100行以上）
        func_pattern = r"def\s+\w+\([^)]*\):[^\n]*\n((?:[ \t]+[^\n]*\n)*)"
        for match in re.finditer(func_pattern, content):
            func_body = match.group(1)
            line_count = func_body.count("\n")
            if line_count > 100:
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code="S-030",
                        severity=AuditSeverity.MEDIUM,
                        message=f"関数が長すぎる: {line_count}行",
                        location=f"position {match.start()}",
                        suggestion="関数を分割してください",
                    )
                )

        return issues

    # PURPOSE: 全タイプをサポート
    def supports(self, target_type: AuditTargetType) -> bool:
        """全タイプをサポート"""
        return True
