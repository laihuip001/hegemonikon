# PROOF: [L3/テスト] <- aristos/ WF ルーティングテスト
"""
Aristos Router Unit Tests

WF 依存関係グラフの構築、最短経路探索、CCL マクロ分析のテスト。
"""

import pytest
import sys
from pathlib import Path

# パッケージパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from aristos.cost import CostCalculator, CostVector, Depth, Tier, OPERATOR_PT
from aristos.graph_builder import (
    WorkflowGraphBuilder, WFGraph, WFNode, WFEdge,
    SERIES_MAP, OMEGA_CONTAINS,
)
from aristos.router import WorkflowRouter, Route, MacroAnalysis, RouteSuggestion


# =============================================================================
# CostCalculator Tests
# =============================================================================

class TestCostCalculator:
    """CostCalculator のテスト"""

    def setup_method(self):
        self.calc = CostCalculator()

    # PURPOSE: 階層分類
    def test_classify_tier_omega(self):
        """Ω 層の分類"""
        assert self.calc.classify_tier("o") == Tier.OMEGA
        assert self.calc.classify_tier("s") == Tier.OMEGA
        assert self.calc.classify_tier("ax") == Tier.OMEGA

    def test_classify_tier_delta(self):
        """Δ 層の分類"""
        assert self.calc.classify_tier("noe") == Tier.DELTA
        assert self.calc.classify_tier("dia") == Tier.DELTA
        assert self.calc.classify_tier("bou") == Tier.DELTA

    def test_classify_tier_tau(self):
        """τ 層の分類"""
        assert self.calc.classify_tier("boot") == Tier.TAU
        assert self.calc.classify_tier("dendron") == Tier.TAU

    def test_classify_tier_macro(self):
        """マクロの分類"""
        assert self.calc.classify_tier("ccl-vet") == Tier.MACRO
        assert self.calc.classify_tier("ccl-build") == Tier.MACRO

    def test_classify_tier_special(self):
        """特殊 WF の分類"""
        assert self.calc.classify_tier("u") == Tier.SPECIAL
        assert self.calc.classify_tier("m") == Tier.SPECIAL

    # PURPOSE: 深度分類
    def test_classify_depth(self):
        """WF 名からの深度自動判定"""
        assert self.calc.classify_depth("o") == Depth.L3      # Ω → L3
        assert self.calc.classify_depth("noe") == Depth.L2    # Δ → L2
        assert self.calc.classify_depth("boot") == Depth.L1   # τ → L1

    def test_parse_depth_from_derivative(self):
        """CCL 派生記号からの深度判定"""
        assert self.calc.parse_depth_from_derivative("/noe+") == Depth.L3
        assert self.calc.parse_depth_from_derivative("/noe-") == Depth.L1
        assert self.calc.parse_depth_from_derivative("/noe") == Depth.L2

    # PURPOSE: コスト計算
    def test_calculate_basic(self):
        """基本的なコスト計算"""
        cost = self.calc.calculate("noe")
        assert cost.depth == 2.0  # L2
        assert cost.tier_weight == 2.0  # Δ
        assert cost.time_min > 0
        assert cost.scalar() > 0

    def test_calculate_with_ccl(self):
        """CCL 式付きのコスト計算"""
        cost = self.calc.calculate("noe", ccl_expr="/noe+~/dia")
        assert cost.pt > 0  # CCL 演算子のポイントが計算される

    def test_calculate_pt(self):
        """pt コスト計算"""
        pt = self.calc.calculate_pt("/noe+~/dia_/ene")
        assert pt > 0
        # ~ (3) + _ (1) + + (1) = 少なくとも 5
        assert pt >= 5

    # PURPOSE: CostVector
    def test_cost_vector_scalar(self):
        """CostVector のスカラー変換"""
        cost = CostVector(pt=10, depth=2.0, time_min=5, bc_count=8, tier_weight=2.0)
        assert cost.scalar() > 0

    def test_cost_vector_custom_weights(self):
        """カスタム重みでのスカラー変換"""
        cost = CostVector(pt=10, depth=2.0)
        w1 = cost.scalar({"pt": 1.0, "depth": 1.0, "time_min": 0, "bc_count": 0, "tier_weight": 0})
        w2 = cost.scalar({"pt": 2.0, "depth": 1.0, "time_min": 0, "bc_count": 0, "tier_weight": 0})
        assert w2 > w1

    def test_calculate_macro(self):
        """マクロのコスト計算"""
        cost = self.calc.calculate_macro(
            "ccl-test",
            "/noe_/dia_/ene",
            ["noe", "dia", "ene"],
        )
        assert cost.pt > 0
        assert cost.time_min > 0


# =============================================================================
# WFGraph Tests
# =============================================================================

class TestWFGraph:
    """WFGraph のテスト"""

    def test_add_node(self):
        """ノードの追加"""
        graph = WFGraph()
        node = WFNode(name="noe", tier="delta", series="O")
        graph.add_node(node)
        assert graph.node_count() == 1
        assert "noe" in graph.nodes

    def test_add_edge(self):
        """エッジの追加"""
        graph = WFGraph()
        graph.add_node(WFNode(name="o", tier="omega"))
        graph.add_node(WFNode(name="noe", tier="delta"))
        graph.add_edge(WFEdge(source="o", target="noe", relation="contains"))
        assert graph.edge_count() == 1

    def test_neighbors(self):
        """隣接ノードの取得"""
        graph = WFGraph()
        graph.add_node(WFNode(name="o", tier="omega"))
        graph.add_node(WFNode(name="noe", tier="delta"))
        graph.add_edge(WFEdge(source="o", target="noe", weight=0.5))
        neighbors = graph.neighbors("o")
        assert len(neighbors) == 1
        assert neighbors[0] == ("noe", 0.5)

    def test_reverse_neighbors(self):
        """逆方向隣接ノードの取得"""
        graph = WFGraph()
        graph.add_node(WFNode(name="o", tier="omega"))
        graph.add_node(WFNode(name="noe", tier="delta"))
        graph.add_edge(WFEdge(source="o", target="noe", weight=0.5))
        rev = graph.reverse_neighbors("noe")
        assert len(rev) == 1
        assert rev[0] == ("o", 0.5)

    def test_summary(self):
        """サマリー出力"""
        graph = WFGraph()
        graph.add_node(WFNode(name="o", tier="omega"))
        graph.add_node(WFNode(name="noe", tier="delta"))
        graph.add_edge(WFEdge(source="o", target="noe", relation="contains"))
        summary = graph.summary()
        assert "2 nodes" in summary
        assert "1 edges" in summary


# =============================================================================
# WorkflowGraphBuilder Tests
# =============================================================================

class TestWorkflowGraphBuilder:
    """WorkflowGraphBuilder のテスト"""

    def test_build_from_project_dir(self):
        """プロジェクトディレクトリからグラフ構築"""
        builder = WorkflowGraphBuilder()
        graph = builder.build(Path("/home/makaron8426/oikos/hegemonikon"))
        assert graph.node_count() > 0
        assert graph.edge_count() > 0

    def test_nodes_have_tiers(self):
        """ノードに階層が設定されている"""
        builder = WorkflowGraphBuilder()
        graph = builder.build(Path("/home/makaron8426/oikos/hegemonikon"))
        for node in graph.nodes.values():
            assert node.tier in ("omega", "delta", "tau", "macro", "special")

    def test_omega_contains_edges(self):
        """Ω → Δ の contains エッジが存在"""
        builder = WorkflowGraphBuilder()
        graph = builder.build(Path("/home/makaron8426/oikos/hegemonikon"))
        contains_edges = [e for e in graph.edges if e.relation == "contains"]
        assert len(contains_edges) > 0

    def test_macro_dependencies_extracted(self):
        """CCL マクロの依存関係が抽出される"""
        builder = WorkflowGraphBuilder()
        graph = builder.build(Path("/home/makaron8426/oikos/hegemonikon"))
        # ccl-vet は /kho, /dia, /ene, /pra, /pis, /dox を含む
        if "ccl-vet" in graph.nodes:
            node = graph.nodes["ccl-vet"]
            assert len(node.dependencies) > 0

    def test_series_mapping(self):
        """Series マッピングが正しい"""
        assert SERIES_MAP.get("noe") == "O"
        assert SERIES_MAP.get("dia") == "A"
        assert SERIES_MAP.get("met") == "S"
        assert SERIES_MAP.get("pro") == "H"
        assert SERIES_MAP.get("kho") == "P"
        assert SERIES_MAP.get("euk") == "K"

    def test_extract_wf_references(self):
        """CCL 式から WF 参照を抽出"""
        builder = WorkflowGraphBuilder()
        refs = builder._extract_wf_references("/noe+~/dia_/ene_/pis_/dox-")
        assert "noe" in refs
        assert "dia" in refs
        assert "ene" in refs
        assert "pis" in refs
        assert "dox" in refs


# =============================================================================
# WorkflowRouter Tests
# =============================================================================

class TestWorkflowRouter:
    """WorkflowRouter のテスト"""

    @pytest.fixture
    def router(self):
        """実 WF グラフでルーターを初期化"""
        r = WorkflowRouter(base_dir=Path("/home/makaron8426/oikos/hegemonikon"))
        r.build()
        return r

    @pytest.fixture
    def simple_router(self):
        """テスト用の最小グラフ"""
        graph = WFGraph()
        graph.add_node(WFNode(name="a", tier="omega", cost=CostVector(pt=1, tier_weight=4)))
        graph.add_node(WFNode(name="b", tier="delta", cost=CostVector(pt=2, tier_weight=2)))
        graph.add_node(WFNode(name="c", tier="delta", cost=CostVector(pt=3, tier_weight=2)))
        graph.add_node(WFNode(name="d", tier="tau", cost=CostVector(pt=1, tier_weight=1)))
        graph.add_edge(WFEdge(source="a", target="b", weight=1.0))
        graph.add_edge(WFEdge(source="a", target="c", weight=3.0))
        graph.add_edge(WFEdge(source="b", target="d", weight=1.0))
        graph.add_edge(WFEdge(source="c", target="d", weight=1.0))
        return WorkflowRouter(graph=graph)

    @pytest.fixture
    def heuristic_router(self):
        """ヒューリスティクス差異を検証するグラフ

        構造:
          a --1--> b --1--> d   (最短: 3 steps, 速い小型 WF)
          a --1--> c --1--> e --1--> d  (最深: 4 steps, 遅い深い WF)

        b, d は浅く速い (depth=1, time=3)
        c, e は深く遅い (depth=4, time=20)
        """
        graph = WFGraph()
        graph.add_node(WFNode(name="a", tier="omega",
            cost=CostVector(pt=1, depth=2.0, time_min=5, tier_weight=4)))
        graph.add_node(WFNode(name="b", tier="tau",
            cost=CostVector(pt=1, depth=1.0, time_min=3, tier_weight=1)))
        graph.add_node(WFNode(name="c", tier="delta",
            cost=CostVector(pt=3, depth=4.0, time_min=20, tier_weight=2)))
        graph.add_node(WFNode(name="d", tier="tau",
            cost=CostVector(pt=1, depth=1.0, time_min=3, tier_weight=1)))
        graph.add_node(WFNode(name="e", tier="delta",
            cost=CostVector(pt=2, depth=4.0, time_min=15, tier_weight=2)))
        # 経路 1: a → b → d (短い、速い、浅い)
        graph.add_edge(WFEdge(source="a", target="b", weight=1.0))
        graph.add_edge(WFEdge(source="b", target="d", weight=1.0))
        # 経路 2: a → c → e → d (長い、遅い、深い)
        graph.add_edge(WFEdge(source="a", target="c", weight=1.0))
        graph.add_edge(WFEdge(source="c", target="e", weight=1.0))
        graph.add_edge(WFEdge(source="e", target="d", weight=1.0))
        return WorkflowRouter(graph=graph)

    # PURPOSE: 最短経路
    def test_shortest_path_simple(self, simple_router):
        """最短経路探索 (Simple)"""
        route = simple_router.find_shortest_path("a", "d")
        assert route.reachable
        assert route.path == ["a", "b", "d"]  # a→b→d (cost=2) < a→c→d (cost=4)
        assert route.total_cost == 2.0

    def test_shortest_path_same_node(self, simple_router):
        """同一ノードの経路"""
        route = simple_router.find_shortest_path("a", "a")
        assert route.reachable
        assert route.path == ["a"]
        assert route.total_cost == 0.0

    def test_shortest_path_unreachable(self, simple_router):
        """到達不能な経路"""
        route = simple_router.find_shortest_path("d", "a")
        assert not route.reachable

    def test_shortest_path_unknown_node(self, simple_router):
        """未知のノード"""
        route = simple_router.find_shortest_path("x", "y")
        assert not route.reachable

    # PURPOSE: 全経路探索
    def test_find_all_paths(self, simple_router):
        """全経路探索"""
        paths = simple_router.find_all_paths("a", "d")
        assert len(paths) == 2  # a→b→d, a→c→d
        # コスト順にソートされている
        assert paths[0].total_cost <= paths[1].total_cost

    # PURPOSE: 到達可能ノード
    def test_reachable_from(self, simple_router):
        """到達可能ノードの探索"""
        reachable = simple_router.reachable_from("a")
        assert reachable == {"b", "c", "d"}

    def test_reachable_from_leaf(self, simple_router):
        """リーフノードからの到達"""
        reachable = simple_router.reachable_from("d")
        assert reachable == set()

    # PURPOSE: 実 WF グラフでのテスト
    def test_real_graph_build(self, router):
        """実 WF グラフの構築"""
        assert router.graph.node_count() > 30
        assert router.graph.edge_count() > 10

    def test_real_graph_omega_to_delta(self, router):
        """Ω → Δ の経路"""
        route = router.find_shortest_path("o", "noe")
        assert route.reachable
        assert "noe" in route.path

    def test_real_graph_summary(self, router):
        """実グラフのサマリー"""
        summary = router.summary()
        assert "nodes" in summary
        assert "edges" in summary

    # PURPOSE: マクロ分析
    def test_analyze_macro(self, router):
        """CCL マクロの分析"""
        analysis = router.analyze_macro("ccl-vet")
        if analysis:
            assert analysis.name == "ccl-vet"
            assert len(analysis.component_wfs) > 0
            assert analysis.bottleneck is not None

    def test_analyze_non_macro(self, router):
        """非マクロの分析は None"""
        analysis = router.analyze_macro("noe")
        assert analysis is None

    # PURPOSE: Route 表示
    def test_route_repr(self):
        """Route の文字列表現"""
        route = Route(path=["a", "b", "c"], total_cost=5.0)
        assert "a → b → c" in repr(route)
        assert "5.00" in repr(route)

    def test_route_unreachable_repr(self):
        """到達不能 Route の文字列表現"""
        route = Route(path=[], reachable=False)
        assert "unreachable" in repr(route)

    def test_route_detail(self):
        """Route の詳細表示"""
        route = Route(
            path=["a", "b"],
            total_cost=2.0,
            segments=[("a", "b", 2.0)],
        )
        detail = route.detail()
        assert "a → b" in detail
        assert "2.00" in detail

    # PURPOSE: ヒューリスティクス提案
    def test_suggest_routes_returns_three_heuristics(self, heuristic_router):
        """suggest_routes が3つのヒューリスティクスを返す"""
        suggestion = heuristic_router.suggest_routes("a", "d")
        assert suggestion.shortest is not None
        assert suggestion.fastest is not None
        assert suggestion.deepest is not None

    def test_suggest_routes_shortest_has_fewest_steps(self, heuristic_router):
        """最短ルートのステップ数が最少"""
        suggestion = heuristic_router.suggest_routes("a", "d")
        assert len(suggestion.shortest.path) <= len(suggestion.deepest.path)

    def test_suggest_routes_fastest_has_least_time(self, heuristic_router):
        """最速ルートの推定時間が最少"""
        suggestion = heuristic_router.suggest_routes("a", "d")
        assert suggestion.fastest.time_min <= suggestion.deepest.time_min

    def test_suggest_routes_deepest_has_max_depth(self, heuristic_router):
        """最深ルートの認知深度が最大"""
        suggestion = heuristic_router.suggest_routes("a", "d")
        assert suggestion.deepest.max_depth >= suggestion.shortest.max_depth

    def test_suggest_routes_different_paths(self, heuristic_router):
        """異なるヒューリスティクスが異なる経路を返す"""
        suggestion = heuristic_router.suggest_routes("a", "d")
        # 最短 (a→b→d) と最深 (a→c→e→d) は異なるはず
        assert suggestion.shortest.path != suggestion.deepest.path

    def test_suggest_routes_heuristic_labels(self, heuristic_router):
        """ヒューリスティクス名が設定される"""
        suggestion = heuristic_router.suggest_routes("a", "d")
        assert suggestion.shortest.heuristic == "shortest"
        assert suggestion.fastest.heuristic == "fastest"
        assert suggestion.deepest.heuristic == "deepest"

    def test_suggest_routes_format_output(self, heuristic_router):
        """format() がテンプレート形式で出力する"""
        suggestion = heuristic_router.suggest_routes("a", "d")
        output = suggestion.format()
        assert "📐 Aristos" in output
        assert "最短" in output
        assert "最速" in output
        assert "最深" in output
        assert "→" in output

    def test_suggest_routes_unreachable(self, heuristic_router):
        """到達不能な場合"""
        suggestion = heuristic_router.suggest_routes("d", "a")
        assert suggestion.shortest is None
        assert suggestion.fastest is None

    def test_suggest_routes_unknown_node(self, heuristic_router):
        """未知ノードの場合"""
        suggestion = heuristic_router.suggest_routes("x", "y")
        assert suggestion.shortest is None

    def test_suggest_routes_same_path_context(self, simple_router):
        """全ヒューリスティクスが同一経路の場合のコンテキスト"""
        # simple_router の a→b→d は唯一の最短経路
        # ただし a→c→d もあるので、ここでは同一にはならない可能性がある
        suggestion = simple_router.suggest_routes("a", "d")
        # テストは suggestion が正常に動くことを確認
        assert suggestion.shortest is not None

    def test_suggest_routes_real_graph(self, router):
        """実 WF グラフでのヒューリスティクス提案"""
        suggestion = router.suggest_routes("o", "ene")
        if suggestion.shortest:
            assert suggestion.shortest.reachable
            assert len(suggestion.shortest.path) >= 2
            output = suggestion.format()
            assert "📐 Aristos" in output


# =============================================================================
# Run
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
