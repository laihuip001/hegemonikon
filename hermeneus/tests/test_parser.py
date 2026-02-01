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

from hermeneus.src import (
    parse_ccl, compile_ccl,
    Workflow, Sequence, ConvergenceLoop, Fusion, Oscillation,
    ForLoop, IfCondition, WhileLoop, Lambda,
    OpType
)


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


# =============================================================================
# Run
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
