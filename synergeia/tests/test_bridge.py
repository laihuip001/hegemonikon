# PROOF: [L3/テスト] <- synergeia/tests/ Synergeia v2 Bridge テスト
"""
Synergeia v2 Bridge Tests
==========================

bridge.py の単体テスト (n8n 不要、mock 使用)
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from synergeia.bridge import (
    dispatch,
    dispatch_compile_only,
    health_check,
    SynergeiaResult,
    SYNERGEIA_WEBHOOK,
)


class TestSynergeiaResult:
    """SynergeiaResult dataclass のテスト"""

    def test_success_result(self):
        r = SynergeiaResult(ccl="/noe+", status="success")
        assert r.is_success
        assert r.timestamp != ""

    def test_error_result(self):
        r = SynergeiaResult(ccl="/noe+", status="error", error="fail")
        assert not r.is_success
        assert r.error == "fail"

    def test_to_dict(self):
        r = SynergeiaResult(ccl="/noe+", status="success", results=[{"a": 1}])
        d = r.to_dict()
        assert d["ccl"] == "/noe+"
        assert d["status"] == "success"
        assert len(d["results"]) == 1


class TestDispatch:
    """dispatch() のテスト"""

    @patch("synergeia.bridge.requests.post")
    def test_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "status": "success",
            "results": [{"thread": "ochema", "answer": "test"}],
            "plan": {"type": "single"},
        }
        mock_post.return_value = mock_resp

        result = dispatch("/noe+", save=False)

        assert result.is_success
        assert result.ccl == "/noe+"
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == SYNERGEIA_WEBHOOK
        payload = call_args[1]["json"]
        assert payload["ccl"] == "/noe+"

    @patch("synergeia.bridge.requests.post")
    def test_connection_error(self, mock_post):
        import requests as req
        mock_post.side_effect = req.exceptions.ConnectionError("refused")

        result = dispatch("/noe+", save=False)

        assert result.status == "error"
        assert "n8n" in result.error

    @patch("synergeia.bridge.requests.post")
    def test_timeout(self, mock_post):
        import requests as req
        mock_post.side_effect = req.exceptions.Timeout()

        result = dispatch("/noe+", timeout=5, save=False)

        assert result.status == "timeout"


class TestDispatchCompileOnly:
    """dispatch_compile_only() のテスト"""

    @patch("synergeia.bridge.requests.post")
    def test_compile_only(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {"lmql": "argmax ...", "status": "compiled"}
        mock_post.return_value = mock_resp

        result = dispatch_compile_only("/noe+")

        assert result.status == "compiled"
        payload = mock_post.call_args[1]["json"]
        assert payload["mode"] == "compile_only"


class TestHealthCheck:
    """health_check() のテスト"""

    @patch("synergeia.bridge.requests.post")
    def test_healthy(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_post.return_value = mock_resp

        result = health_check()
        assert result["status"] == "ok"

    @patch("synergeia.bridge.requests.post")
    def test_unreachable(self, mock_post):
        import requests as req
        mock_post.side_effect = req.exceptions.ConnectionError()

        result = health_check()
        assert result["status"] == "unreachable"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
