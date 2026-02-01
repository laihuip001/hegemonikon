# PROOF: [L3/テスト] Synergeia 統合テスト
"""
Synergeia Integration Tests — プロジェクト間連携のテスト

Tests:
    - Hermeneus CCL Compiler 統合
    - FEP Selector 統合
    - マクロローダー統合
"""

import pytest
from pathlib import Path


class TestHermeneusIntegration:
    """Hermeneus 統合テスト"""
    
    def test_hermeneus_available(self):
        """Hermeneus がインポート可能"""
        from synergeia.coordinator import HERMENEUS_AVAILABLE
        assert HERMENEUS_AVAILABLE is True
    
    def test_standard_macros_loaded(self):
        """標準マクロがロードされている"""
        from synergeia.coordinator import STANDARD_MACROS
        assert len(STANDARD_MACROS) >= 5
        assert "think" in STANDARD_MACROS
        assert "scoped" in STANDARD_MACROS
    
    def test_execute_hermeneus_compile(self):
        """CCL を LMQL にコンパイル"""
        from synergeia.coordinator import execute_hermeneus
        result = execute_hermeneus("/noe+", "test", compile_only=True)
        assert result["status"] == "compiled"
        assert "lmql" in result
        assert "macros_available" in result
    
    def test_execute_hermeneus_with_convergence(self):
        """収束ループをコンパイル"""
        from synergeia.coordinator import execute_hermeneus
        result = execute_hermeneus("/noe+ >> V[] < 0.3", "test")
        assert result["status"] == "success"
        assert result["ast_type"] == "ConvergenceLoop"


class TestFEPSelectorIntegration:
    """FEP Selector 統合テスト"""
    
    def test_fep_selector_available(self):
        """FEP Selector がインポート可能"""
        from synergeia.coordinator import FEP_SELECTOR_AVAILABLE
        assert FEP_SELECTOR_AVAILABLE is True
    
    def test_select_thread_with_fep(self):
        """FEP ベースのスレッド選択"""
        from synergeia.coordinator import select_thread
        
        # 高複雑度 → antigravity
        thread = select_thread("/noe+ >> V[] < 0.3")
        assert thread == "antigravity"
        
        # 中複雑度 → claude
        thread = select_thread("/s+ _ /ene")
        assert thread == "claude"
    
    def test_select_thread_fallback(self):
        """FEP 無効時はルールベースにフォールバック"""
        from synergeia.coordinator import select_thread
        thread = select_thread("/unknown+", use_fep=False)
        assert thread == "antigravity"


class TestMacroLoader:
    """マクロローダーテスト"""
    
    def test_load_standard_macros(self):
        """ccl/macros/ からマクロをロード"""
        from hermeneus.src.macros import load_standard_macros
        macros = load_standard_macros()
        assert len(macros) >= 10
        assert "scoped" in macros
        assert "validate" in macros
    
    def test_get_all_macros(self):
        """ビルトイン + 標準マクロを結合"""
        from hermeneus.src.macros import get_all_macros
        macros = get_all_macros()
        # ビルトイン
        assert "think" in macros
        assert "tak" in macros
        # 標準
        assert "scoped" in macros
    
    def test_macro_definition_structure(self):
        """マクロ定義の構造"""
        from hermeneus.src.macros import load_standard_macros, MacroDefinition
        macros = load_standard_macros()
        for name, macro in macros.items():
            assert isinstance(macro, MacroDefinition)
            assert macro.name == name
            assert isinstance(macro.parameters, dict)


class TestEndToEnd:
    """エンドツーエンドテスト"""
    
    def test_full_pipeline(self):
        """CCL → FEP選択 → Hermeneus コンパイル"""
        from synergeia.coordinator import select_thread, execute_hermeneus
        
        ccl = "/noe+ >> V[] < 0.3"
        
        # FEP でスレッド選択
        thread = select_thread(ccl)
        assert thread in ["antigravity", "hermeneus"]
        
        # Hermeneus でコンパイル
        result = execute_hermeneus(ccl, "E2E test")
        assert result["status"] == "success"
        assert "lmql" in result
        assert "convergence_loop" in result["lmql"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
