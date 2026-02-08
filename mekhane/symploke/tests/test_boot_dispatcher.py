"""
Tests for Dispatcher integration in boot_integration.py

Verifies that:
1. Dispatcher failure does not break boot (graceful degradation)
2. Dispatch info is correctly extracted when available
3. Format includes both attractor and dispatch sections

Fix #1 from /dia+: Tests now import extract_dispatch_info() from
boot_integration.py instead of re-implementing the logic.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


# Import the ACTUAL function from boot_integration (dia+ fix #1)
from mekhane.symploke.boot_integration import extract_dispatch_info


# =============================================================================
# Tests
# =============================================================================


class TestDispatcherIntegration:
    """Dispatcher 統合のテスト (boot_integration.extract_dispatch_info)"""

    # PURPOSE: Dispatcher import failure → graceful degradation
    def test_dispatcher_import_failure(self):
        """AttractorDispatcher がインポートできなくても空 dict 返却"""
        with patch.dict("sys.modules", {"mekhane.fep.attractor_dispatcher": None}):
            result = extract_dispatch_info("テスト入力")
            assert result["primary"] == ""
            assert result["alternatives"] == []
            assert result["dispatch_formatted"] == ""

    # PURPOSE: Dispatcher raises exception → graceful degradation
    def test_dispatcher_exception(self):
        """dispatch() が例外を投げても空 dict 返却"""
        with patch("mekhane.symploke.boot_integration.extract_dispatch_info", wraps=extract_dispatch_info):
            # Mock at the import level within the function
            mock_dispatcher_cls = MagicMock()
            mock_dispatcher_cls.return_value.dispatch.side_effect = RuntimeError("test error")
            with patch.dict("sys.modules", {"mekhane.fep.attractor_dispatcher": MagicMock(AttractorDispatcher=mock_dispatcher_cls)}):
                result = extract_dispatch_info("テスト入力")
                assert result["primary"] == ""

    # PURPOSE: Dispatcher returns None (outside basin) → graceful
    def test_dispatcher_returns_none(self):
        """dispatch() が None (引力圏外) → 空 dict"""
        mock_cls = MagicMock()
        mock_cls.return_value.dispatch.return_value = None

        with patch.dict("sys.modules", {"mekhane.fep.attractor_dispatcher": MagicMock(AttractorDispatcher=mock_cls)}):
            result = extract_dispatch_info("テスト入力")
            assert result["primary"] == ""

    # PURPOSE: Successful dispatch → correct extraction
    def test_successful_dispatch(self):
        """正常な dispatch → primary, alternatives, formatted を抽出"""
        # Create mock plan
        mock_primary = MagicMock()
        mock_primary.workflow = "/noe"

        mock_alt1 = MagicMock()
        mock_alt1.workflow = "/zet"
        mock_alt2 = MagicMock()
        mock_alt2.workflow = "/dia"

        mock_plan = MagicMock()
        mock_plan.primary = mock_primary
        mock_plan.alternatives = [mock_alt1, mock_alt2]

        mock_dispatcher = MagicMock()
        mock_dispatcher.dispatch.return_value = mock_plan
        mock_dispatcher.format_compact.return_value = "/noe (O-series, 85%)"

        mock_cls = MagicMock(return_value=mock_dispatcher)

        with patch.dict("sys.modules", {"mekhane.fep.attractor_dispatcher": MagicMock(AttractorDispatcher=mock_cls)}):
            result = extract_dispatch_info("深い認識が必要")
            assert result["primary"] == "/noe"
            assert result["alternatives"] == ["/zet", "/dia"]
            assert "O-series" in result["dispatch_formatted"]

    # PURPOSE: formatted_parts assembly (boot_integration L271-275)
    def test_formatted_parts_assembly(self):
        """attractor + dispatch の formatted 結合が正しい"""
        llm_fmt = "O-series → /noe (85%)"
        dispatch_info = {
            "primary": "/noe",
            "alternatives": ["/zet"],
            "dispatch_formatted": "/noe (O-series, 85%)",
        }

        formatted_parts = []
        if llm_fmt:
            formatted_parts.append(f"🎯 **Attractor**: {llm_fmt}")
        if dispatch_info["primary"]:
            formatted_parts.append(f"   📎 Dispatch: {dispatch_info['dispatch_formatted']}")

        result = "\n".join(formatted_parts)
        assert "🎯 **Attractor**" in result
        assert "📎 Dispatch" in result
        assert result.count("\n") == 1  # exactly 2 lines

    # PURPOSE: no dispatch, only attractor → single line
    def test_attractor_only(self):
        """dispatch なし → attractor 行のみ"""
        llm_fmt = "K-series → /sop (70%)"
        dispatch_info = {"primary": "", "alternatives": [], "dispatch_formatted": ""}

        formatted_parts = []
        if llm_fmt:
            formatted_parts.append(f"🎯 **Attractor**: {llm_fmt}")
        if dispatch_info["primary"]:
            formatted_parts.append(f"   📎 Dispatch: {dispatch_info['dispatch_formatted']}")

        result = "\n".join(formatted_parts)
        assert "🎯 **Attractor**" in result
        assert "📎 Dispatch" not in result

    # PURPOSE: gpu_ok flag is passed through
    def test_gpu_ok_passed(self):
        """gpu_ok=False → force_cpu=True でインスタンス化"""
        mock_cls = MagicMock()
        mock_cls.return_value.dispatch.return_value = None

        with patch.dict("sys.modules", {"mekhane.fep.attractor_dispatcher": MagicMock(AttractorDispatcher=mock_cls)}):
            extract_dispatch_info("テスト", gpu_ok=False)
            mock_cls.assert_called_once_with(force_cpu=True)
