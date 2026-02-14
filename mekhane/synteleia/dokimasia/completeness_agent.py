# PROOF: [L1/定理] <- mekhane/synteleia/dokimasia/ A2.epo 完全性検証エージェント
"""
Completeness Agent

欠落要素を検出する「判断停止」エージェント。
必須要素の欠如、空の実装、未完了マーカーを検出。

CCL: /dia.epo
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


# PURPOSE: 完全性検証エージェント
class CompletenessAgent(AuditAgent):
    """完全性検証エージェント"""

    name = "CompletenessAgent"
    description = "欠落要素を検出（判断停止モード）"

    # ターゲットタイプごとの必須要素
    REQUIRED_ELEMENTS: Dict[AuditTargetType, List[str]] = {
        AuditTargetType.CCL_OUTPUT: [
            "結論",
            "conclusion",
            "summary",
            "result",
        ],
        AuditTargetType.PLAN: [
            "目的",
            "goal",
            "objective",
            "ステップ",
            "step",
            "action",
        ],
        AuditTargetType.PROOF: [
            "PROOF:",
            "理由",
            "reason",
            "why",
        ],
    }

    # 未完了マーカー
    INCOMPLETE_MARKERS = [
        (r"\bTODO\b", "COMP-001", "TODO マーカーが残っています"),
        (r"\bFIXME\b", "COMP-002", "FIXME マーカーが残っています"),
        (r"\bXXX\b", "COMP-003", "XXX マーカーが残っています"),
        (r"\bHACK\b", "COMP-004", "HACK マーカーが残っています"),
        (r"\.\.\.(?!\s*\]|\s*\))", "COMP-005", "省略記号 ... が残っています"),
        (r"\bpass\s*$", "COMP-006", "空の pass 文があります"),
        (r'raise\s+NotImplementedError', "COMP-007", "NotImplementedError が残っています"),
        (r"\?\?\?", "COMP-008", "??? プレースホルダーが残っています"),
    ]

    # 空のブロックパターン
    EMPTY_PATTERNS = [
        (r"def\s+\w+\([^)]*\):\s*\n\s*pass\s*$", "COMP-010", "空の関数定義"),
        (r"class\s+\w+[^:]*:\s*\n\s*pass\s*$", "COMP-011", "空のクラス定義"),
        (r"if\s+[^:]+:\s*\n\s*pass\s*$", "COMP-012", "空の if ブロック"),
        (r"try:\s*\n\s*pass\s*$", "COMP-013", "空の try ブロック"),
        (r"except[^:]*:\s*\n\s*pass\s*$", "COMP-014", "空の except ブロック"),
    ]

    # PURPOSE: 完全性を監査
    def audit(self, target: AuditTarget) -> AgentResult:
        """完全性を監査"""
        issues: List[AuditIssue] = []

        content = target.content
        is_diff = self._is_diff_content(content)

        # diff 入力の場合、追加行のみに正規化
        normalized = self._normalize_diff_content(content) if is_diff else content

        # 未完了マーカー検出 (diff の場合は追加行のみ)
        issues.extend(self._check_incomplete_markers(normalized))

        # 空のブロック検出 (diff の場合は追加行のみ)
        issues.extend(self._check_empty_blocks(normalized))

        # タイプ固有の必須要素チェック (全文を使う)
        issues.extend(self._check_required_elements(content, target.target_type))

        # 構造的完全性チェック (diff の場合は追加行のみ)
        issues.extend(self._check_structural_completeness(normalized, target.target_type))

        passed = not any(
            i.severity in (AuditSeverity.CRITICAL, AuditSeverity.HIGH) for i in issues
        )

        return AgentResult(
            agent_name=self.name,
            passed=passed,
            issues=issues,
            confidence=0.90,
        )

    # PURPOSE: diff 形式のコンテンツかどうかを判定
    @staticmethod
    def _is_diff_content(content: str) -> bool:
        """diff 形式のコンテンツかどうかを判定

        unified diff の特徴的なパターンを検出:
        - `+++ ` / `--- ` ヘッダー行
        - `@@ ... @@` ハンクヘッダー
        - `+` / `-` で始まる変更行の割合
        """
        lines = content.split("\n")
        if len(lines) < 3:
            return False

        # unified diff ヘッダー検出
        has_diff_header = any(
            line.startswith("--- ") or line.startswith("+++ ") or line.startswith("@@ ")
            for line in lines[:20]
        )
        if has_diff_header:
            return True

        # +/- 行の割合で判定 (50% 以上なら diff)
        diff_lines = sum(1 for line in lines if line.startswith("+") or line.startswith("-"))
        return len(lines) > 5 and diff_lines / len(lines) > 0.5

    # PURPOSE: diff コンテンツから追加行のみを抽出して正規化
    @staticmethod
    def _normalize_diff_content(content: str) -> str:
        """diff コンテンツから追加行 (+) とコンテキスト行のみを抽出

        削除行 (-) を除外することで、括弧バランスチェック等の
        偽陽性を防ぐ。
        """
        normalized_lines = []
        for line in content.split("\n"):
            # diff メタ行をスキップ
            if line.startswith("--- ") or line.startswith("+++ ") or line.startswith("@@ "):
                continue
            # 削除行をスキップ
            if line.startswith("-"):
                continue
            # 追加行は + プレフィックスを除去
            if line.startswith("+"):
                normalized_lines.append(line[1:])
            else:
                # コンテキスト行はそのまま
                normalized_lines.append(line)
        return "\n".join(normalized_lines)

    # PURPOSE: [L2-auto] 未完了マーカーを検出
    def _check_incomplete_markers(self, content: str) -> List[AuditIssue]:
        """未完了マーカーを検出"""
        issues = []

        for pattern, code, message in self.INCOMPLETE_MARKERS:
            for match in re.finditer(pattern, content, re.MULTILINE):
                # コメント内の TODO/FIXME の重大度を調整
                line_start = content.rfind("\n", 0, match.start()) + 1
                line = content[line_start : content.find("\n", match.start())]

                severity = AuditSeverity.LOW
                if "#" not in line[:match.start() - line_start]:
                    # コメント外なら重大度を上げる
                    severity = AuditSeverity.MEDIUM

                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code=code,
                        severity=severity,
                        message=message,
                        location=f"position {match.start()}",
                    )
                )

        return issues

    # PURPOSE: [L2-auto] 空のブロックを検出
    def _check_empty_blocks(self, content: str) -> List[AuditIssue]:
        """空のブロックを検出"""
        issues = []

        for pattern, code, message in self.EMPTY_PATTERNS:
            for match in re.finditer(pattern, content, re.MULTILINE):
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code=code,
                        severity=AuditSeverity.MEDIUM,
                        message=message,
                        location=f"position {match.start()}",
                        suggestion="実装を追加するか、意図的な場合はコメントを追加",
                    )
                )

        return issues

    # PURPOSE: [L2-auto] 必須要素の存在をチェック
    def _check_required_elements(
        self, content: str, target_type: AuditTargetType
    ) -> List[AuditIssue]:
        """必須要素の存在をチェック"""
        issues = []

        required = self.REQUIRED_ELEMENTS.get(target_type, [])
        if not required:
            return issues

        content_lower = content.lower()
        found_any = any(elem.lower() in content_lower for elem in required)

        if not found_any:
            issues.append(
                AuditIssue(
                    agent=self.name,
                    code="COMP-020",
                    severity=AuditSeverity.HIGH,
                    message=f"必須要素が見つかりません: {required[:3]}",
                    suggestion=f"以下のいずれかを追加: {', '.join(required[:3])}",
                )
            )

        return issues

    # PURPOSE: [L2-auto] 構造的完全性をチェック
    def _check_structural_completeness(
        self, content: str, target_type: AuditTargetType
    ) -> List[AuditIssue]:
        """構造的完全性をチェック"""
        issues = []

        # 括弧のバランスチェック
        brackets = [("(", ")"), ("[", "]"), ("{", "}")]
        for open_b, close_b in brackets:
            open_count = content.count(open_b)
            close_count = content.count(close_b)
            if open_count != close_count:
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code="COMP-030",
                        severity=AuditSeverity.HIGH,
                        message=f"括弧のバランスが不正: '{open_b}' = {open_count}, '{close_b}' = {close_count}",
                    )
                )

        return issues

    # PURPOSE: 全タイプをサポート
    def supports(self, target_type: AuditTargetType) -> bool:
        """全タイプをサポート"""
        return True

