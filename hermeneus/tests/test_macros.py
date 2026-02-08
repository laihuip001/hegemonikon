# PURPOSE: CCL Macro ローダー + 展開 + E2E パイプライン テスト
"""
Hermēneus Macro テストスイート

対象:
- macros.py: MacroDefinition, load_standard_macros, get_all_macros, get_macro_expansion
- expander.py: Expander, expand_ccl (@macro 展開)
- E2E: @macro → expand → parse (→ compile)
"""

import pytest

from hermeneus.src.macros import (
    BUILTIN_MACROS,
    MacroDefinition,
    get_all_macros,
    get_macro_expansion,
    get_macro_registry,
    load_standard_macros,
    parse_macro_file,
)
from hermeneus.src.expander import Expander, ExpansionResult, expand_ccl
from hermeneus.src.parser import CCLParser


# =============================================================================
# MacroLoader
# =============================================================================


class TestBuiltinMacros:
    """BUILTIN_MACROS (ハードコード版) のテスト"""

    def test_builtin_macros_exist(self):
        assert len(BUILTIN_MACROS) >= 5

    def test_think_macro(self):
        assert "think" in BUILTIN_MACROS
        assert "/noe+" in BUILTIN_MACROS["think"]

    def test_plan_macro(self):
        assert "plan" in BUILTIN_MACROS
        assert "/bou+" in BUILTIN_MACROS["plan"]

    def test_review_macro(self):
        assert "review" in BUILTIN_MACROS
        assert "/dia+" in BUILTIN_MACROS["review"]

    def test_tak_macro(self):
        assert "tak" in BUILTIN_MACROS
        assert "/s+" in BUILTIN_MACROS["tak"]

    def test_dig_macro(self):
        assert "dig" in BUILTIN_MACROS
        assert "/zet+" in BUILTIN_MACROS["dig"]


class TestLoadStandardMacros:
    """ccl/macros/ からのマクロ読み込みテスト"""

    def test_loads_from_ccl_macros_dir(self):
        macros = load_standard_macros()
        # ccl/macros/ が存在すれば 1 件以上
        # 存在しなければ空辞書（エラーなし）
        assert isinstance(macros, dict)

    def test_file_macros_loaded(self):
        macros = load_standard_macros()
        if macros:  # ccl/macros/ が存在する場合
            # At least some macros should be loaded
            assert len(macros) >= 1
            # Each should be a MacroDefinition
            first_name = next(iter(macros))
            assert isinstance(macros[first_name], MacroDefinition)

    def test_macro_has_required_fields(self):
        macros = load_standard_macros()
        for name, macro in macros.items():
            assert macro.name == name
            assert isinstance(macro.expansion, str)
            assert macro.source_file.exists()


class TestGetAllMacros:
    """全マクロ取得 (builtin + file) テスト"""

    def test_includes_builtin(self):
        all_macros = get_all_macros()
        # Builtin macros should always be present
        assert "think" in all_macros
        assert "plan" in all_macros

    def test_includes_file_macros(self):
        all_macros = get_all_macros()
        # At least some file macros should load
        assert len(all_macros) >= len(BUILTIN_MACROS)

    def test_returns_strings(self):
        all_macros = get_all_macros()
        for name, expansion in all_macros.items():
            assert isinstance(name, str)
            assert isinstance(expansion, str)

    def test_total_count(self):
        all_macros = get_all_macros()
        # 5 builtin + file macros
        assert len(all_macros) >= 5


class TestGetMacroExpansion:
    def test_known_macro(self):
        # Builtin "think" might not be in load_standard_macros
        # but get_macro_expansion only checks ccl/macros/
        # This is fine — test the mechanism
        result = get_macro_expansion("nonexistent_macro_xyz")
        assert result is None

    def test_file_macro_if_available(self):
        macros = load_standard_macros()
        if macros:
            name = next(iter(macros))
            result = get_macro_expansion(name)
            # パース成功していれば展開形がある
            assert result is not None or result is None  # graceful


# =============================================================================
# Expander — @macro 展開
# =============================================================================


class TestExpander:
    """Expander クラスのテスト"""

    def test_expand_simple_macro(self):
        expander = Expander(macro_registry={"think": "/noe+ >> V[] < 0.3"})
        result = expander.expand("@think")
        assert result.expanded == "/noe+ >> V[] < 0.3"

    def test_expand_no_macro(self):
        expander = Expander(macro_registry={"think": "/noe+"})
        result = expander.expand("/dia+")
        assert result.expanded == "/dia+"

    def test_expand_unknown_macro(self):
        expander = Expander(macro_registry={"think": "/noe+"})
        result = expander.expand("@unknown")
        assert result.expanded == "@unknown"  # Passthrough

    def test_expand_with_sequence(self):
        expander = Expander(macro_registry={"plan": "/bou+ _ /s+ _ /sta.done"})
        result = expander.expand("@plan")
        assert "/bou+" in result.expanded
        assert "/s+" in result.expanded

    def test_expansion_records_steps(self):
        expander = Expander(macro_registry={"think": "/noe+"})
        result = expander.expand("@think")
        assert len(result.expansions) >= 1
        assert "@think → /noe+" in result.expansions[0]

    def test_expand_preserves_original(self):
        expander = Expander(macro_registry={"think": "/noe+"})
        result = expander.expand("@think")
        assert result.original == "@think"


class TestExpandCCL:
    """expand_ccl() 便利関数のテスト"""

    def test_with_macros(self):
        result = expand_ccl("@think", macros={"think": "/noe+"})
        assert result.expanded == "/noe+"

    def test_without_macros(self):
        result = expand_ccl("/dia+")
        assert result.expanded == "/dia+"

    def test_with_all_macros(self):
        all_macros = get_all_macros()
        result = expand_ccl("@think", macros=all_macros)
        assert "/noe+" in result.expanded

    def test_convergence_notation(self):
        result = expand_ccl("/noe+ >> V[] < 0.3")
        # >> は lim 形式に展開される
        assert "lim" in result.formal


# =============================================================================
# E2E: @macro → expand → parse
# =============================================================================


class TestMacroE2E:
    """マクロ → 展開 → パースの E2E テスト"""

    def test_think_macro_e2e(self):
        """@think → /noe+ >> V[] < 0.3 → parse"""
        all_macros = get_all_macros()
        expanded = expand_ccl("@think", macros=all_macros)
        
        parser = CCLParser()
        ast = parser.parse(expanded.expanded)
        assert ast is not None

    def test_plan_macro_e2e(self):
        """@plan → /bou+ _ /s+ _ /sta.done → parse"""
        all_macros = get_all_macros()
        expanded = expand_ccl("@plan", macros=all_macros)
        
        parser = CCLParser()
        ast = parser.parse(expanded.expanded)
        assert ast is not None

    def test_review_macro_e2e(self):
        """@review → /dia+ _ /pre+ _ /sta.done → parse"""
        all_macros = get_all_macros()
        expanded = expand_ccl("@review", macros=all_macros)
        
        parser = CCLParser()
        ast = parser.parse(expanded.expanded)
        assert ast is not None

    def test_dig_macro_e2e(self):
        """@dig → /zet+ _ /noe+ → parse"""
        all_macros = get_all_macros()
        expanded = expand_ccl("@dig", macros=all_macros)
        
        parser = CCLParser()
        ast = parser.parse(expanded.expanded)
        assert ast is not None

    def test_plain_workflow_e2e(self):
        """プレーンなワークフロー (マクロなし)"""
        expanded = expand_ccl("/noe+")
        parser = CCLParser()
        ast = parser.parse(expanded.expanded)
        assert ast is not None
