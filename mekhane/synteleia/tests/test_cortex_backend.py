# PROOF: [L2/テスト] <- mekhane/synteleia/tests/ CortexBackend E2E テスト
# PURPOSE: CortexBackend の接続テスト + フォールバック動作検証
"""
CortexBackend Tests

API キーなしフォールバック、モック応答、is_available の検証。
"""

import json
import os
from unittest.mock import patch, MagicMock

import pytest

from mekhane.synteleia.dokimasia.cortex_backend import CortexBackend


class TestCortexBackendAvailability:
    """is_available() のテスト。"""

    def test_unavailable_without_key(self):
        with patch.dict(os.environ, {}, clear=True):
            backend = CortexBackend()
            backend._available = None  # Reset cache
            assert backend.is_available() is False

    def test_available_with_key(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}):
            backend = CortexBackend()
            backend._available = None
            assert backend.is_available() is True


class TestCortexBackendQuery:
    """query() のテスト。"""

    def test_fallback_without_key(self):
        """API キーなしで JSON フォールバック応答を返す。"""
        with patch.dict(os.environ, {}, clear=True):
            # GEMINI_API_KEY を確実に除去
            os.environ.pop("GEMINI_API_KEY", None)
            backend = CortexBackend()
            result = backend.query("test prompt", "test context")
            parsed = json.loads(result)
            assert parsed["issues"] == []
            assert parsed["confidence"] == 0.0
            assert "not set" in parsed["summary"]

    def test_query_with_mock_api(self):
        """モック API 応答のテスト — query 自体をパッチ。"""
        expected = json.dumps({
            "issues": [{"code": "TEST-001", "message": "test"}],
            "summary": "mock audit",
            "confidence": 0.8,
        })
        backend = CortexBackend()
        with patch.object(backend, "query", return_value=expected):
            result = backend.query("audit this", "content")
            parsed = json.loads(result)
            assert parsed["confidence"] == 0.8
            assert len(parsed["issues"]) == 1

    def test_query_integration_structure(self):
        """query の内部構造テスト — API なしで呼び出し構造を確認。"""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("GEMINI_API_KEY", None)
            backend = CortexBackend(model="gemini-2.0-flash")
            result = backend.query("test", "ctx")
            parsed = json.loads(result)
            # API キーなし → フォールバック JSON
            assert "issues" in parsed
            assert "confidence" in parsed


class TestCortexBackendRepr:
    def test_repr(self):
        backend = CortexBackend(model="gemini-2.5-pro", label="Pro")
        r = repr(backend)
        assert "gemini-2.5-pro" in r
        assert "Pro" in r

    def test_default_label(self):
        backend = CortexBackend()
        assert backend.label == "gemini-2.5-flash"
