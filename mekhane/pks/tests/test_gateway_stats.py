#!/usr/bin/env python3
"""F6c: Gateway Stats API endpoint tests."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """TestClient for the API without starting PKSEngine."""
    from mekhane.api.server import app
    return TestClient(app)


class TestGatewayStatsEndpoint:
    """GET /api/pks/gateway-stats のテスト。"""

    def test_gateway_stats_returns_200(self, client):
        """エンドポイントが 200 を返す。"""
        resp = client.get("/api/pks/gateway-stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "timestamp" in data
        assert "enabled" in data
        assert "sources" in data
        assert "total_files" in data

    def test_gateway_stats_no_directory_leak(self, client):
        """directory パスがレスポンスに含まれない (F6a)。"""
        resp = client.get("/api/pks/gateway-stats")
        data = resp.json()
        for source_name, source_data in data.get("sources", {}).items():
            assert "directory" not in source_data, (
                f"source '{source_name}' leaks 'directory' field"
            )
            assert "exists" not in source_data, (
                f"source '{source_name}' leaks 'exists' field"
            )

    def test_gateway_stats_no_total_nuggets(self, client):
        """total_nuggets フィールドが削除されている (F6b)。"""
        resp = client.get("/api/pks/gateway-stats")
        data = resp.json()
        assert "total_nuggets" not in data

    def test_gateway_stats_sources_have_count(self, client):
        """各ソースに count フィールドがある。"""
        resp = client.get("/api/pks/gateway-stats")
        data = resp.json()
        for source_name, source_data in data.get("sources", {}).items():
            assert "count" in source_data, (
                f"source '{source_name}' missing 'count' field"
            )
            assert isinstance(source_data["count"], int)

    def test_gateway_stats_total_files_matches_sum(self, client):
        """total_files が各ソースの count の合計と一致する。"""
        resp = client.get("/api/pks/gateway-stats")
        data = resp.json()
        expected_total = sum(
            s.get("count", 0)
            for s in data.get("sources", {}).values()
        )
        assert data["total_files"] == expected_total

    @patch("mekhane.api.routes.pks._get_engine")
    def test_gateway_stats_engine_unavailable(self, mock_engine, client):
        """PKSEngine 未初期化時に空レスポンスを返す。"""
        mock_engine.return_value = None
        resp = client.get("/api/pks/gateway-stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["enabled"] is False
        assert data["sources"] == {}
        assert data["total_files"] == 0

    @patch("mekhane.api.routes.pks._get_engine")
    def test_gateway_stats_engine_exception(self, mock_engine, client):
        """PKSEngine が例外を投げた場合もグレースフルに処理。"""
        engine = MagicMock()
        engine.gateway_stats.side_effect = RuntimeError("test error")
        mock_engine.return_value = engine
        resp = client.get("/api/pks/gateway-stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["enabled"] is False
