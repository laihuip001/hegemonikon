#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/api/tests/
# PURPOSE: Synteleia REST API エンドポイントのテスト
"""Synteleia API Tests"""

import pytest
from fastapi.testclient import TestClient
from mekhane.api.server import create_app


@pytest.fixture(scope="module")
def client():
    """テスト用 FastAPI クライアント。"""
    app = create_app()
    return TestClient(app)


# ── POST /api/synteleia/audit ────────────────────────


class TestSynteleiaAudit:
    """/api/synteleia/audit エンドポイント。"""

    def test_audit_simple_code(self, client: TestClient):
        """POST /api/synteleia/audit — 正常コード → 200"""
        r = client.post(
            "/api/synteleia/audit",
            json={"content": "def hello():\n    return 'world'", "target_type": "code"},
        )
        assert r.status_code == 200
        data = r.json()
        assert "passed" in data
        assert "summary" in data
        assert "agent_results" in data
        assert "report" in data
        assert isinstance(data["agent_results"], list)
        assert len(data["agent_results"]) == 8  # 3 poiesis + 5 dokimasia

    def test_audit_vague_content(self, client: TestClient):
        """POST /api/synteleia/audit — 曖昧テキスト → issues 検出"""
        r = client.post(
            "/api/synteleia/audit",
            json={
                "content": "これをそれに変換して、あれを使って etc.",
                "target_type": "plan",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["total_issues"] > 0  # OusiaAgent が曖昧語を検出するはず

    def test_audit_with_source(self, client: TestClient):
        """POST /api/synteleia/audit — source パラメータ付き"""
        r = client.post(
            "/api/synteleia/audit",
            json={
                "content": "class Foo:\n    pass",
                "target_type": "code",
                "source": "test.py",
            },
        )
        assert r.status_code == 200

    def test_audit_unknown_target_type(self, client: TestClient):
        """POST /api/synteleia/audit — 不明な target_type → generic にフォールバック"""
        r = client.post(
            "/api/synteleia/audit",
            json={"content": "test content", "target_type": "unknown_type"},
        )
        assert r.status_code == 200

    def test_audit_empty_content(self, client: TestClient):
        """POST /api/synteleia/audit — 空コンテンツ → 422"""
        r = client.post(
            "/api/synteleia/audit",
            json={"content": "", "target_type": "code"},
        )
        assert r.status_code == 422  # Pydantic validation (min_length=1)

    def test_audit_response_structure(self, client: TestClient):
        """レスポンス構造の検証。"""
        r = client.post(
            "/api/synteleia/audit",
            json={"content": "x = 1", "target_type": "code"},
        )
        data = r.json()
        assert "passed" in data
        assert "summary" in data
        assert "critical_count" in data
        assert "high_count" in data
        assert "total_issues" in data
        assert "agent_results" in data
        assert "report" in data

        # agent_results の各要素を検証
        for ar in data["agent_results"]:
            assert "agent_name" in ar
            assert "passed" in ar
            assert "confidence" in ar
            assert "issues" in ar


# ── POST /api/synteleia/audit-quick ──────────────────


class TestSynteleiaAuditQuick:
    """/api/synteleia/audit-quick エンドポイント。"""

    def test_quick_audit(self, client: TestClient):
        """POST /api/synteleia/audit-quick → LogicAgent のみ"""
        r = client.post(
            "/api/synteleia/audit-quick",
            json={"content": "if True:\n    pass", "target_type": "code"},
        )
        assert r.status_code == 200
        data = r.json()
        assert len(data["agent_results"]) == 1
        assert data["agent_results"][0]["agent_name"] == "LogicAgent"

    def test_quick_audit_contradiction(self, client: TestClient):
        """POST /api/synteleia/audit-quick — 矛盾テキスト"""
        r = client.post(
            "/api/synteleia/audit-quick",
            json={
                "content": "この設定は必須です。ただしこの設定は任意です。",
                "target_type": "plan",
            },
        )
        assert r.status_code == 200
        data = r.json()
        assert data["total_issues"] > 0


# ── GET /api/synteleia/agents ────────────────────────


class TestSynteleiaAgents:
    """/api/synteleia/agents エンドポイント。"""

    def test_list_agents(self, client: TestClient):
        """GET /api/synteleia/agents → 8 エージェント"""
        r = client.get("/api/synteleia/agents")
        assert r.status_code == 200
        agents = r.json()
        assert len(agents) == 8

        # レイヤー分布の検証
        poiesis = [a for a in agents if a["layer"] == "poiesis"]
        dokimasia = [a for a in agents if a["layer"] == "dokimasia"]
        assert len(poiesis) == 3
        assert len(dokimasia) == 5

    def test_agent_structure(self, client: TestClient):
        """エージェント情報の構造検証。"""
        r = client.get("/api/synteleia/agents")
        agents = r.json()
        for agent in agents:
            assert "name" in agent
            assert "description" in agent
            assert "layer" in agent
            assert agent["layer"] in ("poiesis", "dokimasia")
