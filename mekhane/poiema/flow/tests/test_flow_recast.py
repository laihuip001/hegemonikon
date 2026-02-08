# PROOF: [L2/インフラ] <- mekhane/poiema/flow/tests/ O4→創造機能が必要
"""
Tests for Flow AI Hegemonikón Recast

Verifies that philosophical references are correctly implemented
and backward compatibility is maintained.
"""

import pytest
from ..metron_resolver import MetronResolver, METRON_LIGHT, METRON_MEDIUM, METRON_RICH
from ..epoche_shield import EpocheShield, EpocheScanner


# PURPOSE: S1 Metron tests
class TestMetronResolver:
    """S1 Metron tests"""

    # PURPOSE: Low levels should resolve to LIGHT (30)
    def test_resolve_level_light(self):
        """Low levels should resolve to LIGHT (30)"""
        assert MetronResolver.resolve_level(0) == METRON_LIGHT
        assert MetronResolver.resolve_level(30) == METRON_LIGHT
        assert MetronResolver.resolve_level(45) == METRON_LIGHT

    # PURPOSE: Medium levels should resolve to MEDIUM (60)
    def test_resolve_level_medium(self):
        """Medium levels should resolve to MEDIUM (60)"""
        assert MetronResolver.resolve_level(46) == METRON_MEDIUM
        assert MetronResolver.resolve_level(60) == METRON_MEDIUM
        assert MetronResolver.resolve_level(75) == METRON_MEDIUM

    # PURPOSE: High levels should resolve to RICH (100)
    def test_resolve_level_rich(self):
        """High levels should resolve to RICH (100)"""
        assert MetronResolver.resolve_level(76) == METRON_RICH
        assert MetronResolver.resolve_level(100) == METRON_RICH

    # PURPOSE: System prompts should contain formatting instructions
    def test_get_system_prompt_contains_instructions(self):
        """System prompts should contain formatting instructions"""
        prompt = MetronResolver.get_system_prompt(30)
        assert "入力文" in prompt
        assert "出力は" in prompt

    # PURPOSE: SeasoningManager alias should work
    def test_backward_compatibility_alias(self):
        """SeasoningManager alias should work"""
        from ..metron_resolver import SeasoningManager

        assert SeasoningManager is MetronResolver


# PURPOSE: A2 Krisis (Epochē) tests
class TestEpocheShield:
    """A2 Krisis (Epochē) tests"""

    # PURPOSE: Email should be masked
    def test_mask_email(self):
        """Email should be masked"""
        shield = EpocheShield()
        text = "Contact me at test@example.com"
        masked, mapping = shield.mask(text, use_custom_vocab=False)

        assert "test@example.com" not in masked
        assert "[EPOCHE_" in masked
        assert len(mapping) == 1

    # PURPOSE: Unmasking should restore original PII
    def test_unmask_restores_original(self):
        """Unmasking should restore original PII"""
        shield = EpocheShield()
        original = "My email is test@example.com and phone is 03-1234-5678"
        masked, mapping = shield.mask(original, use_custom_vocab=False)
        restored = shield.unmask(masked, mapping)

        assert restored == original

    # PURPOSE: Phone number should be masked
    def test_mask_phone(self):
        """Phone number should be masked"""
        shield = EpocheShield()
        text = "Call 03-1234-5678"
        masked, mapping = shield.mask(text, use_custom_vocab=False)

        assert "03-1234-5678" not in masked

    # PURPOSE: PrivacyHandler/PrivacyScanner aliases should work
    def test_backward_compatibility_aliases(self):
        """PrivacyHandler/PrivacyScanner aliases should work"""
        from ..epoche_shield import PrivacyHandler, PrivacyScanner

        assert PrivacyHandler is EpocheShield
        assert PrivacyScanner is EpocheScanner


# PURPOSE: A2 Krisis scanner tests
class TestEpocheScanner:
    """A2 Krisis scanner tests"""

    # PURPOSE: Scanner should detect email patterns
    def test_scan_detects_email(self):
        """Scanner should detect email patterns"""
        scanner = EpocheScanner()
        result = scanner.scan("Email: admin@example.org")

        assert result["has_risks"] is True
        assert "EMAIL" in result["risks"]

    # PURPOSE: Scanner should detect sensitive keywords
    def test_scan_detects_sensitive_keywords(self):
        """Scanner should detect sensitive keywords"""
        scanner = EpocheScanner()
        result = scanner.scan("This is CONFIDENTIAL information")

        assert result["has_risks"] is True
        assert "SENSITIVE_KEYWORD" in result["risks"]

    # PURPOSE: Deny list should block sensitive keywords
    def test_check_deny_list(self):
        """Deny list should block sensitive keywords"""
        scanner = EpocheScanner()
        blocked, keyword = scanner.check_deny_list("This is 社外秘")

        assert blocked is True
        assert keyword == "社外秘"
