# F11: Compare Routes テスト
"""
WorkflowRouter.compare_routes() の A/B 比較テスト。
evolved weights vs default weights の diff_pct 計算を検証。
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from aristos.router import WorkflowRouter, Route
from aristos.graph_builder import WFGraph, WFNode, WFEdge
from aristos.cost import CostVector


def _make_test_graph() -> WFGraph:
    """テスト用の小さなグラフ"""
    g = WFGraph()
    for name in ["noe", "dia", "ene", "dox"]:
        g.nodes[name] = WFNode(
            name=name,
            cost=CostVector(pt=1.0, depth=2, time_min=5.0),
        )
    g.edges.append(WFEdge(source="noe", target="dia", weight=2.0))
    g.edges.append(WFEdge(source="dia", target="ene", weight=3.0))
    g.edges.append(WFEdge(source="ene", target="dox", weight=1.5))
    g.edges.append(WFEdge(source="noe", target="ene", weight=6.0))
    return g


class TestCompareRoutesBasic:
    """compare_routes 基本テスト"""

    def test_returns_both_routes(self, tmp_path):
        """evolved と default の両方を返す"""
        g = _make_test_graph()
        router = WorkflowRouter(graph=g, base_dir=tmp_path)
        result = router.compare_routes("noe", "dox", base_dir=tmp_path)
        assert "evolved" in result
        assert "default" in result
        assert "diff_pct" in result

    def test_diff_pct_is_float(self, tmp_path):
        """diff_pct が float"""
        g = _make_test_graph()
        router = WorkflowRouter(graph=g, base_dir=tmp_path)
        result = router.compare_routes("noe", "dox", base_dir=tmp_path)
        assert isinstance(result["diff_pct"], float)

    def test_same_weights_zero_diff(self, tmp_path):
        """同一重みなら diff_pct ≈ 0"""
        default_w = {
            "pt": 1.0, "depth": 2.0, "time_min": 0.5,
            "bc_count": 0.3, "tier_weight": 1.0,
        }
        g = _make_test_graph()
        router = WorkflowRouter(
            graph=g,
            base_dir=tmp_path,
            evolved_weights=default_w,
        )
        result = router.compare_routes("noe", "dox", base_dir=tmp_path)
        assert abs(result["diff_pct"]) < 0.1


class TestCompareRoutesEdgeCases:
    """edge case テスト"""

    def test_unreachable_nodes(self, tmp_path):
        """到達不能 → diff_pct = 0"""
        g = WFGraph()
        g.nodes["a"] = WFNode(name="a")
        g.nodes["z"] = WFNode(name="z")
        router = WorkflowRouter(graph=g, base_dir=tmp_path)
        result = router.compare_routes("a", "z", base_dir=tmp_path)
        assert result["diff_pct"] == 0.0

    def test_evolved_route_reachable(self, tmp_path):
        """evolved route の可達性"""
        g = _make_test_graph()
        router = WorkflowRouter(graph=g, base_dir=tmp_path)
        result = router.compare_routes("noe", "dox", base_dir=tmp_path)
        evolved = result["evolved"]
        assert isinstance(evolved, Route)
