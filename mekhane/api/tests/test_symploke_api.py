# PROOF: [L2/インフラ] <- mekhane/api/tests/
# PURPOSE: Symploke API エンドポイントのテスト
"""
Symploke API Tests — 知識統合層 REST API のエンドポイント検証

テスト方針:
- 各エンドポイントが 200 を返すことを確認
- レスポンス型が Pydantic モデルに準拠することを確認
- 検索の基本動作 (パラメータバリデーション) を確認
"""

import pytest
from fastapi.testclient import TestClient

from mekhane.api.server import create_app


@pytest.fixture(scope="module")
def client():
    """TestClient を生成。"""
    app = create_app()
    with TestClient(app) as c:
        yield c


# ============================================================
# Symploke Search
# ============================================================


class TestSymplokeSearch:
    """/api/symploke/search エンドポイント。"""

    def test_search_basic(self, client: TestClient):
        """GET /api/symploke/search?q=test → 200 + results"""
        r = client.get("/api/symploke/search", params={"q": "test"})
        assert r.status_code == 200
        data = r.json()
        assert "query" in data
        assert data["query"] == "test"
        assert "results" in data
        assert "total" in data
        assert "sources_searched" in data
        assert isinstance(data["results"], list)

    def test_search_with_sources_filter(self, client: TestClient):
        """GET /api/symploke/search?q=test&sources=handoff → ソースフィルタ"""
        r = client.get("/api/symploke/search", params={
            "q": "test",
            "sources": "handoff",
        })
        assert r.status_code == 200
        data = r.json()
        # results は handoff のみ (or 空)
        for item in data["results"]:
            assert item["source"] == "handoff"

    def test_search_with_k(self, client: TestClient):
        """GET /api/symploke/search?q=test&k=2 → k 制限"""
        r = client.get("/api/symploke/search", params={"q": "test", "k": 2})
        assert r.status_code == 200
        data = r.json()
        assert len(data["results"]) <= 2

    def test_search_missing_query(self, client: TestClient):
        """GET /api/symploke/search without q → 422"""
        r = client.get("/api/symploke/search")
        assert r.status_code == 422


# ============================================================
# Symploke Persona
# ============================================================


class TestSymplokePersona:
    """/api/symploke/persona エンドポイント。"""

    def test_persona_basic(self, client: TestClient):
        """GET /api/symploke/persona → 200 + persona/creator"""
        r = client.get("/api/symploke/persona")
        assert r.status_code == 200
        data = r.json()
        assert "persona" in data
        assert "creator" in data
        assert isinstance(data["persona"], dict)
        assert isinstance(data["creator"], dict)


# ============================================================
# Symploke Boot Context
# ============================================================


class TestSymplokeBootContext:
    """/api/symploke/boot-context エンドポイント。"""

    def test_boot_context_fast(self, client: TestClient):
        """GET /api/symploke/boot-context?mode=fast → 200"""
        r = client.get("/api/symploke/boot-context", params={"mode": "fast"})
        assert r.status_code == 200
        data = r.json()
        assert data["mode"] == "fast"
        assert "axes" in data
        assert "summary" in data

    def test_boot_context_standard(self, client: TestClient):
        """GET /api/symploke/boot-context → 200 (内部エラーも catch される)"""
        r = client.get("/api/symploke/boot-context")
        assert r.status_code == 200
        data = r.json()
        assert data["mode"] == "standard"
        assert "axes" in data


# ============================================================
# Symploke Stats
# ============================================================


class TestSymplokeStats:
    """/api/symploke/stats エンドポイント。"""

    def test_stats_basic(self, client: TestClient):
        """GET /api/symploke/stats → 200 + 統計情報"""
        r = client.get("/api/symploke/stats")
        assert r.status_code == 200
        data = r.json()
        assert "handoff_count" in data
        assert "sophia_index_exists" in data
        assert "kairos_index_exists" in data
        assert "persona_exists" in data
        assert isinstance(data["handoff_count"], int)
