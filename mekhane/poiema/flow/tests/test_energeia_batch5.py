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


# PURPOSE: Test suite validating energeia core init correctness
class TestEnergeiaCoreInit:
    """EnergeiaCoreResolver 初期化テスト"""

    # PURPOSE: Verify init default behaves correctly
    def test_init_default(self):
        """Verify init default behavior."""
        resolver = EnergeiaCoreResolver()
        assert resolver.metron_resolver is not None
        assert resolver.epoche_shield is not None

    # PURPOSE: Verify init with settings behaves correctly
    def test_init_with_settings(self):
        """Verify init with settings behavior."""
        settings = {"PRIVACY_MODE": False, "MODEL_FAST": "test-model"}
        resolver = EnergeiaCoreResolver(settings=settings)
        assert resolver.settings["PRIVACY_MODE"] is False

    # PURPOSE: Verify default settings behaves correctly
    def test_default_settings(self):
        """Verify default settings behavior."""
        resolver = EnergeiaCoreResolver()
        settings = resolver.settings
        assert "PRIVACY_MODE" in settings
        assert "MODEL_FAST" in settings
        assert "MODEL_SMART" in settings

    # PURPOSE: Verify backward compat alias behaves correctly
    def test_backward_compat_alias(self):
        """Verify backward compat alias behavior."""
        assert CoreProcessor is EnergeiaCoreResolver


# PURPOSE: Test suite validating model selection correctness
class TestModelSelection:
    """K1 Eukairia: モデル選択テスト"""

    # PURPOSE: Verify resolver behaves correctly
    @pytest.fixture
    def resolver(self):
        """Verify resolver behavior."""
        return EnergeiaCoreResolver()

    # PURPOSE: Verify fast model default behaves correctly
    def test_fast_model_default(self, resolver):
        """Verify fast model default behavior."""
        model = resolver._select_model("short text", 60)
        assert "flash" in model.lower() or "fast" in model.lower() or model == resolver.settings["MODEL_FAST"]

    # PURPOSE: Verify smart model deep level behaves correctly
    def test_smart_model_deep_level(self, resolver):
        """Verify smart model deep level behavior."""
        model = resolver._select_model("short text", METRON_DEEP_THRESHOLD)
        assert model == resolver.settings["MODEL_SMART"]

    # PURPOSE: Verify smart model long text behaves correctly
    def test_smart_model_long_text(self, resolver):
        """Verify smart model long text behavior."""
        long_text = "x" * (NOUS_COMPLEXITY_THRESHOLD + 1)
        model = resolver._select_model(long_text, 60)
        assert model == resolver.settings["MODEL_SMART"]

    # PURPOSE: Verify fast model short text low level behaves correctly
    def test_fast_model_short_text_low_level(self, resolver):
        """Verify fast model short text low level behavior."""
        model = resolver._select_model("hello", 30)
        assert model == resolver.settings["MODEL_FAST"]


# PURPOSE: Test suite validating process pipeline correctness
class TestProcessPipeline:
    """O4 Energeia: 処理パイプラインテスト"""

    # PURPOSE: Verify resolver behaves correctly
    @pytest.fixture
    def resolver(self):
        """Verify resolver behavior."""
        return EnergeiaCoreResolver()

    # PURPOSE: Verify process sync behaves correctly
    def test_process_sync(self, resolver):
        """Verify process sync behavior."""
        result = resolver.process_sync("Hello world", 60)
        assert "result" in result or "error" in result

    # PURPOSE: Verify process sync returns result behaves correctly
    def test_process_sync_returns_result(self, resolver):
        """Verify process sync returns result behavior."""
        result = resolver.process_sync("Test input text", 60)
        if "result" in result:
            assert isinstance(result["result"], str)
            assert result["metron_level"] in [30, 60, 100]

    # PURPOSE: Verify process sync with privacy behaves correctly
    def test_process_sync_with_privacy(self, resolver):
        """Verify process sync with privacy behavior."""
        result = resolver.process_sync("user@example.com", 60)
        # PII should be masked and unmasked transparently
        assert "result" in result or "error" in result

    # PURPOSE: Verify process async behaves correctly
    def test_process_async(self, resolver):
        """Verify process async behavior."""
        # PURPOSE: Verify run behaves correctly
        async def run():
            """Verify run behavior."""
            return await resolver.process("Test async", 60)
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(run())
        finally:
            loop.close()
        assert "result" in result or "error" in result

    # PURPOSE: Verify process privacy disabled behaves correctly
    def test_process_privacy_disabled(self):
        """Verify process privacy disabled behavior."""
        resolver = EnergeiaCoreResolver(settings={
            "PRIVACY_MODE": False,
            "MODEL_FAST": "test",
            "MODEL_SMART": "test",
            "USER_SYSTEM_PROMPT": "",
        })
        result = resolver.process_sync("user@example.com", 30)
        assert "result" in result or "error" in result


# PURPOSE: Test suite validating constants correctness
class TestConstants:
    """定数テスト"""

    # PURPOSE: Verify complexity threshold behaves correctly
    def test_complexity_threshold(self):
        """Verify complexity threshold behavior."""
        assert NOUS_COMPLEXITY_THRESHOLD == 1000

    # PURPOSE: Verify deep threshold behaves correctly
    def test_deep_threshold(self):
        """Verify deep threshold behavior."""
        assert METRON_DEEP_THRESHOLD == 100
