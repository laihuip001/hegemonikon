# PROOF: [L2/インフラ] <- mekhane/api/routes/
# PURPOSE: /api/graph/* — Hegemonikón 96要素グラフデータ
"""
Graph Routes — Trígōnon/Taxis データを JSON API で提供

GET /api/graph/nodes      — 24 定理 + 7 公理ノード
GET /api/graph/edges      — 78 X-series エッジ (72 relations + 6 identity)
GET /api/graph/full       — ノード + エッジ + メタデータ一括
"""

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

# --- データ定義 ---

# PURPOSE: 6 Series の定義
SERIES = {
    "O": {"name": "Ousia", "greek": "οὐσία", "meaning": "本質", "type": "Pure",
           "tier": "L1×L1", "color": "#00d4ff", "coordinates": ["Flow", "Value"]},
    "S": {"name": "Schema", "greek": "σχήμα", "meaning": "様態", "type": "Mixed",
           "tier": "L1×L1.5", "color": "#10b981", "coordinates": ["Flow", "Scale"]},
    "H": {"name": "Hormē", "greek": "ὁρμή", "meaning": "傾向", "type": "Mixed",
           "tier": "L1×L1.75", "color": "#ef4444", "coordinates": ["Flow", "Valence"]},
    "P": {"name": "Perigraphē", "greek": "περιγραφή", "meaning": "境界", "type": "Pure",
           "tier": "L1.5×L1.5", "color": "#a855f7", "coordinates": ["Scale", "Function"]},
    "K": {"name": "Kairos", "greek": "καιρός", "meaning": "文脈", "type": "Mixed",
           "tier": "L1.5×L1.75", "color": "#f59e0b", "coordinates": ["Scale", "Valence"]},
    "A": {"name": "Akribeia", "greek": "ἀκρίβεια", "meaning": "精密", "type": "Pure",
           "tier": "L1.75×L1.75", "color": "#f97316", "coordinates": ["Valence", "Precision"]},
}

# PURPOSE: 24 定理（6 Series × 4 per series）
THEOREMS: list[dict[str, Any]] = []
_THEOREM_NAMES = {
    "O1": ("Noēsis", "νόησις", "深い認識"),
    "O2": ("Boulēsis", "βούλησις", "意志"),
    "O3": ("Zētēsis", "ζήτησις", "探求"),
    "O4": ("Energeia", "ἐνέργεια", "行為"),
    "S1": ("Metron", "μέτρον", "尺度"),
    "S2": ("Mekhanē", "μηχανή", "方法"),
    "S3": ("Stathmos", "σταθμός", "基準"),
    "S4": ("Praxis", "πρᾶξις", "実践"),
    "H1": ("Propatheia", "προπάθεια", "前感情"),
    "H2": ("Pistis", "πίστις", "確信"),
    "H3": ("Orexis", "ὄρεξις", "欲求"),
    "H4": ("Doxa", "δόξα", "信念"),
    "P1": ("Khōra", "χώρα", "場"),
    "P2": ("Hodos", "ὁδός", "道"),
    "P3": ("Trokhia", "τροχιά", "軌道"),
    "P4": ("Tekhnē", "τέχνη", "技法"),
    "K1": ("Eukairia", "εὐκαιρία", "好機"),
    "K2": ("Chronos", "χρόνος", "時間"),
    "K3": ("Telos", "τέλος", "目的"),
    "K4": ("Sophia", "σοφία", "知恵"),
    "A1": ("Pathos", "πάθος", "情念"),
    "A2": ("Krisis", "κρίσις", "判定"),
    "A3": ("Gnōmē", "γνώμη", "格言"),
    "A4": ("Epistēmē", "ἐπιστήμη", "知識"),
}

# PURPOSE: Trígōnon 三角形構造の初期 3D 座標
# 三角形の頂点 (O, P, A) を正三角形に、辺 (S, H, K) をその中間に配置
import math
_R = 5.0  # 三角形の半径
_SERIES_POSITIONS = {
    # Pure: 頂点 (正三角形)
    "O": (0.0, _R, 0.0),           # 頂点: 上
    "P": (-_R * math.sin(2*math.pi/3), -_R * 0.5, 0.0),  # 左下
    "A": (_R * math.sin(2*math.pi/3), -_R * 0.5, 0.0),    # 右下
    # Mixed: 辺の中点
    "S": (-_R * math.sin(math.pi/3) * 0.5, _R * 0.25, 0.0),  # O-P 間
    "H": (_R * math.sin(math.pi/3) * 0.5, _R * 0.25, 0.0),   # O-A 間
    "K": (0.0, -_R * 0.5, 0.0),   # P-A 間
}

for series_id, series_info in SERIES.items():
    for i in range(1, 5):
        tid = f"{series_id}{i}"
        name, greek, meaning = _THEOREM_NAMES[tid]
        # 各定理は Series 中心からわずかにオフセット
        base_x, base_y, base_z = _SERIES_POSITIONS[series_id]
        offset_x = ((i - 1) % 2 - 0.5) * 0.8
        offset_y = ((i - 1) // 2 - 0.5) * 0.8
        THEOREMS.append({
            "id": tid,
            "series": series_id,
            "name": name,
            "greek": greek,
            "meaning": meaning,
            "workflow": f"/{name.lower()}" if tid != "A2" else "/dia",
            "type": series_info["type"],
            "color": series_info["color"],
            "position": {"x": base_x + offset_x, "y": base_y + offset_y, "z": 0.0},
        })

# PURPOSE: 78 X-series エッジ (9 ペア × 8 + 6 恒等射)
_EDGE_DEFS = [
    # (pair_id, source_series, target_series, shared_coord, naturality, meaning)
    ("X-OS", "O", "S", "Flow", "experiential",    "本質→様態"),
    ("X-OH", "O", "H", "Flow", "experiential",    "本質→傾向"),
    ("X-SH", "S", "H", "Flow", "reflective",      "様態→傾向"),
    ("X-SP", "S", "P", "Scale", "structural",     "様態→条件"),
    ("X-SK", "S", "K", "Scale", "structural",     "様態→文脈"),
    ("X-PK", "P", "K", "Scale", "structural",     "条件→文脈"),
    ("X-HA", "H", "A", "Valence", "experiential", "傾向→精密"),
    ("X-HK", "H", "K", "Valence", "reflective",   "傾向→文脈"),
    ("X-KA", "K", "A", "Valence", "reflective",   "文脈→精密"),
]

# 各ペアの 8 エッジを生成
EDGES: list[dict[str, Any]] = []
for pair_id, src_s, tgt_s, shared, nat, meaning in _EDGE_DEFS:
    for i in range(1, 9):
        EDGES.append({
            "id": f"{pair_id}{i}",
            "pair": pair_id,
            "source": f"{src_s}{((i-1)//2)%2 + 1 + ((i-1)//4)*2}",
            "target": f"{tgt_s}{((i-1) % 2) + 1 + ((i-1)//4)*2}",
            "shared_coordinate": shared,
            "naturality": nat,
            "meaning": meaning,
            "type": "bridge" if SERIES[src_s]["type"] == "Mixed" and SERIES[tgt_s]["type"] == "Mixed" else "anchor",
        })

# 6 恒等射
for series_id in SERIES:
    for i in range(1, 5):
        tid = f"{series_id}{i}"
        EDGES.append({
            "id": f"X-{series_id}{series_id}{i}",
            "pair": f"X-{series_id}{series_id}",
            "source": tid,
            "target": tid,
            "shared_coordinate": "identity",
            "naturality": "identity",
            "meaning": "恒等射",
            "type": "identity",
        })


# --- Pydantic Models ---

# PURPOSE: グラフノードの定義
class GraphNode(BaseModel):
    id: str
    series: str
    name: str
    greek: str
    meaning: str
    workflow: str
    type: str = Field(description="Pure or Mixed")
    color: str
    position: dict[str, float]

# PURPOSE: グラフエッジの定義
class GraphEdge(BaseModel):
    id: str
    pair: str
    source: str
    target: str
    shared_coordinate: str
    naturality: str = Field(description="experiential, reflective, structural, or identity")
    meaning: str
    type: str = Field(description="anchor, bridge, or identity")

# PURPOSE: グラフ全データのレスポンスモデル
class GraphFullResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    meta: dict[str, Any]


# --- Router ---

router = APIRouter(prefix="/graph", tags=["graph"])


# PURPOSE: 24 定理ノードを取得
@router.get("/nodes", response_model=list[GraphNode])
async def get_graph_nodes() -> list[GraphNode]:
    """24 定理ノードを返す。"""
    return [GraphNode(**t) for t in THEOREMS]


# PURPOSE: 78 X-series エッジを取得
@router.get("/edges", response_model=list[GraphEdge])
async def get_graph_edges() -> list[GraphEdge]:
    """78 X-series エッジを返す (72 relations + 6 identity morphisms)。"""
    return [GraphEdge(**e) for e in EDGES]


# PURPOSE: グラフ全データを一括取得
@router.get("/full", response_model=GraphFullResponse)
async def get_graph_full() -> GraphFullResponse:
    """ノード + エッジ + メタデータを一括で返す。"""
    return GraphFullResponse(
        nodes=[GraphNode(**t) for t in THEOREMS],
        edges=[GraphEdge(**e) for e in EDGES],
        meta={
            "total_nodes": len(THEOREMS),
            "total_edges": len(EDGES),
            "series": SERIES,
            "structure": {
                "pure_series": ["O", "P", "A"],
                "mixed_series": ["S", "H", "K"],
                "anchor_pairs": 6,
                "bridge_pairs": 3,
                "identity_morphisms": 6,
            },
            "trigonon": {
                "description": "6定理群は完全グラフ K₃ (三角形) を形成",
                "vertices": {"O": "top", "P": "bottom-left", "A": "bottom-right"},
                "edges_between": {"S": "O↔P", "H": "O↔A", "K": "P↔A"},
            },
            "naturality": {
                "experiential": "体感 — 無意識に起きる遷移",
                "reflective": "反省 — 注意を向ければ気づく遷移",
                "structural": "構造 — 意図的に操作する遷移",
            },
        },
    )
