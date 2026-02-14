# PROOF: [L1/算出] <- aristos/ WF 依存関係グラフの自動構築
"""
Aristos Graph Builder — WF 依存関係グラフの自動構築

.agent/workflows/*.md から WF 定義をパースし、
CCL マクロから WF 間の接続を抽出して有向グラフを構築する。

Usage:
    from aristos.graph_builder import WorkflowGraphBuilder
    builder = WorkflowGraphBuilder()
    graph = builder.build()
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .cost import CostCalculator, CostVector, Tier


# =============================================================================
# Types
# =============================================================================

@dataclass
class WFNode:
    """ワークフローノード"""
    name: str
    description: str = ""
    tier: str = ""      # omega, delta, tau, macro, special
    series: str = ""    # O, S, H, P, K, A, X, or ""
    ccl_expr: str = ""  # CCL マクロの場合、展開式
    cost: Optional[CostVector] = None
    dependencies: List[str] = field(default_factory=list)  # このWFが依存するWF

    @property
    def is_macro(self) -> bool:
        return self.name.startswith("ccl-")


@dataclass
class WFEdge:
    """ワークフロー間のエッジ"""
    source: str
    target: str
    relation: str = ""  # "requires", "contains", "triggers", "sequence"
    weight: float = 1.0

    def __repr__(self) -> str:
        return f"{self.source} --[{self.relation}]--> {self.target} (w={self.weight:.1f})"


@dataclass
class WFGraph:
    """ワークフロー依存関係グラフ"""
    nodes: Dict[str, WFNode] = field(default_factory=dict)
    edges: List[WFEdge] = field(default_factory=list)
    _adjacency: Dict[str, List[Tuple[str, float]]] = field(default_factory=dict)

    def add_node(self, node: WFNode) -> None:
        self.nodes[node.name] = node
        if node.name not in self._adjacency:
            self._adjacency[node.name] = []

    def add_edge(self, edge: WFEdge) -> None:
        self.edges.append(edge)
        if edge.source not in self._adjacency:
            self._adjacency[edge.source] = []
        self._adjacency[edge.source].append((edge.target, edge.weight))

    def neighbors(self, node: str) -> List[Tuple[str, float]]:
        """ノードの隣接ノードと重みを返す"""
        return self._adjacency.get(node, [])

    def reverse_neighbors(self, node: str) -> List[Tuple[str, float]]:
        """ノードへの逆方向エッジ (依存元) を返す"""
        result = []
        for edge in self.edges:
            if edge.target == node:
                result.append((edge.source, edge.weight))
        return result

    def node_count(self) -> int:
        return len(self.nodes)

    def edge_count(self) -> int:
        return len(self.edges)

    def summary(self) -> str:
        """グラフのサマリーを返す"""
        tiers = {}
        for node in self.nodes.values():
            tiers[node.tier] = tiers.get(node.tier, 0) + 1

        lines = [
            f"WorkflowGraph: {self.node_count()} nodes, {self.edge_count()} edges",
            "Tiers:",
        ]
        for tier, count in sorted(tiers.items()):
            lines.append(f"  {tier}: {count}")

        # Edge types
        edge_types = {}
        for edge in self.edges:
            edge_types[edge.relation] = edge_types.get(edge.relation, 0) + 1
        lines.append("Edge types:")
        for rel, count in sorted(edge_types.items()):
            lines.append(f"  {rel}: {count}")

        return "\n".join(lines)


# =============================================================================
# Series Mapping
# =============================================================================

# WF name → Series
SERIES_MAP = {
    # O-series
    "noe": "O", "bou": "O", "zet": "O", "ene": "O",
    "o": "O",
    # S-series
    "met": "S", "mek": "S", "sta": "S", "pra": "S",
    "s": "S",
    # H-series
    "pro": "H", "pis": "H", "ore": "H", "dox": "H",
    "h": "H",
    # P-series
    "kho": "P", "hod": "P", "tro": "P", "tek": "P",
    "p": "P",
    # K-series
    "euk": "K", "chr": "K", "tel": "K", "sop": "K",
    "k": "K",
    # A-series
    "pat": "A", "dia": "A", "gno": "A", "epi": "A",
    "a": "A",
    # X-series
    "x": "X",
    # Meta
    "ax": "AX",
}

# Ω-series 含有関係 (各 Peras は自 Series の4定理を統合)
OMEGA_CONTAINS = {
    "o": ["noe", "bou", "zet", "ene"],
    "s": ["met", "mek", "sta", "pra"],
    "h": ["pro", "pis", "ore", "dox"],
    "p": ["kho", "hod", "tro", "tek"],
    "k": ["euk", "chr", "tel", "sop"],
    "a": ["pat", "dia", "gno", "epi"],
}


# =============================================================================
# Builder
# =============================================================================

class WorkflowGraphBuilder:
    """WF 依存関係グラフの自動構築器"""

    def __init__(
        self,
        workflows_dir: Optional[Path] = None,
        cost_calculator: Optional[CostCalculator] = None,
    ):
        self._wf_dir = workflows_dir or Path(".agent/workflows")
        self._calc = cost_calculator or CostCalculator()

    def build(self, base_dir: Optional[Path] = None) -> WFGraph:
        """WF 依存関係グラフを構築"""
        graph = WFGraph()
        base = base_dir or Path(".")

        wf_dir = base / self._wf_dir
        if not wf_dir.exists():
            return graph

        # Phase 1: WF ノードの登録
        for md_file in sorted(wf_dir.glob("*.md")):
            wf_name = md_file.stem
            desc, ccl_expr = self._parse_workflow_file(md_file)
            tier = self._calc.classify_tier(wf_name)
            series = SERIES_MAP.get(wf_name, "")

            node = WFNode(
                name=wf_name,
                description=desc,
                tier=tier.value,
                series=series,
                ccl_expr=ccl_expr,
                cost=self._calc.calculate(wf_name, ccl_expr=ccl_expr),
            )
            graph.add_node(node)

        # Phase 2: 暗黙的依存関係 (Ω → Δ)
        for omega, deltas in OMEGA_CONTAINS.items():
            if omega in graph.nodes:
                for delta in deltas:
                    if delta in graph.nodes:
                        graph.add_edge(WFEdge(
                            source=omega,
                            target=delta,
                            relation="contains",
                            weight=0.5,  # 階層内は低コスト
                        ))

        # Phase 3: CCL マクロからの依存関係抽出
        for node in graph.nodes.values():
            if node.is_macro and node.ccl_expr:
                deps = self._extract_wf_references(node.ccl_expr)
                for dep in deps:
                    if dep in graph.nodes:
                        node.dependencies.append(dep)
                        cost = graph.nodes[dep].cost
                        graph.add_edge(WFEdge(
                            source=node.name,
                            target=dep,
                            relation="contains",
                            weight=cost.scalar() if cost else 1.0,
                        ))

        # Phase 4: 共通パターンからの暗黙的依存
        self._add_implicit_dependencies(graph)

        return graph

    def _parse_workflow_file(self, path: Path) -> Tuple[str, str]:
        """WF ファイルから description と CCL 式を抽出"""
        description = ""
        ccl_expr = ""

        try:
            text = path.read_text(encoding="utf-8")
            # YAML frontmatter から description を抽出
            if text.startswith("---"):
                parts = text.split("---", 2)
                if len(parts) >= 3:
                    fm = parts[1]
                    for line in fm.strip().split("\n"):
                        if line.startswith("description:"):
                            description = line.split(":", 1)[1].strip().strip('"')
                            # CCL マクロの場合、description に CCL 式が含まれる
                            ccl_match = re.search(r"—\s*(.+)$", description)
                            if ccl_match:
                                ccl_expr = ccl_match.group(1).strip()
                            break
        except (IOError, UnicodeDecodeError):
            pass

        return description, ccl_expr

    def _extract_wf_references(self, ccl_expr: str) -> List[str]:
        """CCL 式から WF 参照を抽出"""
        # /xxx パターンを検出 (演算子ではない)
        refs = re.findall(r'/([a-z][a-z0-9]*)', ccl_expr)
        # 重複除去しつつ順序保持
        seen = set()
        unique = []
        for r in refs:
            if r not in seen:
                seen.add(r)
                unique.append(r)
        return unique

    def _add_implicit_dependencies(self, graph: WFGraph) -> None:
        """共通パターンから暗黙的依存を追加"""
        # /boot → /bye (対称)
        if "boot" in graph.nodes and "bye" in graph.nodes:
            graph.add_edge(WFEdge(
                source="boot", target="bye",
                relation="symmetric", weight=0.1,
            ))
            graph.add_edge(WFEdge(
                source="bye", target="boot",
                relation="symmetric", weight=0.1,
            ))

        # /dia (Krisis) は多くの WF で使われる検証ステップ
        if "dia" in graph.nodes:
            for node in graph.nodes.values():
                if node.is_macro and "dia" in node.dependencies:
                    # 既にエッジがあるのでスキップ
                    pass

        # /dox (信念記録) は H-series の永続化
        # /pis (確信度) は H-series の評価
        # これらは多くのマクロで共通する終端パターン
        terminal_pattern = ["pis", "dox"]
        for tp in terminal_pattern:
            if tp in graph.nodes:
                for node in graph.nodes.values():
                    if node.is_macro and tp in node.dependencies:
                        # エッジの relation を "terminal" に更新可能
                        pass

        # X-series は Series 間を接続
        if "x" in graph.nodes:
            for omega in OMEGA_CONTAINS:
                if omega in graph.nodes:
                    graph.add_edge(WFEdge(
                        source="x", target=omega,
                        relation="cross-series", weight=1.0,
                    ))

        # /ax は全 Ω を統合
        if "ax" in graph.nodes:
            for omega in OMEGA_CONTAINS:
                if omega in graph.nodes:
                    graph.add_edge(WFEdge(
                        source="ax", target=omega,
                        relation="contains", weight=0.5,
                    ))
