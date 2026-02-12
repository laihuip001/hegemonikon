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
    
    # PURPOSE: 単純なワークフロー
    def test_simple_workflow(self):
        """単純なワークフロー"""
        ast = parse_ccl("/noe")
        assert isinstance(ast, Workflow)
        assert ast.id == "noe"
    
    # PURPOSE: /noe+ (深化)
    def test_workflow_with_deepen(self):
        """/noe+ (深化)"""
        ast = parse_ccl("/noe+")
        assert isinstance(ast, Workflow)
        assert ast.id == "noe"
        assert OpType.DEEPEN in ast.operators
    
    # PURPOSE: /bou- (縮約)
    def test_workflow_with_condense(self):
        """/bou- (縮約)"""
        ast = parse_ccl("/bou-")
        assert isinstance(ast, Workflow)
        assert ast.id == "bou"
        assert OpType.CONDENSE in ast.operators
    
    # PURPOSE: /noe+^ (深化 + 上昇)
    def test_workflow_with_multiple_ops(self):
        """/noe+^ (深化 + 上昇)"""
        ast = parse_ccl("/noe+^")
        assert isinstance(ast, Workflow)
        assert OpType.DEEPEN in ast.operators
        assert OpType.ASCEND in ast.operators
    
    # PURPOSE: /s! (全展開)
    def test_workflow_expand(self):
        """/s! (全展開)"""
        ast = parse_ccl("/s!")
        assert isinstance(ast, Workflow)
        assert OpType.EXPAND in ast.operators


class TestSequence:
    """シーケンスのテスト"""
    
    # PURPOSE: /s+_/ene
    def test_simple_sequence(self):
        """/s+_/ene"""
        ast = parse_ccl("/s+_/ene")
        assert isinstance(ast, Sequence)
        assert len(ast.steps) == 2
        assert ast.steps[0].id == "s"
        assert ast.steps[1].id == "ene"
    
    # PURPOSE: /boot_/bou_/ene
    def test_three_step_sequence(self):
        """/boot_/bou_/ene"""
        ast = parse_ccl("/boot_/bou_/ene")
        assert isinstance(ast, Sequence)
        assert len(ast.steps) == 3


class TestConvergenceLoop:
    """収束ループのテスト"""
    
    # PURPOSE: /noe+ >> V[] < 0.3
    def test_simple_convergence(self):
        """/noe+ >> V[] < 0.3"""
        ast = parse_ccl("/noe+ >> V[] < 0.3")
        assert isinstance(ast, ConvergenceLoop)
        assert isinstance(ast.body, Workflow)
        assert ast.condition.var == "V[]"
        assert ast.condition.op == "<"
        assert ast.condition.value == 0.3
    
    # PURPOSE: lim[V[] < 0.3]{/noe+}
    def test_lim_formal(self):
        """lim[V[] < 0.3]{/noe+}"""
        ast = parse_ccl("lim[V[] < 0.3]{/noe+}")
        assert isinstance(ast, ConvergenceLoop)
        assert ast.condition.value == 0.3


class TestFusionAndOscillation:
    """融合と振動のテスト"""
    
    # PURPOSE: /noe * /dia
    def test_fusion(self):
        """/noe * /dia"""
        ast = parse_ccl("/noe * /dia")
        assert isinstance(ast, Fusion)
    
    # PURPOSE: /u+ ~ /noe!
    def test_oscillation(self):
        """/u+ ~ /noe!"""
        ast = parse_ccl("/u+ ~ /noe!")
        assert isinstance(ast, Oscillation)


class TestCPLControlStructures:
    """CPL v2.0 制御構文のテスト"""
    
    # PURPOSE: F:[×3]{/dia}
    def test_for_loop_count(self):
        """F:[×3]{/dia}"""
        ast = parse_ccl("F:[×3]{/dia}")
        assert isinstance(ast, ForLoop)
        assert ast.iterations == 3
    
    # PURPOSE: I:[V[] > 0.5]{/noe+}
    def test_if_condition(self):
        """I:[V[] > 0.5]{/noe+}"""
        ast = parse_ccl("I:[V[] > 0.5]{/noe+}")
        assert isinstance(ast, IfCondition)
        assert ast.condition.op == ">"
    
    # PURPOSE: I:[V[] > 0.5]{/noe+} E:{/noe-}
    def test_if_else(self):
        """I:[V[] > 0.5]{/noe+} E:{/noe-}"""
        ast = parse_ccl("I:[V[] > 0.5]{/noe+} E:{/noe-}")
        assert isinstance(ast, IfCondition)
        assert ast.else_branch is not None
    
    # PURPOSE: W:[E[] > 0.3]{/dia}
    def test_while_loop(self):
        """W:[E[] > 0.3]{/dia}"""
        ast = parse_ccl("W:[E[] > 0.3]{/dia}")
        assert isinstance(ast, WhileLoop)
    
    # PURPOSE: L:[wf]{wf+}
    def test_lambda(self):
        """L:[wf]{wf+}"""
        ast = parse_ccl("L:[wf]{wf+}")
        assert isinstance(ast, Lambda)
        assert "wf" in ast.params


class TestCompilation:
    """コンパイル統合テスト"""
    
    # PURPOSE: 単純なコンパイル
    def test_compile_simple(self):
        """単純なコンパイル"""
        lmql = compile_ccl("/noe+")
        assert "@lmql.query" in lmql
        assert "def ccl_noe" in lmql
    
    # PURPOSE: シーケンスのコンパイル
    def test_compile_sequence(self):
        """シーケンスのコンパイル"""
        lmql = compile_ccl("/s+_/ene")
        assert "Step 1" in lmql
        assert "Step 2" in lmql
    
    # PURPOSE: 収束ループのコンパイル
    def test_compile_convergence(self):
        """収束ループのコンパイル"""
        lmql = compile_ccl("/noe+ >> V[] < 0.3")
        assert "MAX_ITERATIONS" in lmql
        assert "while" in lmql.lower()


class TestProcessOperators:
    """Process Layer 演算子のテスト (~*, ~!, \\, (), {})"""
    
    # PURPOSE: /dia+~*/noe (収束振動)
    def test_convergent_oscillation(self):
        """/dia+~*/noe (収束振動)"""
        ast = parse_ccl("/dia+~*/noe")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is True
        assert ast.divergent is False
    
    # PURPOSE: /dia+~!/noe (発散振動)
    def test_divergent_oscillation(self):
        """/dia+~!/noe (発散振動)"""
        ast = parse_ccl("/dia+~!/noe")
        assert isinstance(ast, Oscillation)
        assert ast.divergent is True
        assert ast.convergent is False
    
    # PURPOSE: /dia+ ~ /noe (通常振動、既存互換)
    def test_plain_oscillation_unchanged(self):
        """/dia+ ~ /noe (通常振動、既存互換)"""
        ast = parse_ccl("/dia+ ~ /noe")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is False
        assert ast.divergent is False
    
    # PURPOSE: (/dia+~*/noe) — 括弧グループの剥離
    def test_parenthesized_group(self):
        """(/dia+~*/noe) — 括弧グループの剥離"""
        ast = parse_ccl("(/dia+~*/noe)")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is True
    
    # PURPOSE: {/dia+~*/noe} — ブレースグループの剥離
    def test_brace_group(self):
        """{/dia+~*/noe} — ブレースグループの剥離"""
        ast = parse_ccl("{/dia+~*/noe}")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is True
    
    # PURPOSE: \pan+ — Colimit 演算子
    def test_colimit(self):
        """\\pan+ — Colimit 演算子"""
        from hermeneus.src.ccl_ast import ColimitExpansion
        ast = parse_ccl("\\pan+")
        assert isinstance(ast, ColimitExpansion)
        assert isinstance(ast.body, Workflow)
        assert ast.body.id == "pan"
    
    # PURPOSE: (/dia+~*/noe)~*/pan+ — ネストされた収束振動
    def test_nested_convergent(self):
        """(/dia+~*/noe)~*/pan+ — ネストされた収束振動"""
        ast = parse_ccl("(/dia+~*/noe)~*/pan+")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is True
        # left は /dia+~*/noe の Oscillation
        assert isinstance(ast.left, Oscillation)
        assert ast.left.convergent is True
    
    # PURPOSE: {(/dia+~*/noe)~*/pan+} — マクロ前半
    def test_full_macro_group_a(self):
        """{(/dia+~*/noe)~*/pan+} — マクロ前半"""
        ast = parse_ccl("{(/dia+~*/noe)~*/pan+}")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is True
    
    # PURPOSE: {(/dia+~*/noe)~*\pan+} — マクロ後半 (Colimit 含む)
    def test_full_macro_group_b(self):
        """{(/dia+~*/noe)~*\\pan+} — マクロ後半 (Colimit 含む)"""
        from hermeneus.src.ccl_ast import ColimitExpansion
        ast = parse_ccl("{(/dia+~*/noe)~*\\pan+}")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is True
        assert isinstance(ast.right, ColimitExpansion)
    
    # PURPOSE: 完全マクロ: {(/dia+~*/noe)~*/pan+}~*{(/dia+~*/noe)~*\pan+}
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
    
    # PURPOSE: /u+*^/u^ — 基本的な *^ 融合
    def test_fusion_meta_basic(self):
        """/u+*^/u^ — 基本的な *^ 融合"""
        ast = parse_ccl("/u+*^/u^")
        assert isinstance(ast, Fusion)
        assert ast.meta_display is True
        assert isinstance(ast.left, Workflow)
        assert ast.left.id == "u"
        assert isinstance(ast.right, Workflow)
        assert ast.right.id == "u"
    
    # PURPOSE: *^ と * の区別
    def test_fusion_meta_vs_plain(self):
        """*^ と * の区別"""
        ast_meta = parse_ccl("/noe*^/dia")
        ast_plain = parse_ccl("/noe*/dia")
        assert isinstance(ast_meta, Fusion)
        assert isinstance(ast_plain, Fusion)
        assert ast_meta.meta_display is True
        assert ast_plain.meta_display is False
    
    # PURPOSE: /dox+*^/u+_/bye+ — マクロ @learn 相当
    def test_fusion_meta_in_sequence(self):
        """/dox+*^/u+_/bye+ — マクロ @learn 相当"""
        ast = parse_ccl("/dox+*^/u+_/bye+")
        assert isinstance(ast, Sequence)
        assert isinstance(ast.steps[0], Fusion)
        assert ast.steps[0].meta_display is True


class TestPipeline:
    """パイプライン (|>) のテスト"""
    
    # PURPOSE: /noe+|>/dia+ — 基本パイプライン
    def test_pipeline_basic(self):
        """/noe+|>/dia+ — 基本パイプライン"""
        from hermeneus.src.ccl_ast import Pipeline
        ast = parse_ccl("/noe+|>/dia+")
        assert isinstance(ast, Pipeline)
        assert len(ast.steps) == 2
        assert ast.steps[0].id == "noe"
        assert ast.steps[1].id == "dia"
    
    # PURPOSE: /noe+|>/dia+|>/ene — 3段パイプライン
    def test_pipeline_three_steps(self):
        """/noe+|>/dia+|>/ene — 3段パイプライン"""
        from hermeneus.src.ccl_ast import Pipeline
        ast = parse_ccl("/noe+|>/dia+|>/ene")
        assert isinstance(ast, Pipeline)
        assert len(ast.steps) == 3
    
    # PURPOSE: /boot_/noe+|>/dia+ — |> は _ より弱い結合力 → Pipeline(Seq(boot,noe+), dia+)
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
    
    # PURPOSE: /noe+||/dia+ — 基本並列
    def test_parallel_basic(self):
        """/noe+||/dia+ — 基本並列"""
        from hermeneus.src.ccl_ast import Parallel
        ast = parse_ccl("/noe+||/dia+")
        assert isinstance(ast, Parallel)
        assert len(ast.branches) == 2
        assert ast.branches[0].id == "noe"
        assert ast.branches[1].id == "dia"
    
    # PURPOSE: /noe+||/dia+||/ene — 3並列
    def test_parallel_three_branches(self):
        """/noe+||/dia+||/ene — 3並列"""
        from hermeneus.src.ccl_ast import Parallel
        ast = parse_ccl("/noe+||/dia+||/ene")
        assert isinstance(ast, Parallel)
        assert len(ast.branches) == 3
    
    # PURPOSE: /boot_/noe+||/dia+ — || は _ より弱い結合力 → Parallel(Seq(boot,noe+), dia+)
    def test_parallel_in_sequence(self):
        """/boot_/noe+||/dia+ — || は _ より弱い結合力 → Parallel(Seq(boot,noe+), dia+)"""
        from hermeneus.src.ccl_ast import Parallel
        ast = parse_ccl("/boot_/noe+||/dia+")
        assert isinstance(ast, Parallel)
        assert len(ast.branches) == 2
        assert isinstance(ast.branches[0], Sequence)  # /boot_/noe+ がシーケンス
        assert isinstance(ast.branches[1], Workflow)   # /dia+ が単体 WF


class TestElifAndLet:
    """EI: (ELIF) と let 構文のテスト"""
    
    # PURPOSE: EI:[cond]{body} — トップレベル EI: は IF として処理
    def test_elif_toplevel(self):
        """EI:[cond]{body} — トップレベル EI: は IF として処理"""
        ast = parse_ccl("EI:[V[]>0.5]{/noe+}")
        assert isinstance(ast, IfCondition)
        assert ast.condition.op == ">"
    
    # PURPOSE: I:[V[]>0.5]{/noe+}EI:[V[]<0.3]{/ene+}E:{/zet}
    def test_if_elif_else_chain(self):
        """I:[V[]>0.5]{/noe+}EI:[V[]<0.3]{/ene+}E:{/zet}"""
        ast = parse_ccl("I:[V[]>0.5]{/noe+}EI:[V[]<0.3]{/ene+}E:{/zet}")
        assert isinstance(ast, IfCondition)
        assert ast.else_branch is not None
        # else_branch は ネストされた IfCondition (EI → I 変換)
        assert isinstance(ast.else_branch, IfCondition)
        assert ast.else_branch.else_branch is not None  # E:{/zet}
    
    # PURPOSE: let x = /noe — 変数束縛 (@ なし)
    def test_let_variable_binding(self):
        """let x = /noe — 変数束縛 (@ なし)"""
        from hermeneus.src.ccl_ast import LetBinding
        ast = parse_ccl("let x = /noe")
        assert isinstance(ast, LetBinding)
        assert ast.name == "x"
        assert isinstance(ast.body, Workflow)
        assert ast.body.id == "noe"
    
    # PURPOSE: let @think = /noe+_/dia — マクロ定義 (@ 付き)
    def test_let_macro_definition(self):
        """let @think = /noe+_/dia — マクロ定義 (@ 付き)"""
        from hermeneus.src.ccl_ast import LetBinding
        ast = parse_ccl("let @think = /noe+_/dia")
        assert isinstance(ast, LetBinding)
        assert ast.name == "think"
        assert isinstance(ast.body, Sequence)
    
    # PURPOSE: let result = /noe+~/dia — 複雑な式
    def test_let_complex_expression(self):
        """let result = /noe+~/dia — 複雑な式"""
        from hermeneus.src.ccl_ast import LetBinding
        ast = parse_ccl("let result = /noe+~/dia")
        assert isinstance(ast, LetBinding)
        assert ast.name == "result"
        assert isinstance(ast.body, Oscillation)


class TestTaggedBlocks:
    """V:/C:/R:/M: タグ付きブロックのテスト"""
    
    # PURPOSE: V:{/noe~/dia} — 検証ブロック
    def test_verify_block(self):
        """V:{/noe~/dia} — 検証ブロック"""
        from hermeneus.src.ccl_ast import TaggedBlock
        ast = parse_ccl("V:{/noe~/dia}")
        assert isinstance(ast, TaggedBlock)
        assert ast.tag == "V"
    
    # PURPOSE: C:{/dia+_/ene+} — サイクルブロック
    def test_cycle_block(self):
        """C:{/dia+_/ene+} — サイクルブロック"""
        from hermeneus.src.ccl_ast import TaggedBlock
        ast = parse_ccl("C:{/dia+_/ene+}")
        assert isinstance(ast, TaggedBlock)
        assert ast.tag == "C"
    
    # PURPOSE: R:{/u+} — 累積融合ブロック
    def test_reduce_block(self):
        """R:{/u+} — 累積融合ブロック"""
        from hermeneus.src.ccl_ast import TaggedBlock
        ast = parse_ccl("R:{/u+}")
        assert isinstance(ast, TaggedBlock)
        assert ast.tag == "R"
    
    # PURPOSE: M:{/dox-} — 記憶ブロック
    def test_memo_block(self):
        """M:{/dox-} — 記憶ブロック"""
        from hermeneus.src.ccl_ast import TaggedBlock
        ast = parse_ccl("M:{/dox-}")
        assert isinstance(ast, TaggedBlock)
        assert ast.tag == "M"


# =============================================================================
# Run
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
