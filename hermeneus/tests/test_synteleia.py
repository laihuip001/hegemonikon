# PROOF: [L1/テスト] <- hermeneus/tests/ Synteleia 統合テスト
"""
Synteleia Phase 4 TDD テスト — @S マクロ統合

TDD:
- Red: テスト失敗
- Green: 最小実装
- Refactor: 洗練

Test Categories:
1. SynteleiaOrchestrator 基本動作
2. @syn マクロパース
3. Hermeneus 統合 (@syn → Orchestrator)
"""

import pytest
from pathlib import Path
import sys

# パス設定
HEGEMONIKON_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(HEGEMONIKON_ROOT))
sys.path.insert(0, str(HEGEMONIKON_ROOT / "hermeneus"))

from mekhane.synteleia.orchestrator import SynteleiaOrchestrator
from mekhane.synteleia.base import AuditTarget, AuditTargetType


# =============================================================================
# Category 1: SynteleiaOrchestrator 基本動作
# =============================================================================

class TestSynteleiaOrchestrator:
    """SynteleiaOrchestrator の基本機能テスト"""

    # PURPOSE: デフォルトエージェント構成
    def test_init_default_agents(self):
        """デフォルトエージェント構成"""
        orch = SynteleiaOrchestrator()
        
        # Poiēsis: O, S, H (3)
        assert len(orch.poiesis_agents) == 3
        
        # Dokimasia: P, K, A (5: Operator, Logic, Completeness + P, K)
        assert len(orch.dokimasia_agents) == 5
        
        # 合計 8 エージェント
        assert len(orch.agents) == 8

    # PURPOSE: シンプルなコード監査
    def test_audit_simple_code(self):
        """シンプルなコード監査"""
        orch = SynteleiaOrchestrator()
        target = AuditTarget(
            content="def hello():\n    print('Hello, world!')\n",
            target_type=AuditTargetType.CODE
        )
        result = orch.audit(target)
        
        # 結果構造が正しい
        assert result is not None
        assert hasattr(result, "passed")
        assert hasattr(result, "summary")
        assert hasattr(result, "agent_results")

    # PURPOSE: 計画ドキュメント監査
    def test_audit_plan_document(self):
        """計画ドキュメント監査"""
        orch = SynteleiaOrchestrator()
        target = AuditTarget(
            content="# Implementation Plan\n\n## Purpose\n\nTo implement feature X.\n",
            target_type=AuditTargetType.PLAN
        )
        result = orch.audit(target)
        
        assert result is not None
        # 並列実行時、supports() でフィルタリングされるため結果数は変動
        assert len(result.agent_results) >= 7  # 最低7エージェント

    # PURPOSE: レポートフォーマット
    def test_format_report(self):
        """レポートフォーマット"""
        orch = SynteleiaOrchestrator()
        target = AuditTarget(
            content="print('test')",
            target_type=AuditTargetType.CODE
        )
        result = orch.audit(target)
        report = orch.format_report(result)
        
        assert "Hegemonikón Audit Report" in report
        assert "Target:" in report


# =============================================================================
# Category 2: @syn マクロパース
# =============================================================================

class TestSynMacroParsing:
    """@syn マクロのパーサー認識テスト"""

    # PURPOSE: @syn· (内積) パース
    def test_parse_syn_inner(self):
        """@syn· (内積) パース"""
        from hermeneus.src.parser import CCLParser
        
        parser = CCLParser()
        ast = parser.parse("@syn·")
        
        # MacroRef として認識
        assert ast is not None
        assert ast.__class__.__name__ == "MacroRef"
        assert ast.name == "syn·"

    # PURPOSE: @syn× (外積) パース
    def test_parse_syn_outer(self):
        """@syn× (外積) パース"""
        from hermeneus.src.parser import CCLParser
        
        parser = CCLParser()
        ast = parser.parse("@syn×")
        
        assert ast is not None
        assert ast.__class__.__name__ == "MacroRef"
        assert ast.name == "syn×"

    # PURPOSE: @poiesis パース
    def test_parse_poiesis(self):
        """@poiesis パース"""
        from hermeneus.src.parser import CCLParser
        
        parser = CCLParser()
        ast = parser.parse("@poiesis")
        
        assert ast is not None
        assert ast.__class__.__name__ == "MacroRef"
        assert ast.name == "poiesis"

    # PURPOSE: @dokimasia パース
    def test_parse_dokimasia(self):
        """@dokimasia パース"""
        from hermeneus.src.parser import CCLParser
        
        parser = CCLParser()
        ast = parser.parse("@dokimasia")
        
        assert ast is not None
        assert ast.__class__.__name__ == "MacroRef"
        assert ast.name == "dokimasia"

    # PURPOSE: @S{O,A,K} セレクタ付きパース
    def test_parse_syn_with_selector(self):
        """@S{O,A,K} セレクタ付きパース"""
        from hermeneus.src.parser import CCLParser
        
        parser = CCLParser()
        ast = parser.parse("@S{O,A,K}")
        
        assert ast is not None
        assert ast.__class__.__name__ == "MacroRef"
        assert ast.name == "S"
        assert ast.args == ["O,A,K"]  # セレクタは引数として認識

    # PURPOSE: @S- (最小選択) パース
    def test_parse_syn_minimal(self):
        """@S- (最小選択) パース"""
        from hermeneus.src.parser import CCLParser
        
        parser = CCLParser()
        # @S- は @S(-) として解釈されるべき
        ast = parser.parse("@S-")
        
        assert ast is not None


# =============================================================================
# Category 3: Hermeneus 統合 (NEW)
# =============================================================================

class TestHermeneusIntegration:
    """Hermeneus → Synteleia 統合テスト"""

    # PURPOSE: @syn マクロ実行 → SynteleiaOrchestrator 呼び出し
    def test_syn_macro_execution(self):
        """@syn マクロ実行 → SynteleiaOrchestrator 呼び出し"""
        from hermeneus.src import compile_ccl
        
        # @syn· を含む CCL をコンパイル
        lmql = compile_ccl("@syn·")
        
        # LMQL 出力に Synteleia 呼び出しが含まれる
        assert lmql is not None
        # 期待: Synteleia 関連のコードが生成される
        assert "synteleia" in lmql.lower() or "audit" in lmql.lower()

    # PURPOSE: Synteleia 付き CCL 実行
    def test_execute_with_synteleia(self):
        """Synteleia 付き CCL 実行"""
        from hermeneus.src.runtime import execute_ccl
        
        # コンテキスト付きで @syn 実行
        result = execute_ccl(
            "@syn·",
            context="def foo(): return 42"
        )
        
        # Synteleia 監査結果を含む
        assert result is not None
        assert hasattr(result, "output")

    # PURPOSE: @poiesis のみ実行（生成層）
    def test_poiesis_only_execution(self):
        """@poiesis のみ実行（生成層）"""
        from hermeneus.src.runtime import execute_ccl
        
        result = execute_ccl(
            "@poiesis",
            context="print('hello')"
        )
        
        # 結果が返る（具体的内容は実装依存）
        assert result is not None

    # PURPOSE: @dokimasia のみ実行（審査層）
    def test_dokimasia_only_execution(self):
        """@dokimasia のみ実行（審査層）"""
        from hermeneus.src.runtime import execute_ccl
        
        result = execute_ccl(
            "@dokimasia",
            context="if True: pass"
        )
        
        assert result is not None


# =============================================================================
# Category 4: エッジケース
# =============================================================================

class TestEdgeCases:
    """エッジケースと境界条件"""

    # PURPOSE: 空コンテンツ監査
    def test_empty_content_audit(self):
        """空コンテンツ監査"""
        orch = SynteleiaOrchestrator()
        target = AuditTarget(
            content="",
            target_type=AuditTargetType.CODE
        )
        result = orch.audit(target)
        
        # 空でもエラーにならない
        assert result is not None

    # PURPOSE: 大規模コンテンツ監査
    def test_large_content_audit(self):
        """大規模コンテンツ監査"""
        orch = SynteleiaOrchestrator()
        large_code = "x = 1\n" * 1000  # 1000行
        target = AuditTarget(
            content=large_code,
            target_type=AuditTargetType.CODE
        )
        result = orch.audit(target)
        
        assert result is not None

    # PURPOSE: 逐次 vs 並列実行の結果一致
    def test_sequential_vs_parallel(self):
        """逐次 vs 並列実行の結果一致"""
        target = AuditTarget(
            content="def test(): pass",
            target_type=AuditTargetType.CODE
        )
        
        orch_seq = SynteleiaOrchestrator(parallel=False)
        orch_par = SynteleiaOrchestrator(parallel=True)
        
        result_seq = orch_seq.audit(target)
        result_par = orch_par.audit(target)
        
        # 検出件数は一致するはず
        assert len(result_seq.agent_results) == len(result_par.agent_results)


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
