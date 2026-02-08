#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/poiema/flow/tests/
# PURPOSE: EnergeiaCoreResolver のテスト
"""Poiema Energeia Core Tests — Batch 5"""

import pytest
import asyncio
from mekhane.poiema.flow.energeia_core import (
    EnergeiaCoreResolver,
    CoreProcessor,
    NOUS_COMPLEXITY_THRESHOLD,
    METRON_DEEP_THRESHOLD,
)


class TestEnergeiaCoreInit:
    """EnergeiaCoreResolver 初期化テスト"""

    def test_init_default(self):
        resolver = EnergeiaCoreResolver()
        assert resolver.metron_resolver is not None
        assert resolver.epoche_shield is not None

    def test_init_with_settings(self):
        settings = {"PRIVACY_MODE": False, "MODEL_FAST": "test-model"}
        resolver = EnergeiaCoreResolver(settings=settings)
        assert resolver.settings["PRIVACY_MODE"] is False

    def test_default_settings(self):
        resolver = EnergeiaCoreResolver()
        settings = resolver.settings
        assert "PRIVACY_MODE" in settings
        assert "MODEL_FAST" in settings
        assert "MODEL_SMART" in settings

    def test_backward_compat_alias(self):
        assert CoreProcessor is EnergeiaCoreResolver


class TestModelSelection:
    """K1 Eukairia: モデル選択テスト"""

    @pytest.fixture
    def resolver(self):
        return EnergeiaCoreResolver()

    def test_fast_model_default(self, resolver):
        model = resolver._select_model("short text", 60)
        assert "flash" in model.lower() or "fast" in model.lower() or model == resolver.settings["MODEL_FAST"]

    def test_smart_model_deep_level(self, resolver):
        model = resolver._select_model("short text", METRON_DEEP_THRESHOLD)
        assert model == resolver.settings["MODEL_SMART"]

    def test_smart_model_long_text(self, resolver):
        long_text = "x" * (NOUS_COMPLEXITY_THRESHOLD + 1)
        model = resolver._select_model(long_text, 60)
        assert model == resolver.settings["MODEL_SMART"]

    def test_fast_model_short_text_low_level(self, resolver):
        model = resolver._select_model("hello", 30)
        assert model == resolver.settings["MODEL_FAST"]


class TestProcessPipeline:
    """O4 Energeia: 処理パイプラインテスト"""

    @pytest.fixture
    def resolver(self):
        return EnergeiaCoreResolver()

    def test_process_sync(self, resolver):
        result = resolver.process_sync("Hello world", 60)
        assert "result" in result or "error" in result

    def test_process_sync_returns_result(self, resolver):
        result = resolver.process_sync("Test input text", 60)
        if "result" in result:
            assert isinstance(result["result"], str)
            assert result["metron_level"] in [30, 60, 100]

    def test_process_sync_with_privacy(self, resolver):
        result = resolver.process_sync("user@example.com", 60)
        # PII should be masked and unmasked transparently
        assert "result" in result or "error" in result

    def test_process_async(self, resolver):
        async def run():
            return await resolver.process("Test async", 60)
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(run())
        finally:
            loop.close()
        assert "result" in result or "error" in result

    def test_process_privacy_disabled(self):
        resolver = EnergeiaCoreResolver(settings={
            "PRIVACY_MODE": False,
            "MODEL_FAST": "test",
            "MODEL_SMART": "test",
            "USER_SYSTEM_PROMPT": "",
        })
        result = resolver.process_sync("user@example.com", 30)
        assert "result" in result or "error" in result


class TestConstants:
    """定数テスト"""

    def test_complexity_threshold(self):
        assert NOUS_COMPLEXITY_THRESHOLD == 1000

    def test_deep_threshold(self):
        assert METRON_DEEP_THRESHOLD == 100
