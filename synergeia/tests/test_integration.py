# PROOF: [L3/テスト] <- synergeia/tests/ Synergeia 統合テスト
"""
Synergeia Integration Tests — プロジェクト間連携のテスト

Tests:
    - Hermeneus CCL Compiler 統合
    - FEP Selector 統合
    - マクロローダー統合
"""

import pytest
from pathlib import Path


# PURPOSE: [L2-auto] Hermeneus 統合テスト
# NOTE: synergeia.coordinator は _archive_v01/ にアーカイブ済み。
# coordinator が復帰するまでスキップ。
coordinator = pytest.importorskip(
    "synergeia.coordinator",
    reason="synergeia.coordinator archived to _archive_v01/",
)


class TestHermeneusIntegration:
    """Hermeneus 統合テスト"""
    
    # PURPOSE: [L2-auto] Hermeneus がインポート可能
    def test_hermeneus_available(self):
        """Hermeneus がインポート可能"""
        assert coordinator.HERMENEUS_AVAILABLE is True
    
    # PURPOSE: [L2-auto] 標準マクロがロードされている
    def test_standard_macros_loaded(self):
        """標準マクロがロードされている"""
        assert len(coordinator.STANDARD_MACROS) >= 5
        assert "think" in coordinator.STANDARD_MACROS
        assert "scoped" in coordinator.STANDARD_MACROS
    
    # PURPOSE: [L2-auto] CCL を LMQL にコンパイル
    def test_execute_hermeneus_compile(self):
        """CCL を LMQL にコンパイル"""
        result = coordinator.execute_hermeneus("/noe+", "test", compile_only=True)
        assert result["status"] == "compiled"
        assert "lmql" in result
        assert "macros_available" in result
    
    # PURPOSE: [L2-auto] 収束ループをコンパイル
    def test_execute_hermeneus_with_convergence(self):
        """収束ループをコンパイル"""
        result = coordinator.execute_hermeneus("/noe+ >> V[] < 0.3", "test")
        assert result["status"] == "success"
        assert result["ast_type"] == "ConvergenceLoop"


# PURPOSE: [L2-auto] FEP Selector 統合テスト
class TestFEPSelectorIntegration:
    """FEP Selector 統合テスト"""
    
    # PURPOSE: [L2-auto] FEP Selector がインポート可能
    def test_fep_selector_available(self):
        """FEP Selector がインポート可能"""
        assert coordinator.FEP_SELECTOR_AVAILABLE is True
    
    # PURPOSE: [L2-auto] FEP ベースのスレッド選択
    def test_select_thread_with_fep(self):
        """FEP ベースのスレッド選択"""
        # 高複雑度 → antigravity
        thread = coordinator.select_thread("/noe+ >> V[] < 0.3")
        assert thread == "antigravity"
        
        # 中複雑度 → claude
        thread = coordinator.select_thread("/s+ _ /ene")
        assert thread == "claude"
    
    # PURPOSE: [L2-auto] FEP 無効時はルールベースにフォールバック
    def test_select_thread_fallback(self):
        """FEP 無効時はルールベースにフォールバック"""
        thread = coordinator.select_thread("/unknown+", use_fep=False)
        assert thread == "antigravity"


# PURPOSE: [L2-auto] マクロローダーテスト
class TestMacroLoader:
    """マクロローダーテスト"""
    
    # PURPOSE: [L2-auto] ccl/macros/ からマクロをロード
    def test_load_standard_macros(self):
        """ccl/macros/ からマクロをロード"""
        from hermeneus.src.macros import load_standard_macros
        macros = load_standard_macros()
        assert len(macros) >= 10
        assert "scoped" in macros
        assert "validate" in macros
    
    # PURPOSE: [L2-auto] ビルトイン + 標準マクロを結合
    def test_get_all_macros(self):
        """ビルトイン + 標準マクロを結合"""
        from hermeneus.src.macros import get_all_macros
        macros = get_all_macros()
        # ビルトイン
        assert "think" in macros
        assert "tak" in macros
        # 標準
        assert "scoped" in macros
    
    # PURPOSE: [L2-auto] マクロ定義の構造
    def test_macro_definition_structure(self):
        """マクロ定義の構造"""
        from hermeneus.src.macros import load_standard_macros, MacroDefinition
        macros = load_standard_macros()
        for name, macro in macros.items():
            assert isinstance(macro, MacroDefinition)
            assert macro.name == name
            assert isinstance(macro.parameters, dict)


# PURPOSE: [L2-auto] エンドツーエンドテスト
class TestEndToEnd:
    """エンドツーエンドテスト"""
    
    # PURPOSE: [L2-auto] CCL → FEP選択 → Hermeneus コンパイル
    def test_full_pipeline(self):
        """CCL → FEP選択 → Hermeneus コンパイル"""
        ccl = "/noe+ >> V[] < 0.3"
        
        # FEP でスレッド選択
        thread = coordinator.select_thread(ccl)
        assert thread in ["antigravity", "hermeneus"]
        
        # Hermeneus でコンパイル
        result = coordinator.execute_hermeneus(ccl, "E2E test")
        assert result["status"] == "success"
        assert "lmql" in result
        assert "convergence_loop" in result["lmql"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
