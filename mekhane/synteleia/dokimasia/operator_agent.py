# PROOF: [L1/定理] <- mekhane/synteleia/dokimasia/ A2.lex 演算子理解検証エージェント
"""
Operator Understanding Agent

記号・演算子が正しく使用されているかを検証する。
CCL 演算子、コード構文、論理記号の理解度を評価。

CCL: /dia.lex
"""

import re
from typing import Dict, List, Set

from ..base import (
    AgentResult,
    AuditAgent,
    AuditIssue,
    AuditSeverity,
    AuditTarget,
    AuditTargetType,
)


# PURPOSE: 演算子理解検証エージェント
class OperatorAgent(AuditAgent):
    """演算子理解検証エージェント"""

    name = "OperatorAgent"
    description = "記号・演算子が正しく使用されているかを検証"

    # CCL 演算子とその意味
    CCL_OPERATORS: Dict[str, str] = {
        "+": "深化 (deepening)",
        "-": "簡略化 (reduction)",
        "*": "拡張 (expansion)",
        "^": "メタ化 (meta)",
        "~": "振動 (oscillation)",
        ">>": "シーケンス (sequence)",
        "_": "暗黙連結 (implicit)",
        "!": "否定/警告 (negation)",
        "'": "変化追跡 (change tracking)",
        "∂": "偏微分/部分分析 (partial)",
        "√": "収束 (convergence)",
        "∫": "統合 (integration)",
        "Σ": "並列 (parallel)",
    }

    # よくある誤用パターン
    MISUSE_PATTERNS = [
        (r"/\w+\+\+", "OP-001", "++ は無効な演算子。+ を使用してください"),
        (r"/\w+--", "OP-002", "-- は無効な演算子。- を使用してください"),
        (r"\*\*\*", "OP-003", "*** は過剰なメタ化。** 以下を推奨"),
        (r"~~", "OP-004", "~~ は無効。振動は ~ 1つで表現"),
        (r"/\w+\s+/\w+", "OP-005", "ワークフロー間にスペース。>> または _ を使用"),
    ]

    # PURPOSE: 演算子理解を監査
    def audit(self, target: AuditTarget) -> AgentResult:
        """演算子理解を監査"""
        issues: List[AuditIssue] = []

        # CCL 出力の場合は演算子チェック
        if target.target_type == AuditTargetType.CCL_OUTPUT:
            issues.extend(self._check_ccl_operators(target.content))

        # コードの場合は構文チェック
        elif target.target_type == AuditTargetType.CODE:
            issues.extend(self._check_code_operators(target.content))

        # 汎用の場合は両方
        else:
            issues.extend(self._check_ccl_operators(target.content))
            issues.extend(self._check_code_operators(target.content))

        passed = not any(
            i.severity in (AuditSeverity.CRITICAL, AuditSeverity.HIGH) for i in issues
        )

        return AgentResult(
            agent_name=self.name,
            passed=passed,
            issues=issues,
            confidence=0.85,
        )

    # PURPOSE: [L2-auto] CCL 演算子の使用をチェック
    def _check_ccl_operators(self, content: str) -> List[AuditIssue]:
        """CCL 演算子の使用をチェック"""
        issues = []

        # 誤用パターンを検出
        for pattern, code, message in self.MISUSE_PATTERNS:
            matches = re.finditer(pattern, content)
            for match in matches:
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code=code,
                        severity=AuditSeverity.MEDIUM,
                        message=message,
                        location=f"position {match.start()}",
                    )
                )

        # 未知の演算子組み合わせを検出
        ccl_expr_pattern = r"/\w+([+\-*^~'∂√∫Σ!_]|\>\>)+"
        for match in re.finditer(ccl_expr_pattern, content):
            expr = match.group(0)
            # 複雑すぎる式を警告
            operator_count = sum(1 for c in expr if c in "+,-*^~'∂√∫Σ!")
            if operator_count > 5:
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code="OP-010",
                        severity=AuditSeverity.LOW,
                        message=f"複雑な CCL 式 ({operator_count} 演算子): 分割を検討",
                        location=expr,
                    )
                )

        return issues

    # PURPOSE: [L2-auto] コード内の演算子使用をチェック
    def _check_code_operators(self, content: str) -> List[AuditIssue]:
        """コード内の演算子使用をチェック"""
        issues = []

        # 冗長な演算子パターン
        style_patterns = [
            (r"==\s*True\b", "OP-020", "== True は冗長。直接 if x: を使用", AuditSeverity.LOW),
            (r"==\s*False\b", "OP-021", "== False は冗長。if not x: を使用", AuditSeverity.LOW),
            (r"!=\s*None\b", "OP-022", "!= None より is not None を推奨", AuditSeverity.LOW),
            (r"==\s*None\b", "OP-023", "== None より is None を推奨", AuditSeverity.LOW),
        ]

        for pattern, code, message, severity in style_patterns:
            for match in re.finditer(pattern, content):
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code=code,
                        severity=severity,
                        message=message,
                        location=f"position {match.start()}",
                    )
                )

        # セキュリティ危険パターン (HIGH/CRITICAL)
        security_patterns = [
            (r"\beval\s*\(", "SEC-001", "eval() は任意コード実行の脆弱性。ast.literal_eval() を検討", AuditSeverity.CRITICAL),
            (r"\bexec\s*\(", "SEC-002", "exec() は任意コード実行の脆弱性", AuditSeverity.CRITICAL),
            (r"\bos\.system\s*\(", "SEC-003", "os.system() は OS コマンドインジェクションの危険。subprocess.run() を推奨", AuditSeverity.HIGH),
            (r"\bsubprocess\.\w+\(.*shell\s*=\s*True", "SEC-004", "shell=True はコマンドインジェクションの危険", AuditSeverity.HIGH),
            (r"\b__import__\s*\(", "SEC-005", "__import__() は動的インポートの脆弱性。importlib を検討", AuditSeverity.MEDIUM),
            (r"\bpickle\.loads?\s*\(", "SEC-006", "pickle は任意コード実行の脆弱性。信頼できないデータに使用禁止", AuditSeverity.HIGH),
            (r"\byaml\.load\s*\((?!.*Loader\s*=)", "SEC-007", "yaml.load() は unsafe。yaml.safe_load() を使用", AuditSeverity.HIGH),
            (r"\binput\s*\(.*\)", "SEC-008", "input() はサーバーサイドでは危険。Web フレームワーク経由を推奨", AuditSeverity.LOW),
        ]

        for pattern, code, message, severity in security_patterns:
            for match in re.finditer(pattern, content, re.DOTALL):
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code=code,
                        severity=severity,
                        message=message,
                        location=f"position {match.start()}",
                        suggestion="セキュリティレビューを実施してください",
                    )
                )

        return issues

    # PURPOSE: CCL出力とコードをサポート
    def supports(self, target_type: AuditTargetType) -> bool:
        """CCL出力とコードをサポート"""
        return target_type in (
            AuditTargetType.CCL_OUTPUT,
            AuditTargetType.CODE,
            AuditTargetType.GENERIC,
        )
