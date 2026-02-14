# PROOF: [L1/算出] <- aristos/ WF ルーティングエンジン
"""
Aristos Router — WF 間の最適経路探索

Dijkstra アルゴリズムをベースに、WF 依存関係グラフ上で
最適な実行経路を探索する。

Usage:
    from aristos.router import WorkflowRouter
    router = WorkflowRouter()
    route = router.find_shortest_path("noe", "ene")
"""

import copy
import heapq
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from .cost import CostCalculator, CostVector
from .graph_builder import WFGraph, WFNode, WFEdge, WorkflowGraphBuilder


# =============================================================================
# Types
# =============================================================================

@dataclass
class Route:
    """探索結果の経路"""
    path: List[str]           # WF 名の順序列
    total_cost: float = 0.0   # 合計スカラーコスト
    segments: List[Tuple[str, str, float]] = field(default_factory=list)
    reachable: bool = True
    heuristic: str = ""       # ヒューリスティクス名 (shortest/fastest/deepest)
    time_min: float = 0.0     # 推定合計時間 (分)
    max_depth: float = 0.0    # 最大認知深度

    def __repr__(self) -> str:
        if not self.reachable:
            return f"Route(unreachable)"
        arrow = " → ".join(self.path)
        return f"Route({arrow}, cost={self.total_cost:.2f})"

    def detail(self) -> str:
        """詳細な経路情報"""
        if not self.reachable:
            return "到達不能: 経路が存在しません"
        lines = [f"経路: {' → '.join(self.path)}"]
        lines.append(f"合計コスト: {self.total_cost:.2f}")
        if self.segments:
            lines.append("セグメント:")
            for src, tgt, w in self.segments:
                lines.append(f"  {src} → {tgt} (cost={w:.2f})")
        return "\n".join(lines)


@dataclass
class RouteSuggestion:
    """ヒューリスティクス提案セット — 射の提案への統合用"""
    goal: str
    source: str
    shortest: Optional[Route] = None   # ステップ数最少
    fastest: Optional[Route] = None    # 時間最少
    deepest: Optional[Route] = None    # 認知深度最大
    context: str = ""                  # 分析コメント

    def format(self) -> str:
        """射の提案テンプレートに統合可能な形式で出力"""
        lines = [f"📐 Aristos ルート分析 ({self.source} → {self.goal}):"]

        for label, emoji, route in [
            ("最短", "🔹", self.shortest),
            ("最速", "⚡", self.fastest),
            ("最深", "🔮", self.deepest),
        ]:
            if route and route.reachable:
                arrow = " → ".join(route.path)
                meta = []
                meta.append(f"{len(route.path)} steps")
                if route.time_min > 0:
                    meta.append(f"{route.time_min:.0f} min")
                if route.max_depth > 0:
                    depth_label = {0: "L0", 1: "L1", 2: "L2", 4: "L3"}.get(
                        int(route.max_depth), f"d={route.max_depth:.0f}"
                    )
                    meta.append(depth_label)
                lines.append(f"├─ {emoji} [{label}] {arrow} ({', '.join(meta)})")
            else:
                lines.append(f"├─ {emoji} [{label}] 到達不能")

        if self.context:
            lines.append(f"└─ ⚠️ {self.context}")
        else:
            lines.append("└─ (完了)")

        return "\n".join(lines)


@dataclass
class MacroAnalysis:
    """CCL マクロの経路分析結果"""
    name: str
    ccl_expr: str
    component_wfs: List[str]
    total_cost: CostVector
    critical_path: List[str]    # 最もコストが高い経路
    bottleneck: Optional[str] = None  # ボトルネック WF


# =============================================================================
# Router
# =============================================================================

class WorkflowRouter:
    """WF 間の最適経路探索エンジン

    WF 依存関係グラフ上で Dijkstra ベースの最短経路探索を行う。

    Usage:
        router = WorkflowRouter()
        router.build()  # グラフ構築
        route = router.find_shortest_path("boot", "ene")
    """

    def __init__(
        self,
        graph: Optional[WFGraph] = None,
        base_dir: Optional[Path] = None,
    ):
        self._graph = graph
        self._base_dir = base_dir or Path(".")
        self._calc = CostCalculator()
        self._builder = WorkflowGraphBuilder()

    @property
    def graph(self) -> WFGraph:
        if self._graph is None:
            self.build()
        return self._graph

    def build(self, base_dir: Optional[Path] = None) -> WFGraph:
        """WF 依存関係グラフを構築"""
        base = base_dir or self._base_dir
        self._graph = self._builder.build(base)
        return self._graph

    def find_shortest_path(self, start: str, goal: str) -> Route:
        """Dijkstra で最短経路を探索

        Args:
            start: 開始 WF 名
            goal: 目標 WF 名

        Returns:
            Route: 最短経路（到達不能なら reachable=False）
        """
        g = self.graph

        if start not in g.nodes or goal not in g.nodes:
            return Route(path=[], reachable=False)
        if start == goal:
            return Route(path=[start], total_cost=0.0, reachable=True)

        # Dijkstra
        dist: Dict[str, float] = {start: 0.0}
        prev: Dict[str, Optional[str]] = {start: None}
        visited: Set[str] = set()
        pq: list = [(0.0, start)]

        while pq:
            d, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)

            if u == goal:
                break

            for v, w in g.neighbors(u):
                if v in visited:
                    continue
                new_dist = d + w
                if new_dist < dist.get(v, float("inf")):
                    dist[v] = new_dist
                    prev[v] = u
                    heapq.heappush(pq, (new_dist, v))

        # 経路の復元
        if goal not in prev:
            return Route(path=[], reachable=False)

        path: List[str] = []
        segments: List[Tuple[str, str, float]] = []
        current = goal
        while current is not None:
            path.append(current)
            p = prev.get(current)
            if p is not None:
                edge_weight = dist[current] - dist[p]
                segments.append((p, current, edge_weight))
            current = p

        path.reverse()
        segments.reverse()

        return Route(
            path=path,
            total_cost=dist[goal],
            segments=segments,
            reachable=True,
        )

    def find_optimal_route(
        self,
        goal: str,
        constraints: Optional[Dict] = None,
    ) -> Route:
        """目標 WF に到達するための最適経路を探索

        全ノードからの最短経路を計算し、コスト最小のものを返す。

        Args:
            goal: 目標 WF 名
            constraints: コスト制約 (max_time, max_depth 等)
        """
        g = self.graph
        if goal not in g.nodes:
            return Route(path=[], reachable=False)

        # goal への逆方向依存 (どこから到達可能か)
        # 全ノードから目標への最短経路を計算し、最小コストのものを選択
        best_route = Route(path=[], reachable=False)
        best_cost = float("inf")

        for node_name in g.nodes:
            if node_name == goal:
                continue
            route = self.find_shortest_path(node_name, goal)
            if route.reachable and route.total_cost < best_cost:
                if constraints:
                    # 制約チェック
                    if not self._satisfies_constraints(route, constraints):
                        continue
                best_route = route
                best_cost = route.total_cost

        return best_route

    def analyze_macro(self, macro_name: str) -> Optional[MacroAnalysis]:
        """CCL マクロの経路コスト分析"""
        g = self.graph
        node = g.nodes.get(macro_name)
        if not node or not node.is_macro:
            return None

        components = node.dependencies
        if not components:
            return None

        # 構成 WF のコストを集計
        total_cost = self._calc.calculate_macro(
            macro_name, node.ccl_expr, components,
        )

        # クリティカルパス = 最もコストが高い WF をつなぐ経路
        critical = sorted(
            components,
            key=lambda wf: g.nodes[wf].cost.scalar() if wf in g.nodes and g.nodes[wf].cost else 0,
            reverse=True,
        )

        # ボトルネック = 最もコストが高い WF
        bottleneck = critical[0] if critical else None

        return MacroAnalysis(
            name=macro_name,
            ccl_expr=node.ccl_expr,
            component_wfs=components,
            total_cost=total_cost,
            critical_path=critical,
            bottleneck=bottleneck,
        )

    def reachable_from(self, start: str) -> Set[str]:
        """指定ノードから到達可能な全ノードを返す (BFS)"""
        g = self.graph
        if start not in g.nodes:
            return set()

        visited: Set[str] = set()
        queue = [start]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            for neighbor, _ in g.neighbors(current):
                if neighbor not in visited:
                    queue.append(neighbor)

        visited.discard(start)
        return visited

    def find_all_paths(
        self, start: str, goal: str, max_depth: int = 10,
    ) -> List[Route]:
        """全経路を探索 (DFS, max_depth 制限)"""
        g = self.graph
        if start not in g.nodes or goal not in g.nodes:
            return []

        results: List[Route] = []
        self._dfs_all_paths(g, start, goal, [start], set(), 0.0, max_depth, results)
        return sorted(results, key=lambda r: r.total_cost)

    def _dfs_all_paths(
        self,
        g: WFGraph,
        current: str,
        goal: str,
        path: List[str],
        visited: Set[str],
        cost: float,
        max_depth: int,
        results: List[Route],
    ) -> None:
        if current == goal:
            segments = []
            for i in range(len(path) - 1):
                # Find edge weight
                for n, w in g.neighbors(path[i]):
                    if n == path[i + 1]:
                        segments.append((path[i], path[i + 1], w))
                        break
            results.append(Route(
                path=list(path),
                total_cost=cost,
                segments=segments,
                reachable=True,
            ))
            return

        if len(path) >= max_depth:
            return

        visited.add(current)
        for neighbor, weight in g.neighbors(current):
            if neighbor not in visited:
                path.append(neighbor)
                self._dfs_all_paths(g, neighbor, goal, path, visited, cost + weight, max_depth, results)
                path.pop()
        visited.discard(current)

    def _satisfies_constraints(self, route: Route, constraints: Dict) -> bool:
        """経路が制約を満たすか検証"""
        g = self.graph
        max_time = constraints.get("max_time")
        max_depth = constraints.get("max_depth")
        max_steps = constraints.get("max_steps")

        if max_steps and len(route.path) > max_steps:
            return False

        if max_time:
            total_time = sum(
                g.nodes[wf].cost.time_min
                for wf in route.path
                if wf in g.nodes and g.nodes[wf].cost
            )
            if total_time > max_time:
                return False

        if max_depth:
            max_d = max(
                g.nodes[wf].cost.depth
                for wf in route.path
                if wf in g.nodes and g.nodes[wf].cost
            )
            if max_d > max_depth:
                return False

        return True

    def suggest_routes(
        self,
        source: str,
        goal: str,
    ) -> RouteSuggestion:
        """3つのヒューリスティクスをたたき台として提示

        Args:
            source: 現在の WF (起点)
            goal: 目標 WF

        Returns:
            RouteSuggestion: 最短/最速/最深の3候補
        """
        g = self.graph
        suggestion = RouteSuggestion(goal=goal, source=source)

        if source not in g.nodes or goal not in g.nodes:
            return suggestion

        # 全経路を取得 (ベース)
        all_paths = self.find_all_paths(source, goal, max_depth=8)
        if not all_paths:
            return suggestion

        # 各経路にメタデータを付与
        for route in all_paths:
            total_time = 0.0
            max_d = 0.0
            for wf in route.path:
                node = g.nodes.get(wf)
                if node and node.cost:
                    total_time += node.cost.time_min
                    max_d = max(max_d, node.cost.depth)
            route.time_min = total_time
            route.max_depth = max_d

        # 最短 = ステップ数最少
        shortest = copy.copy(min(all_paths, key=lambda r: len(r.path)))
        shortest.heuristic = "shortest"
        suggestion.shortest = shortest

        # 最速 = 推定時間最少
        fastest = copy.copy(min(all_paths, key=lambda r: r.time_min))
        fastest.heuristic = "fastest"
        suggestion.fastest = fastest

        # 最深 = 最大認知深度が最高 (同率なら時間が長い方 = より深い)
        deepest = copy.copy(max(all_paths, key=lambda r: (r.max_depth, r.time_min)))
        deepest.heuristic = "deepest"
        suggestion.deepest = deepest

        # コンテキスト: 3つが同じなら注記
        if shortest.path == fastest.path == deepest.path:
            suggestion.context = "全ヒューリスティクスが同一経路 — 選択の余地なし"
        elif fastest.max_depth < 2.0:
            suggestion.context = f"最速ルートは認知深度が浅い (L{int(fastest.max_depth)})。深い分析が必要なら最深ルート推奨"

        return suggestion

    def summary(self) -> str:
        """ルーターのサマリー"""
        return self.graph.summary()
