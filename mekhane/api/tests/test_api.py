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
