# PROOF: [L3/テスト] <- synergeia/tests/ Synergeia v2 Bridge テスト
"""
Synergeia v2 Bridge Tests
==========================

bridge.py の単体テスト (n8n 不要、mock 使用)

v2: 2段階アーキテクチャ対応
  Stage 1: n8n CCL ルーター (mock)
  Stage 2: バックエンド実行 (mock)
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
    """dispatch() のテスト — 2段階アーキテクチャ"""

    @patch("synergeia.bridge._execute_thread")
    @patch("synergeia.bridge.requests.post")
    def test_success_with_execution(self, mock_post, mock_exec):
        """Stage 1 (n8n routing) + Stage 2 (backend execution)"""
        # Stage 1: n8n returns routing info
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "status": "routed",
            "ccl": "/noe+",
            "tasks": [{"ccl": "/noe+", "thread": "ochema", "prefix": "/noe"}],
            "plan": {"type": "single", "elements": ["/noe+"]},
        }
        mock_post.return_value = mock_resp

        # Stage 2: backend returns result
        mock_exec.return_value = {
            "thread": "ochema",
            "ccl": "/noe+",
            "status": "success",
            "answer": "test answer",
        }

        result = dispatch("/noe+", save=False)

        assert result.is_success
        assert result.ccl == "/noe+"
        mock_post.assert_called_once()
        mock_exec.assert_called_once_with("ochema", "/noe+", "", 120)

    @patch("synergeia.bridge.requests.post")
    def test_routing_only(self, mock_post):
        """execute=False でルーティングのみ"""
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = {
            "status": "routed",
            "tasks": [{"ccl": "/noe+", "thread": "ochema"}],
            "plan": {"type": "single"},
        }
        mock_post.return_value = mock_resp

        result = dispatch("/noe+", save=False, execute=False)

        assert result.status == "routed"

    @patch("synergeia.bridge._local_fallback")
    @patch("synergeia.bridge.requests.post")
    def test_connection_error_fallback(self, mock_post, mock_fallback):
        """n8n 不通時 → ローカルフォールバック"""
        import requests as req
        mock_post.side_effect = req.exceptions.ConnectionError("refused")
        mock_fallback.return_value = SynergeiaResult(
            ccl="/noe+",
            status="error",
            error="Local fallback failed",
        )

        result = dispatch("/noe+", save=False)

        mock_fallback.assert_called_once()
        assert result.status == "error"

    @patch("synergeia.bridge.requests.post")
    def test_timeout(self, mock_post):
        import requests as req
        mock_post.side_effect = req.exceptions.Timeout()

        result = dispatch("/noe+", timeout=5, save=False)

        assert result.status == "timeout"


class TestThreadExecution:
    """Stage 2: スレッド実行のテスト"""

    @patch("synergeia.bridge._exec_hermeneus")
    def test_hermeneus_thread(self, mock_herm):
        from synergeia.bridge import _execute_thread
        mock_herm.return_value = {"thread": "hermeneus", "status": "success"}

        result = _execute_thread("hermeneus", "/test", "", 30)

        assert result["thread"] == "hermeneus"
        mock_herm.assert_called_once()

    def test_jules_deferred(self):
        from synergeia.bridge import _exec_jules

        result = _exec_jules("/mek+", "context")

        assert result["thread"] == "jules"
        assert result["status"] == "deferred"


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
