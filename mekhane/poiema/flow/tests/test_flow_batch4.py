#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/poiema/flow/tests/
# PURPOSE: Poiema flow モジュール (EpocheScanner, EpocheShield, MetronResolver, DoxaCache) テスト
"""Poiema Flow Tests — Batch 4"""

import pytest
import hashlib
from mekhane.poiema.flow.epoche_shield import (
    EpocheScanner,
    EpocheShield,
    mask_pii,
    unmask_pii,
)
from mekhane.poiema.flow.metron_resolver import (
    MetronResolver,
    METRON_LIGHT,
    METRON_MEDIUM,
    METRON_RICH,
    METRON_LIGHT_MAX,
    METRON_MEDIUM_MAX,
    METRON_RICH_MAX,
)
from mekhane.poiema.flow.doxa_cache import DoxaCache


# ═══ EpocheScanner ═════════════════════

# PURPOSE: Test suite validating epoche scanner correctness
class TestEpocheScanner:
    """リスク検知スキャナーのテスト"""

    # PURPOSE: Verify scanner behaves correctly
    @pytest.fixture
    def scanner(self):
        """Verify scanner behavior."""
        return EpocheScanner()

    # PURPOSE: Verify init patterns behaves correctly
    def test_init_patterns(self, scanner):
        """Verify init patterns behavior."""
        assert "EMAIL" in scanner.patterns
        assert "PHONE" in scanner.patterns

    # PURPOSE: Verify scan clean behaves correctly
    def test_scan_clean(self, scanner):
        """Verify scan clean behavior."""
        result = scanner.scan("This is a clean text")
        assert result["has_risks"] is False
        assert result["risk_count"] == 0

    # PURPOSE: Verify scan email behaves correctly
    def test_scan_email(self, scanner):
        """Verify scan email behavior."""
        result = scanner.scan("Contact me at user@example.com")
        assert result["has_risks"] is True
        assert "EMAIL" in result["risks"]

    # PURPOSE: Verify scan phone behaves correctly
    def test_scan_phone(self, scanner):
        """Verify scan phone behavior."""
        result = scanner.scan("電話番号: 03-1234-5678")
        assert result["has_risks"] is True
        assert "PHONE" in result["risks"]

    # PURPOSE: Verify scan zip behaves correctly
    def test_scan_zip(self, scanner):
        """Verify scan zip behavior."""
        result = scanner.scan("〒100-0001")
        assert result["has_risks"] is True
        assert "ZIP" in result["risks"]

    # PURPOSE: Verify scan ip behaves correctly
    def test_scan_ip(self, scanner):
        """Verify scan ip behavior."""
        result = scanner.scan("Server at 192.168.1.100")
        assert result["has_risks"] is True
        assert "IP_ADDRESS" in result["risks"]

    # PURPOSE: Verify scan sensitive keyword behaves correctly
    def test_scan_sensitive_keyword(self, scanner):
        """Verify scan sensitive keyword behavior."""
        result = scanner.scan("This is CONFIDENTIAL information")
        assert result["has_risks"] is True
        assert "SENSITIVE_KEYWORD" in result["risks"]

    # PURPOSE: Verify scan japanese sensitive behaves correctly
    def test_scan_japanese_sensitive(self, scanner):
        """Verify scan japanese sensitive behavior."""
        result = scanner.scan("これは機密文書です")
        assert result["has_risks"] is True

    # PURPOSE: Verify scan multiple risks behaves correctly
    def test_scan_multiple_risks(self, scanner):
        """Verify scan multiple risks behavior."""
        result = scanner.scan("user@example.com 03-1234-5678 CONFIDENTIAL")
        assert result["risk_count"] >= 3

    # PURPOSE: Verify check deny list clean behaves correctly
    def test_check_deny_list_clean(self, scanner):
        """Verify check deny list clean behavior."""
        blocked, keyword = scanner.check_deny_list("Normal text")
        assert blocked is False
        assert keyword is None

    # PURPOSE: Verify check deny list blocked behaves correctly
    def test_check_deny_list_blocked(self, scanner):
        """Verify check deny list blocked behavior."""
        blocked, keyword = scanner.check_deny_list("This is SECRET data")
        assert blocked is True
        assert keyword is not None


# ═══ EpocheShield ══════════════════════

# PURPOSE: Test suite validating epoche shield correctness
class TestEpocheShield:
    """PII マスキングのテスト"""

    # PURPOSE: Verify shield behaves correctly
    @pytest.fixture
    def shield(self):
        """Verify shield behavior."""
        return EpocheShield()

    # PURPOSE: Verify mask clean behaves correctly
    def test_mask_clean(self, shield):
        """Verify mask clean behavior."""
        masked, mapping = shield.mask("Hello world", use_custom_vocab=False)
        assert masked == "Hello world"
        assert len(mapping) == 0

    # PURPOSE: Verify mask email behaves correctly
    def test_mask_email(self, shield):
        """Verify mask email behavior."""
        masked, mapping = shield.mask("user@example.com", use_custom_vocab=False)
        assert "user@example.com" not in masked
        assert "EPOCHE" in masked
        assert len(mapping) == 1

    # PURPOSE: Verify mask multiple behaves correctly
    def test_mask_multiple(self, shield):
        """Verify mask multiple behavior."""
        text = "user@example.com and 03-1234-5678"
        masked, mapping = shield.mask(text, use_custom_vocab=False)
        assert "user@example.com" not in masked
        assert len(mapping) >= 2

    # PURPOSE: Verify unmask behaves correctly
    def test_unmask(self, shield):
        """Verify unmask behavior."""
        masked, mapping = shield.mask("user@example.com", use_custom_vocab=False)
        unmasked = shield.unmask(masked, mapping)
        assert "user@example.com" in unmasked

    # PURPOSE: Verify roundtrip behaves correctly
    def test_roundtrip(self, shield):
        """Verify roundtrip behavior."""
        original = "Send to user@example.com at 03-1234-5678"
        masked, mapping = shield.mask(original, use_custom_vocab=False)
        restored = shield.unmask(masked, mapping)
        assert restored == original


# ═══ Backward Compatibility ════════════

# PURPOSE: Test suite validating backward compat correctness
class TestBackwardCompat:
    """後方互換関数のテスト"""

    # PURPOSE: Verify mask pii behaves correctly
    def test_mask_pii(self):
        """Verify mask pii behavior."""
        masked, mapping = mask_pii("user@example.com", use_custom_vocab=False)
        assert "user@example.com" not in masked

    # PURPOSE: Verify unmask pii behaves correctly
    def test_unmask_pii(self):
        """Verify unmask pii behavior."""
        mapping = {"[EPOCHE_0]": "secret"}
        result = unmask_pii("Found [EPOCHE_0] here", mapping)
        assert "secret" in result


# ═══ MetronResolver ════════════════════

# PURPOSE: Test suite validating metron resolver correctness
class TestMetronResolver:
    """S1 尺度解決器のテスト"""

    # PURPOSE: Verify resolve light behaves correctly
    def test_resolve_light(self):
        """Verify resolve light behavior."""
        assert MetronResolver.resolve_level(10) == METRON_LIGHT
        assert MetronResolver.resolve_level(30) == METRON_LIGHT
        assert MetronResolver.resolve_level(45) == METRON_LIGHT

    # PURPOSE: Verify resolve medium behaves correctly
    def test_resolve_medium(self):
        """Verify resolve medium behavior."""
        assert MetronResolver.resolve_level(50) == METRON_MEDIUM
        assert MetronResolver.resolve_level(60) == METRON_MEDIUM
        assert MetronResolver.resolve_level(75) == METRON_MEDIUM

    # PURPOSE: Verify resolve rich behaves correctly
    def test_resolve_rich(self):
        """Verify resolve rich behavior."""
        assert MetronResolver.resolve_level(80) == METRON_RICH
        assert MetronResolver.resolve_level(100) == METRON_RICH

    # PURPOSE: Verify label light behaves correctly
    def test_label_light(self):
        """Verify label light behavior."""
        label = MetronResolver.get_level_label(20)
        assert "Light" in label or "軽" in label

    # PURPOSE: Verify label medium behaves correctly
    def test_label_medium(self):
        """Verify label medium behavior."""
        label = MetronResolver.get_level_label(50)
        assert "Medium" in label or "標準" in label

    # PURPOSE: Verify label rich behaves correctly
    def test_label_rich(self):
        """Verify label rich behavior."""
        label = MetronResolver.get_level_label(80)
        assert "Rich" in label or "濃" in label

    # PURPOSE: Verify label deep behaves correctly
    def test_label_deep(self):
        """Verify label deep behavior."""
        label = MetronResolver.get_level_label(95)
        assert "Deep" in label or "深" in label

    # PURPOSE: Verify prompt light behaves correctly
    def test_prompt_light(self):
        """Verify prompt light behavior."""
        prompt = MetronResolver.get_system_prompt(20)
        assert "整形" in prompt

    # PURPOSE: Verify prompt medium behaves correctly
    def test_prompt_medium(self):
        """Verify prompt medium behavior."""
        prompt = MetronResolver.get_system_prompt(50)
        assert "整形" in prompt or "構造" in prompt

    # PURPOSE: Verify prompt rich behaves correctly
    def test_prompt_rich(self):
        """Verify prompt rich behavior."""
        prompt = MetronResolver.get_system_prompt(80)
        assert "強化" in prompt or "補完" in prompt

    # PURPOSE: Verify prompt deep behaves correctly
    def test_prompt_deep(self):
        """Verify prompt deep behavior."""
        prompt = MetronResolver.get_system_prompt(95)
        assert "解釈" in prompt or "再構築" in prompt

    # PURPOSE: Verify prompt with user prompt behaves correctly
    def test_prompt_with_user_prompt(self):
        """Verify prompt with user prompt behavior."""
        prompt = MetronResolver.get_system_prompt(50, "Focus on clarity")
        assert "Focus on clarity" in prompt

    # PURPOSE: Verify prompt clamp behaves correctly
    def test_prompt_clamp(self):
        # Level > 100 should be clamped
        """Verify prompt clamp behavior."""
        prompt = MetronResolver.get_system_prompt(200)
        assert isinstance(prompt, str)

    # PURPOSE: Verify prompt negative behaves correctly
    def test_prompt_negative(self):
        # Level < 0 should be clamped
        """Verify prompt negative behavior."""
        prompt = MetronResolver.get_system_prompt(-10)
        assert isinstance(prompt, str)

    # PURPOSE: Verify constants behaves correctly
    def test_constants(self):
        """Verify constants behavior."""
        assert METRON_LIGHT == 30
        assert METRON_MEDIUM == 60
        assert METRON_RICH == 100


# ═══ DoxaCache ═════════════════════════

# PURPOSE: Test suite validating doxa cache correctness
class TestDoxaCache:
    """Doxa キャッシュのテスト"""

    # PURPOSE: Verify cache behaves correctly
    @pytest.fixture
    def cache(self):
        """Verify cache behavior."""
        return DoxaCache()

    # PURPOSE: Verify init default behaves correctly
    def test_init_default(self, cache):
        """Verify init default behavior."""
        assert isinstance(cache, DoxaCache)

    # PURPOSE: Verify init with settings behaves correctly
    def test_init_with_settings(self):
        """Verify init with settings behavior."""
        cache = DoxaCache(settings={"CACHE_TTL_HOURS": 24, "CACHE_MAX_ENTRIES": 100})
        assert isinstance(cache, DoxaCache)

    # PURPOSE: Verify get text hash behaves correctly
    def test_get_text_hash(self):
        """Verify get text hash behavior."""
        h = DoxaCache.get_text_hash("test")
        assert isinstance(h, str)
        assert len(h) > 0

    # PURPOSE: Verify hash deterministic behaves correctly
    def test_hash_deterministic(self):
        """Verify hash deterministic behavior."""
        h1 = DoxaCache.get_text_hash("test")
        h2 = DoxaCache.get_text_hash("test")
        assert h1 == h2

    # PURPOSE: Verify hash different inputs behaves correctly
    def test_hash_different_inputs(self):
        """Verify hash different inputs behavior."""
        h1 = DoxaCache.get_text_hash("test1")
        h2 = DoxaCache.get_text_hash("test2")
        assert h1 != h2

    # PURPOSE: Verify sanitize log behaves correctly
    def test_sanitize_log(self):
        """Verify sanitize log behavior."""
        result = DoxaCache.sanitize_log("Short text")
        assert isinstance(result, str)
        assert len(result) > 0

    # PURPOSE: Verify sanitize log long behaves correctly
    def test_sanitize_log_long(self):
        """Verify sanitize log long behavior."""
        long_text = "x" * 1000
        result = DoxaCache.sanitize_log(long_text)
        assert len(result) <= len(long_text)  # May be truncated
