"""Tests for antigravity_client.py.

PURPOSE: LS 検出・API 呼出し・ポーリングロジックのユニットテスト。
モック使用で LS 不要（CI/LS停止時でも実行可能）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from antigravity_client import (
    AntigravityClient,
    LLMResponse,
    LSConnection,
    resolve_model,
    MODELS,
)


# -- resolve_model --


class TestResolveModel:
    def test_alias(self):
        assert resolve_model("claude-sonnet") == "MODEL_CLAUDE_4_5_SONNET_THINKING"

    def test_enum_passthrough(self):
        assert resolve_model("MODEL_GPT_4_1") == "MODEL_GPT_4_1"

    def test_fuzzy_match(self):
        assert resolve_model("gemini") == "MODEL_GEMINI_2_5_PRO"

    def test_unknown_passthrough(self):
        assert resolve_model("unknown-model") == "unknown-model"


# -- LLMResponse --


class TestLLMResponse:
    def test_str_format(self):
        r = LLMResponse(response="hello", model="MODEL_X")
        s = str(r)
        assert "hello" in s
        assert "MODEL_X" in s

    def test_str_with_thinking(self):
        r = LLMResponse(response="hello", thinking="I thought...", model="M")
        s = str(r)
        assert "[thinking]" in s

    def test_to_dict(self):
        r = LLMResponse(response="hi", model="M", cascade_id="c1", trajectory_id="t1")
        d = r.to_dict()
        assert d["response"] == "hi"
        assert d["cascade_id"] == "c1"


# -- LS Detection --


class TestDetectLS:
    PS_OUTPUT = (
        "user  12345  0.0  0.0  /path/to/language_server_linux_x64 "
        "--workspace hegemonikon --csrf_token abc123secret --random_port\n"
    )

    SS_OUTPUT = (
        "LISTEN  0  128  127.0.0.1:42837  0.0.0.0:*  users:((\"ls\",pid=12345,fd=3))\n"
        "LISTEN  0  128  127.0.0.1:42037  0.0.0.0:*  users:((\"ls\",pid=12345,fd=4))\n"
    )

    @patch("antigravity_client.subprocess.check_output")
    def test_get_ports(self, mock_check):
        mock_check.return_value = self.SS_OUTPUT
        client = AntigravityClient()
        ports = client._get_ports(12345)
        assert 42837 in ports
        assert 42037 in ports

    def test_get_csrf_from_cmdline(self, tmp_path):
        # Create a fake cmdline file
        cmdline = b"language_server\x00--csrf_token\x00testtoken123\x00--random_port\x00"
        cmdline_file = tmp_path / "cmdline"
        cmdline_file.write_bytes(cmdline)

        client = AntigravityClient()
        with patch.object(client, "_get_csrf_from_cmdline") as mock_csrf:
            mock_csrf.return_value = "testtoken123"
            assert mock_csrf(12345) == "testtoken123"

    def test_get_csrf_combined_form(self):
        """Test --csrf_token=VALUE format."""
        client = AntigravityClient()
        cmdline = b"server\x00--csrf_token=abc123\x00--other\x00"
        with patch("builtins.open", mock_open(read_data=cmdline)):
            result = client._get_csrf_from_cmdline(99999)
            assert result == "abc123"


# -- API Calls --


class TestAPICalls:
    def _make_client(self) -> AntigravityClient:
        client = AntigravityClient()
        client._conn = LSConnection(pid=12345, csrf_token="test_csrf", port=42837)
        return client

    @patch("antigravity_client.urllib.request.urlopen")
    def test_start_cascade(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"cascadeId": "cascade-123"}).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        client = self._make_client()
        cid = client.start_cascade()
        assert cid == "cascade-123"

    @patch("antigravity_client.urllib.request.urlopen")
    def test_send_message(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"{}"
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        client = self._make_client()
        result = client.send_message("c1", "hello", "MODEL_X")
        assert result == {}

        # Verify request payload structure
        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        assert "SendUserCascadeMessage" in req.full_url
        body = json.loads(req.data)
        assert body["cascadeId"] == "c1"
        assert body["items"][0]["text"] == "hello"
        assert body["cascadeConfig"]["plannerConfig"]["planModel"] == "MODEL_X"

    @patch("antigravity_client.urllib.request.urlopen")
    def test_get_trajectory(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "trajectorySummaries": {
                "c1": {"trajectoryId": "traj-456", "summary": "test"}
            }
        }).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        client = self._make_client()
        tid = client.get_trajectory("c1")
        assert tid == "traj-456"

    @patch("antigravity_client.urllib.request.urlopen")
    def test_get_trajectory_not_found(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "trajectorySummaries": {}
        }).encode()
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        client = self._make_client()
        with pytest.raises(RuntimeError, match="No trajectory found"):
            client.get_trajectory("nonexistent")


# -- Polling / ask() --


class TestAsk:
    def _make_client(self) -> AntigravityClient:
        client = AntigravityClient()
        client._conn = LSConnection(pid=12345, csrf_token="test_csrf", port=42837)
        return client

    @patch("antigravity_client.time.sleep")
    @patch("antigravity_client.urllib.request.urlopen")
    def test_ask_immediate_response(self, mock_urlopen, mock_sleep):
        """Test ask() when LLM responds immediately."""
        responses = [
            # start_cascade
            json.dumps({"cascadeId": "c1"}).encode(),
            # send_message
            b"{}",
            # get_trajectory
            json.dumps({
                "trajectorySummaries": {
                    "c1": {"trajectoryId": "t1"}
                }
            }).encode(),
            # get_steps (DONE)
            json.dumps({
                "steps": [
                    {
                        "type": "CORTEX_STEP_TYPE_PLANNER_RESPONSE",
                        "status": "CORTEX_STEP_STATUS_DONE",
                        "metadata": {
                            "generatorModel": "MODEL_CLAUDE_4_5_SONNET_THINKING",
                        },
                        "plannerResponse": {
                            "response": "hello world",
                            "thinking": "The user asked...",
                        },
                    }
                ],
            }).encode(),
        ]

        call_idx = [0]

        def urlopen_side_effect(*args, **kwargs):
            mock_resp = MagicMock()
            mock_resp.read.return_value = responses[call_idx[0]]
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            call_idx[0] += 1
            return mock_resp

        mock_urlopen.side_effect = urlopen_side_effect

        client = self._make_client()
        result = client.ask("Say hello", timeout=10, poll_interval=0.01)

        assert result.response == "hello world"
        assert result.thinking == "The user asked..."
        assert result.model == "MODEL_CLAUDE_4_5_SONNET_THINKING"
        assert result.cascade_id == "c1"

    @patch("antigravity_client.time.sleep")
    @patch("antigravity_client.urllib.request.urlopen")
    def test_ask_polling_wait(self, mock_urlopen, mock_sleep):
        """Test ask() with polling (trajectory not ready on first try)."""
        responses = [
            # start_cascade
            json.dumps({"cascadeId": "c1"}).encode(),
            # send_message
            b"{}",
            # get_trajectory (first try - empty)
            json.dumps({"trajectorySummaries": {}}).encode(),
            # get_trajectory (second try - found)
            json.dumps({
                "trajectorySummaries": {
                    "c1": {"trajectoryId": "t1"}
                }
            }).encode(),
            # get_steps (DONE)
            json.dumps({
                "steps": [
                    {
                        "type": "CORTEX_STEP_TYPE_PLANNER_RESPONSE",
                        "status": "CORTEX_STEP_STATUS_DONE",
                        "metadata": {
                            "generatorModel": "MODEL_X",
                        },
                        "plannerResponse": {
                            "response": "result",
                        },
                    }
                ],
            }).encode(),
        ]

        call_idx = [0]

        def urlopen_side_effect(*args, **kwargs):
            mock_resp = MagicMock()
            mock_resp.read.return_value = responses[call_idx[0]]
            mock_resp.__enter__ = MagicMock(return_value=mock_resp)
            mock_resp.__exit__ = MagicMock(return_value=False)
            call_idx[0] += 1
            return mock_resp

        mock_urlopen.side_effect = urlopen_side_effect

        client = self._make_client()
        result = client.ask("test", timeout=10, poll_interval=0.01)
        assert result.response == "result"


# -- Parse Response --


class TestParseResponse:
    def test_parse_planner_response(self):
        """Test parsing with actual API structure: status at step level, model in metadata."""
        client = AntigravityClient()
        steps_result = {
            "steps": [
                {"type": "CORTEX_STEP_TYPE_USER_INPUT", "status": "CORTEX_STEP_STATUS_DONE"},
                {
                    "type": "CORTEX_STEP_TYPE_PLANNER_RESPONSE",
                    "status": "CORTEX_STEP_STATUS_DONE",
                    "metadata": {
                        "generatorModel": "MODEL_X",
                    },
                    "plannerResponse": {
                        "response": "hello",
                        "modifiedResponse": "hello",
                        "thinking": "thought",
                    },
                },
                {"type": "CORTEX_STEP_TYPE_CHECKPOINT", "status": "CORTEX_STEP_STATUS_DONE"},
            ],
        }
        resp = client._parse_response(steps_result, "c1", "t1")
        assert resp.response == "hello"
        assert resp.thinking == "thought"
        assert resp.model == "MODEL_X"
        assert resp.status == "CORTEX_STEP_STATUS_DONE"

    def test_parse_no_planner_response(self):
        client = AntigravityClient()
        steps_result = {
            "steps": [
                {"type": "CORTEX_STEP_TYPE_USER_INPUT", "status": "CORTEX_STEP_STATUS_DONE"},
            ],
        }
        resp = client._parse_response(steps_result, "c1", "t1")
        assert resp.response == ""
        assert resp.status == ""
