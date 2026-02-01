# PROOF: [L2/インフラ] O4→創造機能が必要
"""
Tests for Flow AI Hegemonikón Recast

Verifies that philosophical references are correctly implemented
and backward compatibility is maintained.
"""

import pytest
from ..metron_resolver import MetronResolver, METRON_LIGHT, METRON_MEDIUM, METRON_RICH
from ..epoche_shield import EpocheShield, EpocheScanner


class TestMetronResolver:
    """S1 Metron tests"""

    def test_resolve_level_light(self):
        """Low levels should resolve to LIGHT (30)"""
        assert MetronResolver.resolve_level(0) == METRON_LIGHT
        assert MetronResolver.resolve_level(30) == METRON_LIGHT
        assert MetronResolver.resolve_level(45) == METRON_LIGHT

    def test_resolve_level_medium(self):
        """Medium levels should resolve to MEDIUM (60)"""
        assert MetronResolver.resolve_level(46) == METRON_MEDIUM
        assert MetronResolver.resolve_level(60) == METRON_MEDIUM
        assert MetronResolver.resolve_level(75) == METRON_MEDIUM

    def test_resolve_level_rich(self):
        """High levels should resolve to RICH (100)"""
        assert MetronResolver.resolve_level(76) == METRON_RICH
        assert MetronResolver.resolve_level(100) == METRON_RICH

    def test_get_system_prompt_contains_instructions(self):
        """System prompts should contain formatting instructions"""
        prompt = MetronResolver.get_system_prompt(30)
        assert "入力文" in prompt
        assert "出力は" in prompt

    def test_backward_compatibility_alias(self):
        """SeasoningManager alias should work"""
        from ..metron_resolver import SeasoningManager

        assert SeasoningManager is MetronResolver


class TestEpocheShield:
    """A2 Krisis (Epochē) tests"""

    def test_mask_email(self):
        """Email should be masked"""
        shield = EpocheShield()
        text = "Contact me at test@example.com"
        masked, mapping = shield.mask(text, use_custom_vocab=False)

        assert "test@example.com" not in masked
        assert "[EPOCHE_" in masked
        assert len(mapping) == 1

    def test_unmask_restores_original(self):
        """Unmasking should restore original PII"""
        shield = EpocheShield()
        original = "My email is test@example.com and phone is 03-1234-5678"
        masked, mapping = shield.mask(original, use_custom_vocab=False)
        restored = shield.unmask(masked, mapping)

        assert restored == original

    def test_mask_phone(self):
        """Phone number should be masked"""
        shield = EpocheShield()
        text = "Call 03-1234-5678"
        masked, mapping = shield.mask(text, use_custom_vocab=False)

        assert "03-1234-5678" not in masked

    def test_backward_compatibility_aliases(self):
        """PrivacyHandler/PrivacyScanner aliases should work"""
        from ..epoche_shield import PrivacyHandler, PrivacyScanner

        assert PrivacyHandler is EpocheShield
        assert PrivacyScanner is EpocheScanner


class TestEpocheScanner:
    """A2 Krisis scanner tests"""

    def test_scan_detects_email(self):
        """Scanner should detect email patterns"""
        scanner = EpocheScanner()
        result = scanner.scan("Email: admin@example.org")

        assert result["has_risks"] is True
        assert "EMAIL" in result["risks"]

    def test_scan_detects_sensitive_keywords(self):
        """Scanner should detect sensitive keywords"""
        scanner = EpocheScanner()
        result = scanner.scan("This is CONFIDENTIAL information")

        assert result["has_risks"] is True
        assert "SENSITIVE_KEYWORD" in result["risks"]

    def test_check_deny_list(self):
        """Deny list should block sensitive keywords"""
        scanner = EpocheScanner()
        blocked, keyword = scanner.check_deny_list("This is 社外秘")

        assert blocked is True
        assert keyword == "社外秘"
