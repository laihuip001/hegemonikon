# PROOF: [L1/定理] <- mekhane/synteleia/dokimasia/ A2.epo 完全性検証エージェント
"""
Completeness Agent

欠落要素を検出する「判断停止」エージェント。
必須要素の欠如、空の実装、未完了マーカーを検出。

CCL: /dia.epo
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Set

from ..base import (
    AgentResult,
    AuditAgent,
    AuditIssue,
    AuditSeverity,
    AuditTarget,
    AuditTargetType,
    SourceLanguage,
)
from ..pattern_loader import (
    load_patterns, parse_pattern_list,
)

_PATTERNS_YAML = Path(__file__).parent / "patterns.yaml"

_TARGET_TYPE_MAP = {
    "ccl_output": AuditTargetType.CCL_OUTPUT,
    "plan": AuditTargetType.PLAN,
    "proof": AuditTargetType.PROOF,
    "code": AuditTargetType.CODE,
    "generic": AuditTargetType.GENERIC,
}


# PURPOSE: 完全性検証エージェント
class CompletenessAgent(AuditAgent):
    """完全性検証エージェント"""

    name = "CompletenessAgent"
    description = "欠落要素を検出（判断停止モード）"

    # Fallback values
    _FALLBACK_REQUIRED: Dict[AuditTargetType, List[str]] = {
        AuditTargetType.CCL_OUTPUT: ["結論", "conclusion", "summary", "result"],
        AuditTargetType.PLAN: ["目的", "goal", "objective", "ステップ", "step", "action"],
        AuditTargetType.PROOF: ["PROOF:", "理由", "reason", "why"],
    }

    _FALLBACK_INCOMPLETE = [
        (r"\bTODO\b", "COMP-001", "TODO マーカーが残っています"),
        (r"\bFIXME\b", "COMP-002", "FIXME マーカーが残っています"),
        (r"\bXXX\b", "COMP-003", "XXX マーカーが残っています"),
        (r"\bHACK\b", "COMP-004", "HACK マーカーが残っています"),
        (r"\.\.\.(?!\s*\]|\s*\)|\s*\w)", "COMP-005", "省略記号 ... が残っています"),
        (r"(?<!@abstractmethod\n)\s+pass\s*$", "COMP-006", "空の pass 文があります"),
        (r'raise\s+NotImplementedError', "COMP-007", "NotImplementedError が残っています"),
        (r"\?\?\?", "COMP-008", "??? プレースホルダーが残っています"),
    ]

    _FALLBACK_EMPTY = [
        (r"def\s+\w+\([^)]*\):\s*\n\s*pass\s*$", "COMP-010", "空の関数定義"),
        (r"class\s+\w+[^:]*:\s*\n\s*pass\s*$", "COMP-011", "空のクラス定義"),
        (r"if\s+[^:]+:\s*\n\s*pass\s*$", "COMP-012", "空の if ブロック"),
        (r"try:\s*\n\s*pass\s*$", "COMP-013", "空の try ブロック"),
        (r"except[^:]*:\s*\n\s*pass\s*$", "COMP-014", "空の except ブロック"),
    ]

    def __init__(self):
        loaded = load_patterns(_PATTERNS_YAML, "completeness")
        self.INCOMPLETE_MARKERS = parse_pattern_list(
            loaded.get("incomplete_markers"), self._FALLBACK_INCOMPLETE
        )
        self.EMPTY_PATTERNS = parse_pattern_list(
            loaded.get("empty_patterns"), self._FALLBACK_EMPTY
        )
        self.REQUIRED_ELEMENTS = self._parse_required_elements(
            loaded.get("required_elements"), self._FALLBACK_REQUIRED
        )

    @staticmethod
    def _parse_required_elements(
        raw: Any, default: Dict[AuditTargetType, List[str]]
    ) -> Dict[AuditTargetType, List[str]]:
        """YAML の required_elements を Dict[AuditTargetType, List[str]] に変換。"""
        if not isinstance(raw, dict):
            return default
        result: Dict[AuditTargetType, List[str]] = {}
        for key, values in raw.items():
            target_type = _TARGET_TYPE_MAP.get(str(key))
            if target_type and isinstance(values, list):
                result[target_type] = [str(v) for v in values]
        return result or default

    # PURPOSE: 完全性を監査
    def audit(self, target: AuditTarget) -> AgentResult:
        """完全性を監査"""
        issues: List[AuditIssue] = []

        content = target.content
        stripped = target.stripped_content
        is_diff = self._is_diff_content(content)

        # diff 入力の場合、追加行のみに正規化
        normalized = self._normalize_diff_content(content) if is_diff else content
        normalized_stripped = self._normalize_diff_content(stripped) if is_diff else stripped

        # 未完了マーカー検出 (stripped で文字列/コメント内のマーカー除外)
        issues.extend(self._check_incomplete_markers(normalized_stripped))

        # 空のブロック検出 (stripped で文字列/コメント内のパターン除外)
        issues.extend(self._check_empty_blocks(normalized_stripped))

        # タイプ固有の必須要素チェック (全文を使う)
        issues.extend(self._check_required_elements(content, target.target_type))

        # 構造的完全性チェック (stripped で括弧バランスが正確)
        issues.extend(self._check_structural_completeness(normalized_stripped, target.target_type))

        # 言語固有チェック
        if target.target_type == AuditTargetType.CODE:
            issues.extend(self._check_language_specific(normalized_stripped, target))

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

        # content はすでに stripped_content 経由で文字列/コメント除去済み

        # 括弧のバランスチェック (差分ベースの severity 段階化)
        brackets = [("(", ")"), ("[", "]"), ("{", "}")]
        for open_b, close_b in brackets:
            open_count = content.count(open_b)
            close_count = content.count(close_b)
            diff = abs(open_count - close_count)
            if diff == 0:
                continue

            # 差の大きさに応じて severity を段階化
            if diff >= 4:
                severity = AuditSeverity.HIGH
            elif diff >= 2:
                severity = AuditSeverity.MEDIUM
            else:
                # ±1 は strip 残留や言語固有構文の可能性が高い
                severity = AuditSeverity.LOW

            issues.append(
                AuditIssue(
                    agent=self.name,
                    code="COMP-030",
                    severity=severity,
                    message=f"括弧のバランスが不正: '{open_b}' = {open_count}, '{close_b}' = {close_count} (差: {diff})",
                )
            )

        return issues

    # PURPOSE: 言語固有の品質チェック
    def _check_language_specific(
        self, content: str, target: AuditTarget
    ) -> List[AuditIssue]:
        """言語に基づく固有チェック"""
        issues = []
        lang = target.language

        if lang == SourceLanguage.PYTHON:
            # NotImplementedError が残っている = 未実装
            for m in re.finditer(r'raise\s+NotImplementedError', content):
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code="COMP-040",
                        severity=AuditSeverity.MEDIUM,
                        message="NotImplementedError — 未実装のメソッドが残っています",
                        location=f"position {m.start()}",
                    )
                )

        elif lang in (SourceLanguage.TYPESCRIPT, SourceLanguage.JAVASCRIPT):
            # == / != (非厳密等価) → === / !== を推奨
            for m in re.finditer(r'(?<!=)(?<!!)==(?!=)', content):
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code="COMP-041",
                        severity=AuditSeverity.LOW,
                        message="非厳密等価 (==) — === の使用を推奨",
                        location=f"position {m.start()}",
                        suggestion="=== を使用してください",
                    )
                )

        elif lang == SourceLanguage.RUST:
            # .unwrap() / .expect() は panic 源
            for m in re.finditer(r'\.(unwrap|expect)\s*\(', content):
                issues.append(
                    AuditIssue(
                        agent=self.name,
                        code="COMP-042",
                        severity=AuditSeverity.LOW,
                        message=f".{m.group(1)}() — panic の原因になる可能性",
                        location=f"position {m.start()}",
                        suggestion="? 演算子または match での処理を検討",
                    )
                )

        return issues

    # PURPOSE: 全タイプをサポート
    def supports(self, target_type: AuditTargetType) -> bool:
        """全タイプをサポート"""
        return True

