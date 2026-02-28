# PROOF: [L1/定理] <- mekhane/synteleia/ A2 Krisis 監査基底クラス — 普遍的監査の抽象
"""
Audit Base Classes

すべての監査エージェントの基底クラスと共通型を定義。
A2 Krisis（判定力）の実装基盤。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# PURPOSE: 監査結果の重大度
class AuditSeverity(Enum):
    """監査結果の重大度"""

    CRITICAL = "critical"  # 致命的: 即座に対処必要
    HIGH = "high"  # 高: 重要な問題
    MEDIUM = "medium"  # 中: 注意が必要
    LOW = "low"  # 低: 改善推奨
    INFO = "info"  # 情報: 参考情報


# PURPOSE: 監査対象の種類
class AuditTargetType(Enum):
    """監査対象の種類"""

    CCL_OUTPUT = "ccl_output"  # CCL 実行出力
    CODE = "code"  # ソースコード
    THOUGHT = "thought"  # 思考ログ
    PLAN = "plan"  # 計画・設計
    PROOF = "proof"  # 存在証明
    GENERIC = "generic"  # 汎用


# PURPOSE: ソースコードの言語
class SourceLanguage(Enum):
    """ソースコードの言語 (source 拡張子から自動推定)"""

    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    RUST = "rust"
    GO = "go"
    UNKNOWN = "unknown"


_EXTENSION_MAP = {
    ".py": SourceLanguage.PYTHON,
    ".pyi": SourceLanguage.PYTHON,
    ".ts": SourceLanguage.TYPESCRIPT,
    ".tsx": SourceLanguage.TYPESCRIPT,
    ".js": SourceLanguage.JAVASCRIPT,
    ".jsx": SourceLanguage.JAVASCRIPT,
    ".mjs": SourceLanguage.JAVASCRIPT,
    ".rs": SourceLanguage.RUST,
    ".go": SourceLanguage.GO,
}


# PURPOSE: Audit target の実装
@dataclass
class AuditTarget:
    """監査対象"""

    content: str  # 監査対象のコンテンツ
    target_type: AuditTargetType = AuditTargetType.GENERIC
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None  # ファイルパスや識別子
    exclude_patterns: List[str] = field(default_factory=list)  # 除外 glob パターン
    _stripped_cache: Optional[str] = field(default=None, repr=False, compare=False)

    @property
    def stripped_content(self) -> str:
        """文字列リテラル・コメント除去済みコンテンツ。

        CODE ターゲットの場合は strip_strings_and_comments() を適用。
        それ以外は原文を返却。結果はキャッシュされる。
        """
        if self._stripped_cache is not None:
            return self._stripped_cache
        if self.target_type == AuditTargetType.CODE:
            from .pattern_loader import strip_strings_and_comments
            self._stripped_cache = strip_strings_and_comments(self.content)
        else:
            self._stripped_cache = self.content
        return self._stripped_cache

    @property
    def language(self) -> "SourceLanguage":
        """source 拡張子から言語を自動推定。"""
        if self.source:
            import os
            ext = os.path.splitext(self.source)[1].lower()
            return _EXTENSION_MAP.get(ext, SourceLanguage.UNKNOWN)
        return SourceLanguage.UNKNOWN


# PURPOSE: 監査で検出された問題
@dataclass
class AuditIssue:
    """監査で検出された問題"""

    agent: str  # 検出したエージェント名
    code: str  # 問題コード (e.g., "OP-001", "LOG-001")
    severity: AuditSeverity
    message: str
    location: Optional[str] = None  # 問題箇所
    suggestion: Optional[str] = None  # 改善提案


# PURPOSE: 単一エージェントの監査結果
@dataclass
class AgentResult:
    """単一エージェントの監査結果"""

    agent_name: str
    passed: bool
    issues: List[AuditIssue] = field(default_factory=list)
    confidence: float = 1.0  # 0.0-1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


# PURPOSE: 統合監査結果
@dataclass
class AuditResult:
    """統合監査結果"""

    target: AuditTarget
    agent_results: List[AgentResult] = field(default_factory=list)
    passed: bool = True
    summary: str = ""

    # PURPOSE: 全エージェントからの問題を集約
    @property
    def all_issues(self) -> List[AuditIssue]:
        """全エージェントからの問題を集約"""
        issues = []
        for ar in self.agent_results:
            issues.extend(ar.issues)
        return issues

    # PURPOSE: critical_count の処理
    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.all_issues if i.severity == AuditSeverity.CRITICAL)

    # PURPOSE: high_count の処理
    @property
    def high_count(self) -> int:
        return sum(1 for i in self.all_issues if i.severity == AuditSeverity.HIGH)


# PURPOSE: 監査エージェント基底クラス
class AuditAgent(ABC):
    """監査エージェント基底クラス"""

    name: str = "BaseAgent"
    description: str = "Base audit agent"

    # PURPOSE: 監査を実行する。
    @abstractmethod
    def audit(self, target: AuditTarget) -> AgentResult:
        """
        監査を実行する。

        Args:
            target: 監査対象

        Returns:
            AgentResult: 監査結果
        """
        pass

    # PURPOSE: このエージェントが対象タイプをサポートするか
    def supports(self, target_type: AuditTargetType) -> bool:
        """このエージェントが対象タイプをサポートするか"""
        return True  # デフォルトは全タイプをサポート
