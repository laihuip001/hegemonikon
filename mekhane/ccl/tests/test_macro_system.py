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

class TestMacro:
    """Macro データクラスのテスト"""

    def test_create_macro(self):
        m = Macro(name="test", ccl="/noe_/dia", description="test macro")
        assert m.name == "test"
        assert m.ccl == "/noe_/dia"
        assert m.usage_count == 0

    def test_builtin_flag(self):
        m = Macro(name="x", ccl="/x", description="", is_builtin=True)
        assert m.is_builtin is True

    def test_default_usage_count(self):
        m = Macro(name="x", ccl="/x", description="")
        assert m.usage_count == 0


# ── BUILTIN_MACROS ───────────────────────

class TestBuiltinMacros:
    """Built-in マクロのテスト"""

    def test_dig_exists(self):
        assert "dig" in BUILTIN_MACROS
        assert BUILTIN_MACROS["dig"].is_builtin is True

    def test_go_exists(self):
        assert "go" in BUILTIN_MACROS

    def test_osc_exists(self):
        assert "osc" in BUILTIN_MACROS

    def test_fix_exists(self):
        assert "fix" in BUILTIN_MACROS

    def test_plan_exists(self):
        assert "plan" in BUILTIN_MACROS

    def test_learn_exists(self):
        assert "learn" in BUILTIN_MACROS

    def test_nous_exists(self):
        assert "nous" in BUILTIN_MACROS

    def test_kyc_exists(self):
        assert "kyc" in BUILTIN_MACROS

    def test_wake_exists(self):
        assert "wake" in BUILTIN_MACROS

    def test_all_builtins_have_ccl(self):
        for name, macro in BUILTIN_MACROS.items():
            assert macro.ccl, f"Macro {name} has empty CCL"

    def test_all_builtins_have_description(self):
        for name, macro in BUILTIN_MACROS.items():
            assert macro.description, f"Macro {name} has empty description"

    def test_builtin_count(self):
        assert len(BUILTIN_MACROS) >= 9, "Should have at least 9 built-in macros"


# ── MacroRegistry ────────────────────────

class TestMacroRegistry:
    """MacroRegistry のテスト"""

    @pytest.fixture
    def tmp_registry(self, tmp_path):
        """一時ファイル使用の registry"""
        return MacroRegistry(path=tmp_path / "macros.json")

    def test_get_builtin(self, tmp_registry):
        m = tmp_registry.get("dig")
        assert m is not None
        assert m.name == "dig"

    def test_get_nonexistent(self, tmp_registry):
        m = tmp_registry.get("nonexistent_macro_xyz")
        assert m is None

    def test_define_user_macro(self, tmp_registry):
        m = tmp_registry.define("test1", "/noe_/dia", "Test macro")
        assert m.name == "test1"
        assert m.ccl == "/noe_/dia"
        assert m.is_builtin is False

    def test_define_and_retrieve(self, tmp_registry):
        tmp_registry.define("mydef", "/bou+_/s+", "My definition")
        m = tmp_registry.get("mydef")
        assert m is not None
        assert m.ccl == "/bou+_/s+"

    def test_define_persists(self, tmp_path):
        path = tmp_path / "macros.json"
        r1 = MacroRegistry(path=path)
        r1.define("persist_test", "/noe", "Persist test")

        r2 = MacroRegistry(path=path)
        m = r2.get("persist_test")
        assert m is not None
        assert m.ccl == "/noe"

    def test_list_all_includes_builtins(self, tmp_registry):
        all_macros = tmp_registry.list_all()
        names = [m.name for m in all_macros]
        assert "dig" in names
        assert "go" in names

    def test_list_all_includes_user(self, tmp_registry):
        tmp_registry.define("custom", "/custom", "custom")
        all_macros = tmp_registry.list_all()
        names = [m.name for m in all_macros]
        assert "custom" in names

    def test_record_usage_increments(self, tmp_registry):
        tmp_registry.define("usage_test", "/test", "test")
        tmp_registry.record_usage("usage_test")
        m = tmp_registry.get("usage_test")
        assert m.usage_count == 1

    def test_record_usage_builtin_no_increment(self, tmp_registry):
        tmp_registry.record_usage("dig")
        m = tmp_registry.get("dig")
        # Builtins don't increment
        assert m.usage_count == 0

    def test_suggest_simple_pattern(self, tmp_registry):
        assert tmp_registry.suggest_from_pattern("/noe") is False

    def test_suggest_complex_pattern(self, tmp_registry):
        assert tmp_registry.suggest_from_pattern("/s+~(/p*/a)_/dia*/o+") is True

    def test_suggest_threshold(self, tmp_registry):
        assert tmp_registry.suggest_from_pattern("/noe+_/dia", threshold=2) is True
        assert tmp_registry.suggest_from_pattern("/noe+_/dia", threshold=5) is False

    def test_empty_file_loads(self, tmp_path):
        path = tmp_path / "empty.json"
        path.write_text("[]")
        r = MacroRegistry(path=path)
        assert r.get("dig") is not None  # Builtins still work

    def test_corrupt_file_loads(self, tmp_path):
        path = tmp_path / "corrupt.json"
        path.write_text("{invalid json")
        r = MacroRegistry(path=path)
        assert r.get("dig") is not None  # Gracefully falls back


# ── MacroExpander ────────────────────────

class TestMacroExpander:
    """MacroExpander のテスト"""

    @pytest.fixture
    def expander(self, tmp_path):
        registry = MacroRegistry(path=tmp_path / "macros.json")
        return MacroExpander(registry=registry)

    def test_expand_known_macro(self, expander):
        result, expanded = expander.expand("@dig")
        assert expanded is True
        assert "/s+" in result  # dig = /s+~(/p*/a)_/dia*/o+

    def test_expand_no_macros(self, expander):
        result, expanded = expander.expand("/noe+_/dia")
        assert expanded is False
        assert result == "/noe+_/dia"

    def test_expand_unknown_macro(self, expander):
        result, expanded = expander.expand("@unknown_xyz")
        assert expanded is False
        assert "@unknown_xyz" in result

    def test_expand_numeric_not_macro(self, expander):
        result, expanded = expander.expand("@2")
        assert expanded is False  # @2 is a level, not a macro

    def test_has_macros_true(self, expander):
        assert expander.has_macros("@dig + /noe") is True

    def test_has_macros_false(self, expander):
        assert expander.has_macros("/noe_/dia") is False

    def test_has_macros_numeric_false(self, expander):
        assert expander.has_macros("@2") is False

    def test_list_macros_in_expr(self, expander):
        macros = expander.list_macros_in_expr("@dig @go")
        names = [m.name for m in macros]
        assert "dig" in names
        assert "go" in names

    def test_list_macros_empty(self, expander):
        macros = expander.list_macros_in_expr("/noe_/dia")
        assert len(macros) == 0

    def test_migrate_level_syntax(self, expander):
        result = expander.migrate_level_syntax("@2")
        assert result == ":2"

    def test_migrate_preserves_macros(self, expander):
        result = expander.migrate_level_syntax("@dig")
        assert "@dig" in result  # @dig is a macro, not a level

    def test_multiple_expansions(self, expander):
        result, expanded = expander.expand("@go then @fix")
        assert expanded is True
        assert "@go" not in result
        assert "@fix" not in result
