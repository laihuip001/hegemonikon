#!/usr/bin/env python3
"""
JulesClient Unit Tests

Tests for mekhane/symploke/jules_client.py
Covers: AI-022 fixes (jitter, session tracking), retry logic, batch execution
"""

import asyncio
import pytest
import random
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mekhane.symploke.jules_client import (
    JulesClient,
    JulesSession,
    JulesResult,
    SessionState,
    RateLimitError,
    with_retry,
)


class TestWithRetry:
    """with_retry デコレータのテスト"""

    @pytest.mark.asyncio
    async def test_retry_adds_jitter(self):
        """AI-022: リトライにジッターが追加されていることを確認"""
        call_count = 0
        sleep_times = []

        async def mock_sleep(duration):
            sleep_times.append(duration)

        @with_retry(max_attempts=3, initial_delay=1.0)
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RateLimitError("Rate limited")
            return "success"

        with patch("asyncio.sleep", mock_sleep):
            result = await failing_func()

        assert result == "success"
        assert call_count == 3
        # ジッターにより待機時間は initial_delay より大きい
        assert len(sleep_times) == 2
        # 1回目: 1.0 + jitter (0-0.25), 2回目: 2.0 + jitter (0-0.5)
        assert sleep_times[0] >= 1.0 and sleep_times[0] <= 1.25
        assert sleep_times[1] >= 2.0 and sleep_times[1] <= 2.5

    @pytest.mark.asyncio
    async def test_retry_respects_max_attempts(self):
        """最大試行回数を超えると例外が発生"""
        call_count = 0

        @with_retry(max_attempts=2)
        async def always_fails():
            nonlocal call_count
            call_count += 1
            raise RateLimitError("Always fails")

        with patch("asyncio.sleep", AsyncMock()):
            with pytest.raises(RateLimitError):
                await always_fails()

        assert call_count == 2


class TestSessionState:
    """SessionState のテスト"""

    def test_from_string_known_state(self):
        """既知の状態文字列を正しくパース"""
        assert SessionState.from_string("COMPLETED") == SessionState.COMPLETED
        assert SessionState.from_string("FAILED") == SessionState.FAILED
        assert SessionState.from_string("QUEUED") == SessionState.QUEUED

    def test_from_string_unknown_state(self):
        """未知の状態は UNKNOWN を返す"""
        result = SessionState.from_string("NEW_UNKNOWN_STATE")
        assert result == SessionState.UNKNOWN


class TestJulesResult:
    """JulesResult のテスト"""

    def test_is_success_with_session(self):
        """セッションありでエラーなしは成功"""
        session = JulesSession(
            id="test-123",
            name="test",
            state=SessionState.COMPLETED,
            prompt="test",
            source="test",
        )
        result = JulesResult(session=session)
        assert result.is_success is True
        assert result.is_failed is False

    def test_is_failed_with_error(self):
        """エラーありは失敗"""
        result = JulesResult(error=Exception("test error"))
        assert result.is_success is False
        assert result.is_failed is True

    def test_is_failed_with_failed_state(self):
        """ES-018: FAILED 状態のセッションは is_success=False"""
        session = JulesSession(
            id="test-123",
            name="test",
            state=SessionState.FAILED,
            prompt="test",
            source="test",
        )
        result = JulesResult(session=session)
        assert result.is_success is False
        assert result.is_failed is True


class TestBatchExecute:
    """batch_execute のテスト (AI-022 セッション追跡)"""

    @pytest.mark.asyncio
    async def test_preserves_session_id_on_poll_failure(self):
        """AI-022: poll 失敗時も元のセッションIDを保持"""
        mock_session = JulesSession(
            id="real-session-123",
            name="test",
            state=SessionState.QUEUED,
            prompt="test",
            source="test",
        )

        with patch.object(JulesClient, "create_session", new_callable=AsyncMock) as mock_create:
            with patch.object(JulesClient, "poll_session", new_callable=AsyncMock) as mock_poll:
                mock_create.return_value = mock_session
                mock_poll.side_effect = TimeoutError("Polling timed out")

                client = JulesClient(api_key="test-key")
                client._global_semaphore = asyncio.Semaphore(1)

                tasks = [{"prompt": "test", "source": "test-source"}]
                results = await client.batch_execute(tasks)

        assert len(results) == 1
        result = results[0]
        # AI-022: 失敗しても元のセッションIDが保持される
        assert result.session.id == "real-session-123"
        assert result.session.state == SessionState.FAILED
        assert result.is_failed is True

    @pytest.mark.asyncio
    async def test_uses_error_id_when_create_fails(self):
        """create_session 失敗時は error-* ID を使用"""
        with patch.object(JulesClient, "create_session", new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = RateLimitError("Rate limited")

            client = JulesClient(api_key="test-key")
            client._global_semaphore = asyncio.Semaphore(1)

            tasks = [{"prompt": "test", "source": "test-source"}]
            results = await client.batch_execute(tasks)

        assert len(results) == 1
        result = results[0]
        # create 失敗時は error-* ID
        assert result.session.id.startswith("error-")
        assert result.is_failed is True


class TestJulesClient:
    """JulesClient 基本テスト"""

    def test_init_requires_api_key(self):
        """API キーなしで初期化するとエラー"""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="API key required"):
                JulesClient()

    def test_init_with_api_key(self):
        """API キー指定で正常初期化"""
        client = JulesClient(api_key="test-api-key")
        assert client.api_key == "test-api-key"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
