# PROOF: [L2/パッケージ] <- .agent/projects/aristos/
# Aristos — WF ルーティング最適化 + 進化基盤
"""
Aristos: ワークフロールーティング最適化 & 進化エンジン

L1: WF 依存関係グラフの構築、最適経路探索、コスト分析
L2: 遺伝的アルゴリズムによる派生選択の進化基盤
"""

from .cost import CostCalculator, CostVector, Depth, Tier
from .graph_builder import WorkflowGraphBuilder, WFGraph, WFNode, WFEdge
from .router import WorkflowRouter, Route, MacroAnalysis, RouteSuggestion
from .evolve import (
    Chromosome,
    EvolutionEngine,
    FeedbackCollector,
    FeedbackEntry,
    FitnessVector,
    Scale,
)

__all__ = [
    # L1: Graph & Routing
    "CostCalculator",
    "CostVector",
    "Depth",
    "Tier",
    "WorkflowGraphBuilder",
    "WFGraph",
    "WFNode",
    "WFEdge",
    "WorkflowRouter",
    "Route",
    "MacroAnalysis",
    "RouteSuggestion",
    # L2: Evolution Engine
    "Chromosome",
    "EvolutionEngine",
    "FeedbackCollector",
    "FeedbackEntry",
    "FitnessVector",
    "Scale",
]
