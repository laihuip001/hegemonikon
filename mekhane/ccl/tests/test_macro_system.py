#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/ccl/tests/
# PURPOSE: CCL Macro Registry & Expander の包括テスト
"""CCL Macro System Tests"""

import json
import pytest
from pathlib import Path

from mekhane.ccl.macro_registry import (
    Macro,
    MacroRegistry,
    BUILTIN_MACROS,
)
from mekhane.ccl.macro_expander import MacroExpander


# ── Macro Dataclass ──────────────────────

# PURPOSE: Test suite validating macro correctness
class TestMacro:
    """Macro データクラスのテスト"""

    # PURPOSE: Verify create macro behaves correctly
    def test_create_macro(self):
        """Verify create macro behavior."""
        m = Macro(name="test", ccl="/noe_/dia", description="test macro")
        assert m.name == "test"
        assert m.ccl == "/noe_/dia"
        assert m.usage_count == 0

    # PURPOSE: Verify builtin flag behaves correctly
    def test_builtin_flag(self):
        """Verify builtin flag behavior."""
        m = Macro(name="x", ccl="/x", description="", is_builtin=True)
        assert m.is_builtin is True

    # PURPOSE: Verify default usage count behaves correctly
    def test_default_usage_count(self):
        """Verify default usage count behavior."""
        m = Macro(name="x", ccl="/x", description="")
        assert m.usage_count == 0


# ── BUILTIN_MACROS ───────────────────────

# PURPOSE: Test suite validating builtin macros correctness
class TestBuiltinMacros:
    """Built-in マクロのテスト"""

    # PURPOSE: Verify dig exists behaves correctly
    def test_dig_exists(self):
        """Verify dig exists behavior."""
        assert "dig" in BUILTIN_MACROS
        assert BUILTIN_MACROS["dig"].is_builtin is True

    # PURPOSE: Verify go exists behaves correctly
    def test_go_exists(self):
        """Verify go exists behavior."""
        assert "go" in BUILTIN_MACROS

    # PURPOSE: Verify osc exists behaves correctly
    def test_osc_exists(self):
        """Verify osc exists behavior."""
        assert "osc" in BUILTIN_MACROS

    # PURPOSE: Verify fix exists behaves correctly
    def test_fix_exists(self):
        """Verify fix exists behavior."""
        assert "fix" in BUILTIN_MACROS

    # PURPOSE: Verify plan exists behaves correctly
    def test_plan_exists(self):
        """Verify plan exists behavior."""
        assert "plan" in BUILTIN_MACROS

    # PURPOSE: Verify learn exists behaves correctly
    def test_learn_exists(self):
        """Verify learn exists behavior."""
        assert "learn" in BUILTIN_MACROS

    # PURPOSE: Verify nous exists behaves correctly
    def test_nous_exists(self):
        """Verify nous exists behavior."""
        assert "nous" in BUILTIN_MACROS

    # PURPOSE: Verify kyc exists behaves correctly
    def test_kyc_exists(self):
        """Verify kyc exists behavior."""
        assert "kyc" in BUILTIN_MACROS

    # PURPOSE: Verify wake exists behaves correctly
    def test_wake_exists(self):
        """Verify wake exists behavior."""
        assert "wake" in BUILTIN_MACROS

    # PURPOSE: Verify all builtins have ccl behaves correctly
    def test_all_builtins_have_ccl(self):
        """Verify all builtins have ccl behavior."""
        for name, macro in BUILTIN_MACROS.items():
            assert macro.ccl, f"Macro {name} has empty CCL"

    # PURPOSE: Verify all builtins have description behaves correctly
    def test_all_builtins_have_description(self):
        """Verify all builtins have description behavior."""
        for name, macro in BUILTIN_MACROS.items():
            assert macro.description, f"Macro {name} has empty description"

    # PURPOSE: Verify builtin count behaves correctly
    def test_builtin_count(self):
        """Verify builtin count behavior."""
        assert len(BUILTIN_MACROS) >= 9, "Should have at least 9 built-in macros"


# ── MacroRegistry ────────────────────────

# PURPOSE: Test suite validating macro registry correctness
class TestMacroRegistry:
    """MacroRegistry のテスト"""

    # PURPOSE: Verify tmp registry behaves correctly
    @pytest.fixture
    def tmp_registry(self, tmp_path):
        """一時ファイル使用の registry"""
        return MacroRegistry(path=tmp_path / "macros.json")

    # PURPOSE: Verify get builtin behaves correctly
    def test_get_builtin(self, tmp_registry):
        """Verify get builtin behavior."""
        m = tmp_registry.get("dig")
        assert m is not None
        assert m.name == "dig"

    # PURPOSE: Verify get nonexistent behaves correctly
    def test_get_nonexistent(self, tmp_registry):
        """Verify get nonexistent behavior."""
        m = tmp_registry.get("nonexistent_macro_xyz")
        assert m is None

    # PURPOSE: Verify define user macro behaves correctly
    def test_define_user_macro(self, tmp_registry):
        """Verify define user macro behavior."""
        m = tmp_registry.define("test1", "/noe_/dia", "Test macro")
        assert m.name == "test1"
        assert m.ccl == "/noe_/dia"
        assert m.is_builtin is False

    # PURPOSE: Verify define and retrieve behaves correctly
    def test_define_and_retrieve(self, tmp_registry):
        """Verify define and retrieve behavior."""
        tmp_registry.define("mydef", "/bou+_/s+", "My definition")
        m = tmp_registry.get("mydef")
        assert m is not None
        assert m.ccl == "/bou+_/s+"

    # PURPOSE: Verify define persists behaves correctly
    def test_define_persists(self, tmp_path):
        """Verify define persists behavior."""
        path = tmp_path / "macros.json"
        r1 = MacroRegistry(path=path)
        r1.define("persist_test", "/noe", "Persist test")

        r2 = MacroRegistry(path=path)
        m = r2.get("persist_test")
        assert m is not None
        assert m.ccl == "/noe"

    # PURPOSE: Verify list all includes builtins behaves correctly
    def test_list_all_includes_builtins(self, tmp_registry):
        """Verify list all includes builtins behavior."""
        all_macros = tmp_registry.list_all()
        names = [m.name for m in all_macros]
        assert "dig" in names
        assert "go" in names

    # PURPOSE: Verify list all includes user behaves correctly
    def test_list_all_includes_user(self, tmp_registry):
        """Verify list all includes user behavior."""
        tmp_registry.define("custom", "/custom", "custom")
        all_macros = tmp_registry.list_all()
        names = [m.name for m in all_macros]
        assert "custom" in names

    # PURPOSE: Verify record usage increments behaves correctly
    def test_record_usage_increments(self, tmp_registry):
        """Verify record usage increments behavior."""
        tmp_registry.define("usage_test", "/test", "test")
        tmp_registry.record_usage("usage_test")
        m = tmp_registry.get("usage_test")
        assert m.usage_count == 1

    # PURPOSE: Verify record usage builtin no increment behaves correctly
    def test_record_usage_builtin_no_increment(self, tmp_registry):
        """Verify record usage builtin no increment behavior."""
        tmp_registry.record_usage("dig")
        m = tmp_registry.get("dig")
        # Builtins don't increment
        assert m.usage_count == 0

    # PURPOSE: Verify suggest simple pattern behaves correctly
    def test_suggest_simple_pattern(self, tmp_registry):
        """Verify suggest simple pattern behavior."""
        assert tmp_registry.suggest_from_pattern("/noe") is False

    # PURPOSE: Verify suggest complex pattern behaves correctly
    def test_suggest_complex_pattern(self, tmp_registry):
        """Verify suggest complex pattern behavior."""
        assert tmp_registry.suggest_from_pattern("/s+~(/p*/a)_/dia*/o+") is True

    # PURPOSE: Verify suggest threshold behaves correctly
    def test_suggest_threshold(self, tmp_registry):
        """Verify suggest threshold behavior."""
        assert tmp_registry.suggest_from_pattern("/noe+_/dia", threshold=2) is True
        assert tmp_registry.suggest_from_pattern("/noe+_/dia", threshold=5) is False

    # PURPOSE: Verify empty file loads behaves correctly
    def test_empty_file_loads(self, tmp_path):
        """Verify empty file loads behavior."""
        path = tmp_path / "empty.json"
        path.write_text("[]")
        r = MacroRegistry(path=path)
        assert r.get("dig") is not None  # Builtins still work

    # PURPOSE: Verify corrupt file loads behaves correctly
    def test_corrupt_file_loads(self, tmp_path):
        """Verify corrupt file loads behavior."""
        path = tmp_path / "corrupt.json"
        path.write_text("{invalid json")
        r = MacroRegistry(path=path)
        assert r.get("dig") is not None  # Gracefully falls back


# ── MacroExpander ────────────────────────

# PURPOSE: Test suite validating macro expander correctness
class TestMacroExpander:
    """MacroExpander のテスト"""

    # PURPOSE: Verify expander behaves correctly
    @pytest.fixture
    def expander(self, tmp_path):
        """Verify expander behavior."""
        registry = MacroRegistry(path=tmp_path / "macros.json")
        return MacroExpander(registry=registry)

    # PURPOSE: Verify expand known macro behaves correctly
    def test_expand_known_macro(self, expander):
        """Verify expand known macro behavior."""
        result, expanded = expander.expand("@dig")
        assert expanded is True
        assert "/s+" in result  # dig = /s+~(/p*/a)_/dia*/o+

    # PURPOSE: Verify expand no macros behaves correctly
    def test_expand_no_macros(self, expander):
        """Verify expand no macros behavior."""
        result, expanded = expander.expand("/noe+_/dia")
        assert expanded is False
        assert result == "/noe+_/dia"

    # PURPOSE: Verify expand unknown macro behaves correctly
    def test_expand_unknown_macro(self, expander):
        """Verify expand unknown macro behavior."""
        result, expanded = expander.expand("@unknown_xyz")
        assert expanded is False
        assert "@unknown_xyz" in result

    # PURPOSE: Verify expand numeric not macro behaves correctly
    def test_expand_numeric_not_macro(self, expander):
        """Verify expand numeric not macro behavior."""
        result, expanded = expander.expand("@2")
        assert expanded is False  # @2 is a level, not a macro

    # PURPOSE: Verify has macros true behaves correctly
    def test_has_macros_true(self, expander):
        """Verify has macros true behavior."""
        assert expander.has_macros("@dig + /noe") is True

    # PURPOSE: Verify has macros false behaves correctly
    def test_has_macros_false(self, expander):
        """Verify has macros false behavior."""
        assert expander.has_macros("/noe_/dia") is False

    # PURPOSE: Verify has macros numeric false behaves correctly
    def test_has_macros_numeric_false(self, expander):
        """Verify has macros numeric false behavior."""
        assert expander.has_macros("@2") is False

    # PURPOSE: Verify list macros in expr behaves correctly
    def test_list_macros_in_expr(self, expander):
        """Verify list macros in expr behavior."""
        macros = expander.list_macros_in_expr("@dig @go")
        names = [m.name for m in macros]
        assert "dig" in names
        assert "go" in names

    # PURPOSE: Verify list macros empty behaves correctly
    def test_list_macros_empty(self, expander):
        """Verify list macros empty behavior."""
        macros = expander.list_macros_in_expr("/noe_/dia")
        assert len(macros) == 0

    # PURPOSE: Verify migrate level syntax behaves correctly
    def test_migrate_level_syntax(self, expander):
        """Verify migrate level syntax behavior."""
        result = expander.migrate_level_syntax("@2")
        assert result == ":2"

    # PURPOSE: Verify migrate preserves macros behaves correctly
    def test_migrate_preserves_macros(self, expander):
        """Verify migrate preserves macros behavior."""
        result = expander.migrate_level_syntax("@dig")
        assert "@dig" in result  # @dig is a macro, not a level

    # PURPOSE: Verify multiple expansions behaves correctly
    def test_multiple_expansions(self, expander):
        """Verify multiple expansions behavior."""
        result, expanded = expander.expand("@go then @fix")
        assert expanded is True
        assert "@go" not in result
        assert "@fix" not in result
