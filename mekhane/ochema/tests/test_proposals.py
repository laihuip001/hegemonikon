"""Ochēma unit tests: context_health, _select_model, archive_sessions.

LS 非接続環境でもテスト可能。AntigravityClient のメソッドを
モック経由で単体テストする。
"""

from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# テスト対象は LS 非接続でインスタンス化不可なので、
# クラスメソッドを直接テストする。
import mekhane.ochema.antigravity_client as ac


class TestSelectModel(unittest.TestCase):
    """_select_model のキーワードマッチとフォールバック。"""

    def _make_client(self):
        """LS 接続をバイパスしたモッククライアント。"""
        with patch.object(ac.AntigravityClient, "__init__", lambda self, **kw: None):
            client = ac.AntigravityClient()
            client.workspace = "test"
            client.ls = ac.LSInfo(port=9999, csrf="test")
            client._ssl_ctx = None
            return client

    def test_default_model(self):
        """キーワードなし → デフォルト Claude Thinking。"""
        client = self._make_client()
        # quota_status をモックして Quota 100%
        client.quota_status = MagicMock(return_value={
            "models": [{"model": ac.DEFAULT_MODEL, "remaining_pct": 100}]
        })
        result = client._select_model("hello world")
        self.assertEqual(result, ac.DEFAULT_MODEL)

    def test_security_keyword(self):
        """security → Claude Thinking。"""
        client = self._make_client()
        client.quota_status = MagicMock(return_value={
            "models": [
                {"model": "MODEL_CLAUDE_4_5_SONNET_THINKING", "remaining_pct": 100},
            ]
        })
        result = client._select_model("security audit of API endpoints")
        self.assertEqual(result, "MODEL_CLAUDE_4_5_SONNET_THINKING")

    def test_simple_task_gemini_flash(self):
        """translate + quick → Gemini Flash。"""
        client = self._make_client()
        client.quota_status = MagicMock(return_value={
            "models": [
                {"model": "MODEL_PLACEHOLDER_M18", "remaining_pct": 100},
            ]
        })
        result = client._select_model("translate this quickly please")
        self.assertEqual(result, "MODEL_PLACEHOLDER_M18")

    def test_fallback_on_low_quota(self):
        """Quota 10% → フォールバック。"""
        client = self._make_client()
        client.quota_status = MagicMock(return_value={
            "models": [
                {"model": "MODEL_CLAUDE_4_5_SONNET_THINKING", "remaining_pct": 5},
                {"model": "MODEL_PLACEHOLDER_M26", "remaining_pct": 80},
            ]
        })
        result = client._select_model("review this code for security issues")
        # Thinking(5%) → M26(80%) へフォールバック
        self.assertEqual(result, "MODEL_PLACEHOLDER_M26")

    def test_quota_exception_fallback(self):
        """quota_status 例外 → キーワードマッチ結果をそのまま返す。"""
        client = self._make_client()
        client.quota_status = MagicMock(side_effect=RuntimeError("LS down"))
        result = client._select_model("analyze architecture design")
        self.assertEqual(result, "MODEL_CLAUDE_4_5_SONNET_THINKING")


class TestContextHealth(unittest.TestCase):
    """context_health のレベル判定。"""

    def _make_client(self):
        with patch.object(ac.AntigravityClient, "__init__", lambda self, **kw: None):
            client = ac.AntigravityClient()
            client.workspace = "test"
            client.ls = ac.LSInfo(port=9999, csrf="test")
            client._ssl_ctx = None
            return client

    def test_healthy(self):
        client = self._make_client()
        client.session_info = MagicMock(return_value={
            "total": 1,
            "sessions": [{
                "cascade_id": "test-1",
                "step_count": 15,
                "status": "RUNNING",
                "summary": "test session",
            }],
        })
        client.quota_status = MagicMock(return_value={"models": []})
        result = client.context_health()
        self.assertEqual(result["level"], "healthy")
        self.assertEqual(result["icon"], "🟢")
        self.assertIsNone(result["recommendation"])

    def test_warning(self):
        client = self._make_client()
        client.session_info = MagicMock(return_value={
            "total": 1,
            "sessions": [{
                "cascade_id": "test-2",
                "step_count": 42,
                "status": "RUNNING",
                "summary": "big session",
            }],
        })
        client.quota_status = MagicMock(return_value={"models": []})
        result = client.context_health()
        self.assertEqual(result["level"], "warning")
        self.assertIn("/bye", result["recommendation"])

    def test_danger(self):
        client = self._make_client()
        client.session_info = MagicMock(return_value={
            "total": 1,
            "sessions": [{
                "cascade_id": "test-3",
                "step_count": 80,
                "status": "RUNNING",
                "summary": "huge session",
            }],
        })
        client.quota_status = MagicMock(return_value={"models": []})
        result = client.context_health()
        self.assertEqual(result["level"], "danger")
        self.assertIn("Context Rot", result["message"])

    def test_low_quota_included(self):
        client = self._make_client()
        client.session_info = MagicMock(return_value={
            "total": 1,
            "sessions": [{
                "cascade_id": "test-4",
                "step_count": 10,
                "status": "RUNNING",
                "summary": "ok",
            }],
        })
        client.quota_status = MagicMock(return_value={
            "models": [
                {"label": "Claude 4.5 Sonnet", "remaining_pct": 8},
                {"label": "Gemini Pro", "remaining_pct": 90},
            ]
        })
        result = client.context_health()
        self.assertEqual(result["low_quota_models"], ["Claude 4.5 Sonnet"])


class TestArchiveSessions(unittest.TestCase):
    """archive_sessions のファイル生成。"""

    def _make_client(self):
        with patch.object(ac.AntigravityClient, "__init__", lambda self, **kw: None):
            client = ac.AntigravityClient()
            client.workspace = "test"
            client.ls = ac.LSInfo(port=9999, csrf="test")
            client._ssl_ctx = None
            return client

    def test_export_creates_file(self):
        client = self._make_client()
        client.session_info = MagicMock(return_value={
            "total": 1,
            "sessions": [{
                "cascade_id": "abc123def456",
                "modified": "2026-02-13T10:00:00",
                "step_count": 5,
            }],
        })
        client.session_read = MagicMock(return_value={
            "total_steps": 5,
            "summary": "Test session",
            "conversation": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi!", "model": "Claude"},
            ],
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            result = client.archive_sessions(output_dir=tmpdir, max_sessions=1)
            self.assertEqual(len(result["exported"]), 1)
            # ファイルが存在するか
            path = result["exported"][0]
            self.assertTrue(os.path.isfile(path))
            # 内容確認
            with open(path) as f:
                content = f.read()
            self.assertIn("# Session abc123def456", content)
            self.assertIn("Hello", content)
            self.assertIn("Hi!", content)

    def test_skip_if_already_exported(self):
        client = self._make_client()
        client.session_info = MagicMock(return_value={
            "total": 1,
            "sessions": [{
                "cascade_id": "abc123def456",
                "modified": "2026-02-13T10:00:00",
            }],
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            # 事前にファイルを作成
            filepath = os.path.join(tmpdir, "session_abc123def456_2026-02-13.md")
            with open(filepath, "w") as f:
                f.write("existing")

            result = client.archive_sessions(output_dir=tmpdir, max_sessions=1)
            self.assertEqual(len(result["exported"]), 0)
            self.assertEqual(result["skipped"], 1)


if __name__ == "__main__":
    unittest.main()
