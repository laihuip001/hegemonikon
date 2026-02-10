# PROOF: [L3/テスト] <- hermeneus/tests/ Hermēneus パーサーテスト
"""
Hermēneus Parser Unit Tests

CCLParser の単体テスト。
"""

import pytest
import sys
from pathlib import Path

# パッケージパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hermeneus.src import compile_ccl
from hermeneus.src.ccl_ast import Workflow, Sequence, ConvergenceLoop, Fusion, Oscillation, ForLoop, IfCondition, WhileLoop, Lambda, OpType
from hermeneus.src.parser import parse_ccl


class TestBasicWorkflows:
    """基本ワークフローのテスト"""
    
    def test_simple_workflow(self):
        """単純なワークフロー"""
        ast = parse_ccl("/noe")
        assert isinstance(ast, Workflow)
        assert ast.id == "noe"
    
    def test_workflow_with_deepen(self):
        """/noe+ (深化)"""
        ast = parse_ccl("/noe+")
        assert isinstance(ast, Workflow)
        assert ast.id == "noe"
        assert OpType.DEEPEN in ast.operators
    
    def test_workflow_with_condense(self):
        """/bou- (縮約)"""
        ast = parse_ccl("/bou-")
        assert isinstance(ast, Workflow)
        assert ast.id == "bou"
        assert OpType.CONDENSE in ast.operators
    
    def test_workflow_with_multiple_ops(self):
        """/noe+^ (深化 + 上昇)"""
        ast = parse_ccl("/noe+^")
        assert isinstance(ast, Workflow)
        assert OpType.DEEPEN in ast.operators
        assert OpType.ASCEND in ast.operators
    
    def test_workflow_expand(self):
        """/s! (全展開)"""
        ast = parse_ccl("/s!")
        assert isinstance(ast, Workflow)
        assert OpType.EXPAND in ast.operators


class TestSequence:
    """シーケンスのテスト"""
    
    def test_simple_sequence(self):
        """/s+_/ene"""
        ast = parse_ccl("/s+_/ene")
        assert isinstance(ast, Sequence)
        assert len(ast.steps) == 2
        assert ast.steps[0].id == "s"
        assert ast.steps[1].id == "ene"
    
    def test_three_step_sequence(self):
        """/boot_/bou_/ene"""
        ast = parse_ccl("/boot_/bou_/ene")
        assert isinstance(ast, Sequence)
        assert len(ast.steps) == 3


class TestConvergenceLoop:
    """収束ループのテスト"""
    
    def test_simple_convergence(self):
        """/noe+ >> V[] < 0.3"""
        ast = parse_ccl("/noe+ >> V[] < 0.3")
        assert isinstance(ast, ConvergenceLoop)
        assert isinstance(ast.body, Workflow)
        assert ast.condition.var == "V[]"
        assert ast.condition.op == "<"
        assert ast.condition.value == 0.3
    
    def test_lim_formal(self):
        """lim[V[] < 0.3]{/noe+}"""
        ast = parse_ccl("lim[V[] < 0.3]{/noe+}")
        assert isinstance(ast, ConvergenceLoop)
        assert ast.condition.value == 0.3


class TestFusionAndOscillation:
    """融合と振動のテスト"""
    
    def test_fusion(self):
        """/noe * /dia"""
        ast = parse_ccl("/noe * /dia")
        assert isinstance(ast, Fusion)
    
    def test_oscillation(self):
        """/u+ ~ /noe!"""
        ast = parse_ccl("/u+ ~ /noe!")
        assert isinstance(ast, Oscillation)


class TestCPLControlStructures:
    """CPL v2.0 制御構文のテスト"""
    
    def test_for_loop_count(self):
        """F:[×3]{/dia}"""
        ast = parse_ccl("F:[×3]{/dia}")
        assert isinstance(ast, ForLoop)
        assert ast.iterations == 3
    
    def test_if_condition(self):
        """I:[V[] > 0.5]{/noe+}"""
        ast = parse_ccl("I:[V[] > 0.5]{/noe+}")
        assert isinstance(ast, IfCondition)
        assert ast.condition.op == ">"
    
    def test_if_else(self):
        """I:[V[] > 0.5]{/noe+} E:{/noe-}"""
        ast = parse_ccl("I:[V[] > 0.5]{/noe+} E:{/noe-}")
        assert isinstance(ast, IfCondition)
        assert ast.else_branch is not None
    
    def test_while_loop(self):
        """W:[E[] > 0.3]{/dia}"""
        ast = parse_ccl("W:[E[] > 0.3]{/dia}")
        assert isinstance(ast, WhileLoop)
    
    def test_lambda(self):
        """L:[wf]{wf+}"""
        ast = parse_ccl("L:[wf]{wf+}")
        assert isinstance(ast, Lambda)
        assert "wf" in ast.params


class TestCompilation:
    """コンパイル統合テスト"""
    
    def test_compile_simple(self):
        """単純なコンパイル"""
        lmql = compile_ccl("/noe+")
        assert "@lmql.query" in lmql
        assert "def ccl_noe" in lmql
    
    def test_compile_sequence(self):
        """シーケンスのコンパイル"""
        lmql = compile_ccl("/s+_/ene")
        assert "Step 1" in lmql
        assert "Step 2" in lmql
    
    def test_compile_convergence(self):
        """収束ループのコンパイル"""
        lmql = compile_ccl("/noe+ >> V[] < 0.3")
        assert "MAX_ITERATIONS" in lmql
        assert "while" in lmql.lower()


class TestProcessOperators:
    """Process Layer 演算子のテスト (~*, ~!, \\, (), {})"""
    
    def test_convergent_oscillation(self):
        """/dia+~*/noe (収束振動)"""
        ast = parse_ccl("/dia+~*/noe")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is True
        assert ast.divergent is False
    
    def test_divergent_oscillation(self):
        """/dia+~!/noe (発散振動)"""
        ast = parse_ccl("/dia+~!/noe")
        assert isinstance(ast, Oscillation)
        assert ast.divergent is True
        assert ast.convergent is False
    
    def test_plain_oscillation_unchanged(self):
        """/dia+ ~ /noe (通常振動、既存互換)"""
        ast = parse_ccl("/dia+ ~ /noe")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is False
        assert ast.divergent is False
    
    def test_parenthesized_group(self):
        """(/dia+~*/noe) — 括弧グループの剥離"""
        ast = parse_ccl("(/dia+~*/noe)")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is True
    
    def test_brace_group(self):
        """{/dia+~*/noe} — ブレースグループの剥離"""
        ast = parse_ccl("{/dia+~*/noe}")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is True
    
    def test_colimit(self):
        """\\pan+ — Colimit 演算子"""
        from hermeneus.src.ccl_ast import ColimitExpansion
        ast = parse_ccl("\\pan+")
        assert isinstance(ast, ColimitExpansion)
        assert isinstance(ast.body, Workflow)
        assert ast.body.id == "pan"
    
    def test_nested_convergent(self):
        """(/dia+~*/noe)~*/pan+ — ネストされた収束振動"""
        ast = parse_ccl("(/dia+~*/noe)~*/pan+")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is True
        # left は /dia+~*/noe の Oscillation
        assert isinstance(ast.left, Oscillation)
        assert ast.left.convergent is True
    
    def test_full_macro_group_a(self):
        """{(/dia+~*/noe)~*/pan+} — マクロ前半"""
        ast = parse_ccl("{(/dia+~*/noe)~*/pan+}")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is True
    
    def test_full_macro_group_b(self):
        """{(/dia+~*/noe)~*\\pan+} — マクロ後半 (Colimit 含む)"""
        from hermeneus.src.ccl_ast import ColimitExpansion
        ast = parse_ccl("{(/dia+~*/noe)~*\\pan+}")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is True
        assert isinstance(ast.right, ColimitExpansion)
    
    def test_full_macro(self):
        """完全マクロ: {(/dia+~*/noe)~*/pan+}~*{(/dia+~*/noe)~*\\pan+}"""
        ast = parse_ccl("{(/dia+~*/noe)~*/pan+}~*{(/dia+~*/noe)~*\\pan+}")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is True
        # left = グループ A, right = グループ B
        assert isinstance(ast.left, Oscillation)
        assert isinstance(ast.right, Oscillation)


class TestFusionMeta:
    """融合メタ表示 (*^) のテスト"""
    
    def test_fusion_meta_basic(self):
        """/u+*^/u^ — 基本的な *^ 融合"""
        ast = parse_ccl("/u+*^/u^")
        assert isinstance(ast, Fusion)
        assert ast.meta_display is True
        assert isinstance(ast.left, Workflow)
        assert ast.left.id == "u"
        assert isinstance(ast.right, Workflow)
        assert ast.right.id == "u"
    
    def test_fusion_meta_vs_plain(self):
        """*^ と * の区別"""
        ast_meta = parse_ccl("/noe*^/dia")
        ast_plain = parse_ccl("/noe*/dia")
        assert isinstance(ast_meta, Fusion)
        assert isinstance(ast_plain, Fusion)
        assert ast_meta.meta_display is True
        assert ast_plain.meta_display is False
    
    def test_fusion_meta_in_sequence(self):
        """/dox+*^/u+_/bye+ — マクロ @learn 相当"""
        ast = parse_ccl("/dox+*^/u+_/bye+")
        assert isinstance(ast, Sequence)
        assert isinstance(ast.steps[0], Fusion)
        assert ast.steps[0].meta_display is True


class TestPipeline:
    """パイプライン (|>) のテスト"""
    
    def test_pipeline_basic(self):
        """/noe+|>/dia+ — 基本パイプライン"""
        from hermeneus.src.ccl_ast import Pipeline
        ast = parse_ccl("/noe+|>/dia+")
        assert isinstance(ast, Pipeline)
        assert len(ast.steps) == 2
        assert ast.steps[0].id == "noe"
        assert ast.steps[1].id == "dia"
    
    def test_pipeline_three_steps(self):
        """/noe+|>/dia+|>/ene — 3段パイプライン"""
        from hermeneus.src.ccl_ast import Pipeline
        ast = parse_ccl("/noe+|>/dia+|>/ene")
        assert isinstance(ast, Pipeline)
        assert len(ast.steps) == 3
    
    def test_pipeline_in_sequence(self):
        """/boot_/noe+|>/dia+ — |> は _ より弱い結合力 → Pipeline(Seq(boot,noe+), dia+)"""
        from hermeneus.src.ccl_ast import Pipeline
        ast = parse_ccl("/boot_/noe+|>/dia+")
        assert isinstance(ast, Pipeline)
        assert len(ast.steps) == 2
        assert isinstance(ast.steps[0], Sequence)  # /boot_/noe+ がシーケンス
        assert isinstance(ast.steps[1], Workflow)   # /dia+ が単体 WF


class TestParallel:
    """並列実行 (||) のテスト"""
    
    def test_parallel_basic(self):
        """/noe+||/dia+ — 基本並列"""
        from hermeneus.src.ccl_ast import Parallel
        ast = parse_ccl("/noe+||/dia+")
        assert isinstance(ast, Parallel)
        assert len(ast.branches) == 2
        assert ast.branches[0].id == "noe"
        assert ast.branches[1].id == "dia"
    
    def test_parallel_three_branches(self):
        """/noe+||/dia+||/ene — 3並列"""
        from hermeneus.src.ccl_ast import Parallel
        ast = parse_ccl("/noe+||/dia+||/ene")
        assert isinstance(ast, Parallel)
        assert len(ast.branches) == 3
    
    def test_parallel_in_sequence(self):
        """/boot_/noe+||/dia+ — || は _ より弱い結合力 → Parallel(Seq(boot,noe+), dia+)"""
        from hermeneus.src.ccl_ast import Parallel
        ast = parse_ccl("/boot_/noe+||/dia+")
        assert isinstance(ast, Parallel)
        assert len(ast.branches) == 2
        assert isinstance(ast.branches[0], Sequence)  # /boot_/noe+ がシーケンス
        assert isinstance(ast.branches[1], Workflow)   # /dia+ が単体 WF


# =============================================================================
# Run
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
