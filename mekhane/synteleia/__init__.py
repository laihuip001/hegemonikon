# PROOF: [L2/インフラ] <- mekhane/synteleia/ Synteleia メタ認知・社会的認知 実装層
"""
Synteleia (συντέλεια) — メタ認知・社会的認知の実装層

Hegemonikón の6カテゴリを2層構造で実装:
- Poiēsis (生成層): O, S, H — 何を・どう・なぜ
- Dokimasia (審査層): P, K, A — 範囲・時期・精度

実行モード:
- 内積 (·): 両層を独立実行し統合
- 外積 (×): 3×3 交差検証
"""

# Base classes
from .base import (
    AuditSeverity,
    AuditTargetType,
    AuditTarget,
    AuditIssue,
    AgentResult,
    AuditResult,
    AuditAgent,
)

# Orchestrator
from .orchestrator import SynteleiaOrchestrator

# 互換性のためのエイリアス
AuditOrchestrator = SynteleiaOrchestrator

# Poiēsis (生成層)
from .poiesis import OusiaAgent, SchemaAgent, HormeAgent

# Dokimasia (審査層)
from .dokimasia import (
    PerigrapheAgent,
    KairosAgent,
    OperatorAgent,
    LogicAgent,
    CompletenessAgent,
    SemanticAgent,
)

__all__ = [
    # Base
    "AuditSeverity",
    "AuditTargetType",
    "AuditTarget",
    "AuditIssue",
    "AgentResult",
    "AuditResult",
    "AuditAgent",
    # Orchestrator
    "AuditOrchestrator",
    # Poiēsis
    "OusiaAgent",
    "SchemaAgent",
    "HormeAgent",
    # Dokimasia
    "PerigrapheAgent",
    "KairosAgent",
    "OperatorAgent",
    "LogicAgent",
    "CompletenessAgent",
    # L2
    "SemanticAgent",
]
