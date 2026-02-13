# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: /api/link-graph/* — 知識リンクグラフ API (V2 射影統合)
"""
Link Graph Routes — LinkGraph データを 3D 可視化用 JSON API で提供

GET /api/link-graph/full              — 全ノード + エッジ + 射影情報
GET /api/link-graph/stats             — 統計 + ブリッジノード + コミュニティ
GET /api/link-graph/neighbors/{node_id} — 近傍ノード (hops 指定可)
"""

import math
import logging
from typing import Any, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# --- source_type → Series 射影マッピング ---
# /dia+ 修正提案 #1: 分離された dict で将来のリンクベース自動推定と差替可能
PROJECTION_MAP: dict[str, str] = {
    "kernel": "O",     # 体系の本質
    "ki": "O",         # 知識項目 = 本質
    "doxa": "H",       # 信念 = H4 Doxa
    "workflow": "S",   # 方法の様態
    "research": "K",   # 知恵 = K4 Sophia
    "xseries": "A",    # 精密な関係定義
    "handoff": "K",    # 文脈・時間情報
    "session": "K",    # 時間的コンテキスト
    "review": "A",     # 評価・判定
    "knowledge": "P",  # 境界・条件 (catch-all)
}

# Series 内のデフォルト定理マッピング (source_type が定理を直接参照していない場合のフォールバック)
_SERIES_DEFAULT_THEOREM: dict[str, str] = {
    "O": "O1",  # Noēsis
    "S": "S2",  # Mekhanē
    "H": "H4",  # Doxa
    "P": "P1",  # Khōra
    "K": "K4",  # Sophia
    "A": "A2",  # Krisis
}

# 定理 ID → name (3D Graph 上の既存ノードとの接続用)
_THEOREM_IDS = {
    f"{s}{i}" for s in "OSHPKA" for i in range(1, 5)
}


# --- Pydantic Models ---

# PURPOSE: の統一的インターフェースを実現する
class LinkGraphNode(BaseModel):
    """知識ノード (射影情報付き)."""
    id: str
    title: str
    source_type: str
    projected_series: str = Field(description="射影先 Series (O/S/H/P/K/A)")
    projected_theorem: str = Field(description="射影先定理 (e.g. O1)")
    degree: int = Field(description="接続度 (in + out)")
    backlink_count: int
    community: int = -1
    orbit_angle: float = Field(description="軌道上の角度 (radian)")
    orbit_radius: float = Field(description="定理ノードからの軌道半径")


# PURPOSE: の統一的インターフェースを実現する
class LinkGraphEdge(BaseModel):
    """知識ノード間のエッジ."""
    source: str
    target: str
    type: str = Field(description="outlink or backlink")


# PURPOSE: の統一的インターフェースを実現する
class LinkGraphFullResponse(BaseModel):
    """全データ一括レスポンス."""
    nodes: list[LinkGraphNode]
    edges: list[LinkGraphEdge]
    meta: dict[str, Any]


# PURPOSE: の統一的インターフェースを実現する
class LinkGraphStatsResponse(BaseModel):
    """統計レスポンス."""
    total_nodes: int
    total_edges: int
    bridge_nodes: list[str]
    source_type_counts: dict[str, int]
    projection_counts: dict[str, int]


# --- Projection Logic ---

# PURPOSE: [L2-auto] ノードの射影先 (Series, Theorem) を決定.
def _project_node(node, graph) -> tuple[str, str]:
    """ノードの射影先 (Series, Theorem) を決定.

    /dia+ 修正提案 #2: まずリンク関係から定理を探し、なければ source_type フォールバック。
    """
    # Strategy 1: ノードが [[wikilink]] で参照している定理ファイルを検出
    for out_link in node.out_links:
        out_upper = out_link.upper().replace("-", "").replace("_", "")
        for tid in _THEOREM_IDS:
            if tid.lower() in out_link.lower() or tid in out_upper:
                series = tid[0]
                return series, tid

    # Strategy 2: このノードを参照している定理ファイルを検出
    for in_link in node.in_links:
        in_upper = in_link.upper().replace("-", "").replace("_", "")
        for tid in _THEOREM_IDS:
            if tid.lower() in in_link.lower() or tid in in_upper:
                series = tid[0]
                return series, tid

    # Strategy 3: source_type フォールバック (PROJECTION_MAP)
    series = PROJECTION_MAP.get(node.source_type, "P")
    theorem = _SERIES_DEFAULT_THEOREM.get(series, "O1")
    return series, theorem


# PURPOSE: [L2-auto] 軌道上の角度と半径を計算.
def _compute_orbit(
    node_index: int,
    total_in_group: int,
    degree: int,
) -> tuple[float, float]:
    """軌道上の角度と半径を計算.

    - 角度: グループ内で均等配置
    - 半径: degree が大きいほど近い (重要なノードは定理に近い)
    """
    angle = (2 * math.pi * node_index) / max(total_in_group, 1)
    # 半径: 基本 12、degree が高いほど近い (最小 5)
    base_radius = 12.0
    radius = max(5.0, base_radius - degree * 0.3)
    return round(angle, 4), round(radius, 2)


# PURPOSE: [L2-auto] LinkGraph から API レスポンスを構築.
def _build_response(graph) -> LinkGraphFullResponse:
    """LinkGraph から API レスポンスを構築."""
    from collections import defaultdict

    # 射影グループ別にノードを整理
    projection_groups: dict[str, list] = defaultdict(list)

    for node_id, node in graph.nodes.items():
        series, theorem = _project_node(node, graph)
        projection_groups[theorem].append((node_id, node, series, theorem))

    # ノードを構築
    api_nodes: list[LinkGraphNode] = []
    for theorem, group in projection_groups.items():
        for idx, (node_id, node, series, thm) in enumerate(group):
            degree = len(set(node.out_links + node.in_links))
            angle, radius = _compute_orbit(idx, len(group), degree)

            api_nodes.append(LinkGraphNode(
                id=node_id,
                title=node.title[:100],
                source_type=node.source_type,
                projected_series=series,
                projected_theorem=thm,
                degree=degree,
                backlink_count=len(node.in_links),
                community=node.community,
                orbit_angle=angle,
                orbit_radius=radius,
            ))

    # エッジを構築
    api_edges: list[LinkGraphEdge] = []
    seen_edges: set[tuple[str, str]] = set()
    for node_id, node in graph.nodes.items():
        for target in node.out_links:
            if target in graph.nodes:
                edge_key = (node_id, target)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    api_edges.append(LinkGraphEdge(
                        source=node_id,
                        target=target,
                        type="outlink",
                    ))

    # メタデータ
    from collections import Counter
    source_counts = Counter(n.source_type for n in graph.nodes.values())
    proj_counts = Counter(n.projected_series for n in api_nodes)

    meta = {
        "total_nodes": len(api_nodes),
        "total_edges": len(api_edges),
        "source_type_counts": dict(source_counts),
        "projection_counts": dict(proj_counts),
        "projection_map": PROJECTION_MAP,
    }

    return LinkGraphFullResponse(nodes=api_nodes, edges=api_edges, meta=meta)


# --- Router ---

router = APIRouter(prefix="/link-graph", tags=["link-graph"])


# PURPOSE: link graph full を取得する
@router.get("/full", response_model=LinkGraphFullResponse)
async def get_link_graph_full(
    source_type: Optional[str] = Query(None, description="カンマ区切りの source_type フィルタ"),
) -> LinkGraphFullResponse:
    """全ノード + エッジ + 射影情報."""
    from mekhane.anamnesis.link_graph import load_or_build_graph

    graph = load_or_build_graph()
    response = _build_response(graph)

    # source_type フィルタ
    if source_type:
        allowed = set(source_type.split(","))
        response.nodes = [n for n in response.nodes if n.source_type in allowed]
        node_ids = {n.id for n in response.nodes}
        response.edges = [e for e in response.edges if e.source in node_ids and e.target in node_ids]
        response.meta["total_nodes"] = len(response.nodes)
        response.meta["total_edges"] = len(response.edges)

    return response


# PURPOSE: link graph stats を取得する
@router.get("/stats", response_model=LinkGraphStatsResponse)
async def get_link_graph_stats() -> LinkGraphStatsResponse:
    """統計 + ブリッジノード."""
    from mekhane.anamnesis.link_graph import load_or_build_graph

    graph = load_or_build_graph()
    bridges = graph.find_bridge_nodes()

    from collections import Counter
    source_counts = Counter(n.source_type for n in graph.nodes.values())

    # 射影集計
    proj_counts: dict[str, int] = {}
    for node in graph.nodes.values():
        series, _ = _project_node(node, graph)
        proj_counts[series] = proj_counts.get(series, 0) + 1

    total_edges = sum(len(n.out_links) for n in graph.nodes.values())

    return LinkGraphStatsResponse(
        total_nodes=len(graph.nodes),
        total_edges=total_edges,
        bridge_nodes=bridges[:20],
        source_type_counts=dict(source_counts),
        projection_counts=proj_counts,
    )


# PURPOSE: neighbors を取得する
@router.get("/neighbors/{node_id}")
async def get_neighbors(
    node_id: str,
    hops: int = Query(2, ge=1, le=5),
) -> dict[str, Any]:
    """近傍ノード."""
    from mekhane.anamnesis.link_graph import load_or_build_graph

    graph = load_or_build_graph()
    if node_id not in graph.nodes:
        return {"node_id": node_id, "error": "not found", "neighbors": []}

    neighbor_ids = graph.get_neighbors(node_id, hops=hops)
    neighbors = []
    for nid in neighbor_ids:
        if nid in graph.nodes:
            node = graph.nodes[nid]
            series, theorem = _project_node(node, graph)
            neighbors.append({
                "id": nid,
                "title": node.title,
                "source_type": node.source_type,
                "projected_series": series,
                "projected_theorem": theorem,
                "degree": len(set(node.out_links + node.in_links)),
            })

    return {
        "node_id": node_id,
        "hops": hops,
        "neighbors": neighbors,
        "total": len(neighbors),
    }
