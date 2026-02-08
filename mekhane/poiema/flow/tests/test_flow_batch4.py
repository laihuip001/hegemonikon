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

class TestEpocheScanner:
    """リスク検知スキャナーのテスト"""

    @pytest.fixture
    def scanner(self):
        return EpocheScanner()

    def test_init_patterns(self, scanner):
        assert "EMAIL" in scanner.patterns
        assert "PHONE" in scanner.patterns

    def test_scan_clean(self, scanner):
        result = scanner.scan("This is a clean text")
        assert result["has_risks"] is False
        assert result["risk_count"] == 0

    def test_scan_email(self, scanner):
        result = scanner.scan("Contact me at user@example.com")
        assert result["has_risks"] is True
        assert "EMAIL" in result["risks"]

    def test_scan_phone(self, scanner):
        result = scanner.scan("電話番号: 03-1234-5678")
        assert result["has_risks"] is True
        assert "PHONE" in result["risks"]

    def test_scan_zip(self, scanner):
        result = scanner.scan("〒100-0001")
        assert result["has_risks"] is True
        assert "ZIP" in result["risks"]

    def test_scan_ip(self, scanner):
        result = scanner.scan("Server at 192.168.1.100")
        assert result["has_risks"] is True
        assert "IP_ADDRESS" in result["risks"]

    def test_scan_sensitive_keyword(self, scanner):
        result = scanner.scan("This is CONFIDENTIAL information")
        assert result["has_risks"] is True
        assert "SENSITIVE_KEYWORD" in result["risks"]

    def test_scan_japanese_sensitive(self, scanner):
        result = scanner.scan("これは機密文書です")
        assert result["has_risks"] is True

    def test_scan_multiple_risks(self, scanner):
        result = scanner.scan("user@example.com 03-1234-5678 CONFIDENTIAL")
        assert result["risk_count"] >= 3

    def test_check_deny_list_clean(self, scanner):
        blocked, keyword = scanner.check_deny_list("Normal text")
        assert blocked is False
        assert keyword is None

    def test_check_deny_list_blocked(self, scanner):
        blocked, keyword = scanner.check_deny_list("This is SECRET data")
        assert blocked is True
        assert keyword is not None


# ═══ EpocheShield ══════════════════════

class TestEpocheShield:
    """PII マスキングのテスト"""

    @pytest.fixture
    def shield(self):
        return EpocheShield()

    def test_mask_clean(self, shield):
        masked, mapping = shield.mask("Hello world", use_custom_vocab=False)
        assert masked == "Hello world"
        assert len(mapping) == 0

    def test_mask_email(self, shield):
        masked, mapping = shield.mask("user@example.com", use_custom_vocab=False)
        assert "user@example.com" not in masked
        assert "EPOCHE" in masked
        assert len(mapping) == 1

    def test_mask_multiple(self, shield):
        text = "user@example.com and 03-1234-5678"
        masked, mapping = shield.mask(text, use_custom_vocab=False)
        assert "user@example.com" not in masked
        assert len(mapping) >= 2

    def test_unmask(self, shield):
        masked, mapping = shield.mask("user@example.com", use_custom_vocab=False)
        unmasked = shield.unmask(masked, mapping)
        assert "user@example.com" in unmasked

    def test_roundtrip(self, shield):
        original = "Send to user@example.com at 03-1234-5678"
        masked, mapping = shield.mask(original, use_custom_vocab=False)
        restored = shield.unmask(masked, mapping)
        assert restored == original


# ═══ Backward Compatibility ════════════

class TestBackwardCompat:
    """後方互換関数のテスト"""

    def test_mask_pii(self):
        masked, mapping = mask_pii("user@example.com", use_custom_vocab=False)
        assert "user@example.com" not in masked

    def test_unmask_pii(self):
        mapping = {"[EPOCHE_0]": "secret"}
        result = unmask_pii("Found [EPOCHE_0] here", mapping)
        assert "secret" in result


# ═══ MetronResolver ════════════════════

class TestMetronResolver:
    """S1 尺度解決器のテスト"""

    def test_resolve_light(self):
        assert MetronResolver.resolve_level(10) == METRON_LIGHT
        assert MetronResolver.resolve_level(30) == METRON_LIGHT
        assert MetronResolver.resolve_level(45) == METRON_LIGHT

    def test_resolve_medium(self):
        assert MetronResolver.resolve_level(50) == METRON_MEDIUM
        assert MetronResolver.resolve_level(60) == METRON_MEDIUM
        assert MetronResolver.resolve_level(75) == METRON_MEDIUM

    def test_resolve_rich(self):
        assert MetronResolver.resolve_level(80) == METRON_RICH
        assert MetronResolver.resolve_level(100) == METRON_RICH

    def test_label_light(self):
        label = MetronResolver.get_level_label(20)
        assert "Light" in label or "軽" in label

    def test_label_medium(self):
        label = MetronResolver.get_level_label(50)
        assert "Medium" in label or "標準" in label

    def test_label_rich(self):
        label = MetronResolver.get_level_label(80)
        assert "Rich" in label or "濃" in label

    def test_label_deep(self):
        label = MetronResolver.get_level_label(95)
        assert "Deep" in label or "深" in label

    def test_prompt_light(self):
        prompt = MetronResolver.get_system_prompt(20)
        assert "整形" in prompt

    def test_prompt_medium(self):
        prompt = MetronResolver.get_system_prompt(50)
        assert "整形" in prompt or "構造" in prompt

    def test_prompt_rich(self):
        prompt = MetronResolver.get_system_prompt(80)
        assert "強化" in prompt or "補完" in prompt

    def test_prompt_deep(self):
        prompt = MetronResolver.get_system_prompt(95)
        assert "解釈" in prompt or "再構築" in prompt

    def test_prompt_with_user_prompt(self):
        prompt = MetronResolver.get_system_prompt(50, "Focus on clarity")
        assert "Focus on clarity" in prompt

    def test_prompt_clamp(self):
        # Level > 100 should be clamped
        prompt = MetronResolver.get_system_prompt(200)
        assert isinstance(prompt, str)

    def test_prompt_negative(self):
        # Level < 0 should be clamped
        prompt = MetronResolver.get_system_prompt(-10)
        assert isinstance(prompt, str)

    def test_constants(self):
        assert METRON_LIGHT == 30
        assert METRON_MEDIUM == 60
        assert METRON_RICH == 100


# ═══ DoxaCache ═════════════════════════

class TestDoxaCache:
    """Doxa キャッシュのテスト"""

    @pytest.fixture
    def cache(self):
        return DoxaCache()

    def test_init_default(self, cache):
        assert isinstance(cache, DoxaCache)

    def test_init_with_settings(self):
        cache = DoxaCache(settings={"CACHE_TTL_HOURS": 24, "CACHE_MAX_ENTRIES": 100})
        assert isinstance(cache, DoxaCache)

    def test_get_text_hash(self):
        h = DoxaCache.get_text_hash("test")
        assert isinstance(h, str)
        assert len(h) > 0

    def test_hash_deterministic(self):
        h1 = DoxaCache.get_text_hash("test")
        h2 = DoxaCache.get_text_hash("test")
        assert h1 == h2

    def test_hash_different_inputs(self):
        h1 = DoxaCache.get_text_hash("test1")
        h2 = DoxaCache.get_text_hash("test2")
        assert h1 != h2

    def test_sanitize_log(self):
        result = DoxaCache.sanitize_log("Short text")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_sanitize_log_long(self):
        long_text = "x" * 1000
        result = DoxaCache.sanitize_log(long_text)
        assert len(result) <= len(long_text)  # May be truncated
