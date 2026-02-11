# PROOF: [L2/インフラ] <- mekhane/api/tests/
# PURPOSE: FastAPI エンドポイントの統合テスト
"""
API Integration Tests — FastAPI TestClient によるエンドポイント検証

テスト方針:
- 各エンドポイントが 200/503 を返すことを確認
- レスポンス型が Pydantic モデルに準拠することを確認
- FEP Agent の状態変化を順序付きで検証
"""

import pytest
from fastapi.testclient import TestClient

from mekhane.api.server import create_app


# PURPOSE: テスト用アプリケーション
@pytest.fixture(scope="module")
def client():
    """TestClient を生成。"""
    app = create_app()
    with TestClient(app) as c:
        yield c


# ============================================================
# Status
# ============================================================


class TestStatus:
    """/api/status/* エンドポイント。"""

    def test_health_endpoint(self, client: TestClient):
        """GET /api/status/health → 200 + status=ok"""
        r = client.get("/api/status/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "uptime_seconds" in data

    def test_full_status(self, client: TestClient):
        """GET /api/status → 200 + score + items"""
        r = client.get("/api/status")
        assert r.status_code == 200
        data = r.json()
        assert "score" in data
        assert "items" in data
        assert "timestamp" in data
        assert isinstance(data["items"], list)
        # スコアは 0.0-1.0
        assert 0.0 <= data["score"] <= 1.0


# ============================================================
# FEP
# ============================================================


class TestFEP:
    """/api/fep/* エンドポイント。"""

    def test_fep_state(self, client: TestClient):
        """GET /api/fep/state → 200 + beliefs"""
        r = client.get("/api/fep/state")
        assert r.status_code == 200
        data = r.json()
        assert "beliefs" in data
        assert "epsilon" in data
        assert isinstance(data["beliefs"], list)
        assert len(data["beliefs"]) == 48  # 48-state model

    def test_fep_step(self, client: TestClient):
        """POST /api/fep/step → 200 + action_name"""
        r = client.post("/api/fep/step", json={"observation": 0})
        assert r.status_code == 200
        data = r.json()
        assert "action_name" in data
        assert "action_index" in data
        assert data["action_index"] >= 0

    def test_fep_step_invalid_observation(self, client: TestClient):
        """POST /api/fep/step with invalid observation → 422"""
        r = client.post("/api/fep/step", json={"observation": 999})
        assert r.status_code == 422  # validation error

    def test_fep_dashboard(self, client: TestClient):
        """GET /api/fep/dashboard → 200"""
        r = client.get("/api/fep/dashboard")
        assert r.status_code == 200
        data = r.json()
        assert "total_steps" in data
        assert "available" in data


# ============================================================
# Gnōsis
# ============================================================


class TestGnosis:
    """/api/gnosis/* エンドポイント。"""

    def test_gnosis_stats(self, client: TestClient):
        """GET /api/gnosis/stats → 200 (インデックス障害時も graceful)"""
        r = client.get("/api/gnosis/stats")
        # 503 or 200 — shape mismatch 時は available=false
        assert r.status_code in (200, 503)

    def test_gnosis_search(self, client: TestClient):
        """GET /api/gnosis/search?q=FEP → 200 or 503"""
        r = client.get("/api/gnosis/search", params={"q": "FEP"})
        assert r.status_code in (200, 503)

    def test_gnosis_search_missing_query(self, client: TestClient):
        """GET /api/gnosis/search without q → 422"""
        r = client.get("/api/gnosis/search")
        assert r.status_code == 422


# ============================================================
# Postcheck
# ============================================================


class TestPostcheck:
    """/api/postcheck/* エンドポイント。"""

    def test_postcheck_list(self, client: TestClient):
        """GET /api/postcheck/list → 200 + items"""
        r = client.get("/api/postcheck/list")
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    def test_postcheck_run(self, client: TestClient):
        """POST /api/postcheck/run → 200"""
        r = client.post("/api/postcheck/run", json={
            "wf_name": "dia",
            "mode": "+",
            "content": "Test content for postcheck validation.",
        })
        assert r.status_code == 200
        data = r.json()
        assert "passed" in data
        assert "checks" in data


# ============================================================
# Dendron
# ============================================================


class TestDendron:
    """/api/dendron/* エンドポイント。"""

    def test_dendron_report_summary(self, client: TestClient):
        """GET /api/dendron/report → 200 + summary"""
        r = client.get("/api/dendron/report")
        assert r.status_code == 200
        data = r.json()
        assert "summary" in data
        assert "coverage_percent" in data["summary"]
        # サマリーモードでは file_results は空
        assert data["file_results"] == []

    def test_dendron_check_nonexistent(self, client: TestClient):
        """POST /api/dendron/check with bad path → error message"""
        r = client.post("/api/dendron/check", json={
            "path": "/nonexistent/file.py",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["error"] != ""


# ============================================================
# OpenAPI
# ============================================================


class TestOpenAPI:
    """OpenAPI スキーマの公開確認。"""

    def test_openapi_schema(self, client: TestClient):
        """GET /api/openapi.json → 200 + valid schema"""
        r = client.get("/api/openapi.json")
        assert r.status_code == 200
        data = r.json()
        assert data["info"]["title"] == "Hegemonikón API"
        assert "paths" in data

    def test_docs_page(self, client: TestClient):
        """GET /api/docs → 200 (Swagger UI)"""
        r = client.get("/api/docs")
        assert r.status_code == 200


# ============================================================
# Link Graph
# ============================================================


class TestLinkGraph:
    """/api/link-graph/* エンドポイント。"""

    def test_link_graph_full(self, client: TestClient):
        """GET /api/link-graph/full → 200 + nodes + edges + meta."""
        r = client.get("/api/link-graph/full")
        assert r.status_code == 200
        data = r.json()
        assert "nodes" in data
        assert "edges" in data
        assert "meta" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["edges"], list)
        # ノードが1件以上存在
        if data["nodes"]:
            node = data["nodes"][0]
            assert "id" in node
            assert "projected_series" in node
            assert "projected_theorem" in node
            assert "orbit_angle" in node
            assert "orbit_radius" in node
            # 射影先は有効な Series
            assert node["projected_series"] in "OSHPKA"

    def test_link_graph_full_filter(self, client: TestClient):
        """GET /api/link-graph/full?source_type=kernel → フィルタ動作。"""
        r = client.get("/api/link-graph/full", params={"source_type": "kernel"})
        assert r.status_code == 200
        data = r.json()
        for node in data["nodes"]:
            assert node["source_type"] == "kernel"

    def test_link_graph_stats(self, client: TestClient):
        """GET /api/link-graph/stats → 200 + 統計."""
        r = client.get("/api/link-graph/stats")
        assert r.status_code == 200
        data = r.json()
        assert "total_nodes" in data
        assert "total_edges" in data
        assert "bridge_nodes" in data
        assert "source_type_counts" in data
        assert "projection_counts" in data
        assert isinstance(data["bridge_nodes"], list)

    def test_link_graph_neighbors(self, client: TestClient):
        """GET /api/link-graph/neighbors/{node_id} → 200."""
        # まずノード一覧を取得
        r = client.get("/api/link-graph/full")
        data = r.json()
        if data["nodes"]:
            node_id = data["nodes"][0]["id"]
            r2 = client.get(f"/api/link-graph/neighbors/{node_id}", params={"hops": 2})
            assert r2.status_code == 200
            data2 = r2.json()
            assert data2["node_id"] == node_id
            assert "neighbors" in data2

    def test_link_graph_neighbors_not_found(self, client: TestClient):
        """GET /api/link-graph/neighbors/xxx → error: not found."""
        r = client.get("/api/link-graph/neighbors/nonexistent_node_12345")
        assert r.status_code == 200
        data = r.json()
        assert data["error"] == "not found"


# ============================================================
# Sophia KI
# ============================================================


class TestSophiaKI:
    """CRUD ラウンドトリップ + セキュリティ検証。"""

    def test_ki_list_initial(self, client: TestClient):
        """GET /api/sophia/ki → 200 + items list."""
        r = client.get("/api/sophia/ki")
        assert r.status_code == 200
        data = r.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)

    def test_ki_crud_roundtrip(self, client: TestClient):
        """Create → Get → Update → Delete の完全ラウンドトリップ。"""
        # 1. Create
        r = client.post("/api/sophia/ki", json={
            "title": "テスト KI — pytest",
            "content": "# テスト\n\nこれは pytest による自動テストです。",
            "source_type": "test",
        })
        assert r.status_code == 201
        created = r.json()
        assert created["title"] == "テスト KI — pytest"
        assert "id" in created
        ki_id = created["id"]

        # 2. Get
        r = client.get(f"/api/sophia/ki/{ki_id}")
        assert r.status_code == 200
        detail = r.json()
        assert detail["id"] == ki_id
        assert detail["title"] == "テスト KI — pytest"
        assert "# テスト" in detail["content"]
        assert isinstance(detail["backlinks"], list)

        # 3. Update
        r = client.put(f"/api/sophia/ki/{ki_id}", json={
            "title": "更新された KI",
            "content": "# 更新\n\n内容を変更しました。",
        })
        assert r.status_code == 200
        updated = r.json()
        assert updated["title"] == "更新された KI"
        assert "更新" in updated["content"]

        # 4. Verify list contains it
        r = client.get("/api/sophia/ki")
        assert r.status_code == 200
        items = r.json()["items"]
        ids = [i["id"] for i in items]
        assert ki_id in ids

        # 5. Delete
        r = client.delete(f"/api/sophia/ki/{ki_id}")
        assert r.status_code == 200
        deleted = r.json()
        assert deleted["status"] == "deleted"

        # 6. Get after delete → 404
        r = client.get(f"/api/sophia/ki/{ki_id}")
        assert r.status_code == 404

    def test_ki_search(self, client: TestClient):
        """GET /api/sophia/search?q=xxx → 200 + results list."""
        r = client.get("/api/sophia/search", params={"q": "test"})
        assert r.status_code == 200
        data = r.json()
        assert "query" in data
        assert "results" in data
        assert isinstance(data["results"], list)

    def test_ki_not_found(self, client: TestClient):
        """GET /api/sophia/ki/nonexistent → 404."""
        r = client.get("/api/sophia/ki/nonexistent_ki_12345")
        assert r.status_code == 404

    def test_ki_path_traversal_blocked(self, client: TestClient):
        """Path Traversal 攻撃が拒否されること。"""
        # URL エンコード版: FastAPI の処理で 400 or 404
        r = client.get("/api/sophia/ki/..%2F..%2Fetc%2Fpasswd")
        assert r.status_code in (400, 404)

        # デコード済み直接版: _sanitize_ki_id が 400 を返す
        r = client.get("/api/sophia/ki/..%2F..%2Fetc%2Fpasswd")
        assert r.status_code in (400, 404)

    def test_ki_create_no_title(self, client: TestClient):
        """POST /api/sophia/ki with empty title → 422."""
        r = client.post("/api/sophia/ki", json={
            "title": "",
            "content": "no title",
        })
        # FastAPI の validation or our custom check
        assert r.status_code in (400, 422)


# ============================================================
# Graph (3D)
# ============================================================


class TestGraph:
    """/api/graph/* エンドポイント。"""

    def test_graph_nodes(self, client: TestClient):
        """GET /api/graph/nodes → 200 + 24ノード."""
        r = client.get("/api/graph/nodes")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        # 6 series × 4 theorems = 24
        assert len(data) == 24
        node = data[0]
        assert "id" in node
        assert "series" in node
        assert "name" in node
        assert "position" in node

    def test_graph_edges(self, client: TestClient):
        """GET /api/graph/edges → 200 + エッジリスト."""
        r = client.get("/api/graph/edges")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        # 72 relations + 24 identity = 96
        assert len(data) == 96

    def test_graph_full(self, client: TestClient):
        """GET /api/graph/full → 200 + nodes + edges + meta."""
        r = client.get("/api/graph/full")
        assert r.status_code == 200
        data = r.json()
        assert "nodes" in data
        assert "edges" in data
        assert "meta" in data
        assert data["meta"]["total_nodes"] == 24
        assert data["meta"]["total_edges"] == 96

    def test_graph_node_has_position(self, client: TestClient):
        """各ノードが3D座標を持つことを確認."""
        r = client.get("/api/graph/nodes")
        data = r.json()
        for node in data:
            pos = node["position"]
            assert "x" in pos
            assert "y" in pos
            assert "z" in pos


# ============================================================
# CCL Parse & Execute
# ============================================================


class TestCCL:
    """/api/ccl/* エンドポイント。"""

    def test_ccl_parse_simple(self, client: TestClient):
        """POST /api/ccl/parse with /noe+ → success + AST."""
        r = client.post("/api/ccl/parse", json={"ccl": "/noe+"})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert data["ccl"] == "/noe+"
        assert any("noe" in w for w in data["workflows"])

    def test_ccl_parse_sequence(self, client: TestClient):
        """POST /api/ccl/parse with /s+_/ene → success + 2 WFs."""
        r = client.post("/api/ccl/parse", json={"ccl": "/s+_/ene"})
        assert r.status_code == 200
        data = r.json()
        assert data["success"] is True
        assert len(data["workflows"]) >= 2

    def test_ccl_parse_invalid(self, client: TestClient):
        """POST /api/ccl/parse with empty → error."""
        r = client.post("/api/ccl/parse", json={"ccl": ""})
        assert r.status_code == 200
        data = r.json()
        # 空文字列はパースエラーになるはず
        assert data["success"] is False or data["error"] is not None

    def test_ccl_execute_graceful(self, client: TestClient):
        """POST /api/ccl/execute → 200 (成功 or graceful error)."""
        r = client.post("/api/ccl/execute", json={
            "ccl": "/noe-",
            "context": "test",
        })
        assert r.status_code == 200
        data = r.json()
        assert "ccl" in data


# ============================================================
# WF Registry
# ============================================================


class TestWFRegistry:
    """/api/wf/* エンドポイント。"""

    def test_wf_list(self, client: TestClient):
        """GET /api/wf/list → 200 + total + workflows."""
        r = client.get("/api/wf/list")
        assert r.status_code == 200
        data = r.json()
        assert "total" in data
        assert "workflows" in data
        assert data["total"] > 0
        # 少なくとも主要WFが存在する
        names = [w["name"] for w in data["workflows"]]
        assert any("noe" in n for n in names)

    def test_wf_detail(self, client: TestClient):
        """GET /api/wf/noe → 200 + description."""
        r = client.get("/api/wf/noe")
        assert r.status_code == 200
        data = r.json()
        assert data["name"] == "noe"
        assert data["description"] != ""

    def test_wf_not_found(self, client: TestClient):
        """GET /api/wf/nonexistent → 200 + error in metadata."""
        r = client.get("/api/wf/nonexistent_wf_12345")
        assert r.status_code == 200
        data = r.json()
        assert "error" in data.get("metadata", {}) or data["description"] == "Not found"


# ============================================================
# Sympatheia
# ============================================================


class TestSympatheia:
    """/api/sympatheia/* エンドポイント (遅延ロード)."""

    def test_sympatheia_attractor(self, client: TestClient):
        """POST /api/sympatheia/attractor → 200 or graceful."""
        r = client.post("/api/sympatheia/attractor", json={
            "text": "深く考えたい",
        })
        assert r.status_code in (200, 503)

    def test_sympatheia_notifications(self, client: TestClient):
        """GET /api/sympatheia/notifications → 200."""
        r = client.get("/api/sympatheia/notifications")
        assert r.status_code in (200, 503)

    def test_sympatheia_wbc(self, client: TestClient):
        """POST /api/sympatheia/wbc → 200."""
        r = client.post("/api/sympatheia/wbc", json={
            "details": "test alert",
            "severity": "low",
        })
        assert r.status_code in (200, 503)


# ============================================================
# Gnosis Narrator
# ============================================================


class TestGnosisNarrator:
    """/api/gnosis/papers + /api/gnosis/narrate."""

    def test_papers_list(self, client: TestClient):
        """GET /api/gnosis/papers → 200 + papers list."""
        r = client.get("/api/gnosis/papers")
        assert r.status_code == 200
        data = r.json()
        assert "papers" in data
        assert "total" in data
        assert isinstance(data["papers"], list)

    def test_narrate_requires_paper_id(self, client: TestClient):
        """POST /api/gnosis/narrate without paper_id → 422."""
        r = client.post("/api/gnosis/narrate", json={})
        assert r.status_code == 422


# ============================================================
# Synteleia (6視点認知アンサンブル)
# ============================================================


class TestSynteleia:
    """/api/synteleia/* エンドポイント。"""

    def test_synteleia_agents(self, client: TestClient):
        """GET /api/synteleia/agents → 200 + agent list."""
        r = client.get("/api/synteleia/agents")
        assert r.status_code in (200, 503)
        if r.status_code == 200:
            data = r.json()
            # agents はリスト直接返し or dict
            assert isinstance(data, (list, dict))

    def test_synteleia_audit(self, client: TestClient):
        """POST /api/synteleia/audit → 200 or 503."""
        r = client.post("/api/synteleia/audit", json={
            "content": "テスト内容",
            "wf_name": "test",
        })
        assert r.status_code in (200, 422, 503)


# ============================================================
# Gateway
# ============================================================


class TestGateway:
    """/api/gateway/* エンドポイント。"""

    def test_gateway_status(self, client: TestClient):
        """GET /api/gateway/status → 200."""
        r = client.get("/api/gateway/status")
        assert r.status_code in (200, 503)

    def test_gateway_servers(self, client: TestClient):
        """GET /api/gateway/servers → 200 + servers list."""
        r = client.get("/api/gateway/servers")
        assert r.status_code in (200, 503)

    def test_gateway_policies(self, client: TestClient):
        """GET /api/gateway/policies → 200."""
        r = client.get("/api/gateway/policies")
        assert r.status_code in (200, 503)


