# PROOF: [L2/Mekhane] <- mekhane/ccl/tests/test_operator_loader.py O1->Zet->Impl
"""G6: dispatch E2E テスト + G9: Linter テスト + operator_loader テスト。"""

import pytest
from pathlib import Path


# PURPOSE: G1: operator_loader のテスト。
class TestOperatorLoader:
    """G1: operator_loader のテスト。"""

    # PURPOSE: load_operators_returns_dict をテストする
    def test_load_operators_returns_dict(self):
        from mekhane.ccl.operator_loader import load_operators
        ops = load_operators()
        assert isinstance(ops, dict)
        assert len(ops) > 10  # 少なくとも基本演算子は存在

    # PURPOSE: コア演算子が全て含まれている。
    def test_core_operators_present(self):
        """コア演算子が全て含まれている。"""
        from mekhane.ccl.operator_loader import load_operators
        ops = load_operators()
        core = {"+", "-", "^", "\\", "*", "~", "_", "!", "'", "~*", ">>", "*^"}
        missing = core - set(ops.keys())
        assert not missing, f"コア演算子が不足: {missing}"

    # PURPOSE: operator_def_fields をテストする
    def test_operator_def_fields(self):
        from mekhane.ccl.operator_loader import load_operators
        ops = load_operators()
        op = ops["+"]
        assert op.symbol == "+"
        assert op.name == "深化"
        assert op.effect  # 空でない

    # PURPOSE: to_definitions_dict をテストする
    def test_to_definitions_dict(self):
        from mekhane.ccl.operator_loader import load_operators, to_definitions_dict
        ops = load_operators()
        compound, single, all_ops = to_definitions_dict(ops)
        assert "*^" in compound
        assert "+" in single
        assert len(all_ops) == len(compound) + len(single)

    # PURPOSE: get_operators_hash をテストする
    def test_get_operators_hash(self):
        from mekhane.ccl.operator_loader import get_operators_hash
        h = get_operators_hash()
        assert isinstance(h, str)
        assert len(h) == 16

    # PURPOSE: operators.md テーブルにない演算子がフォールバックで含まれる。
    def test_fallback_operators(self):
        """operators.md テーブルにない演算子がフォールバックで含まれる。"""
        from mekhane.ccl.operator_loader import load_operators
        ops = load_operators()
        assert "*^" in ops
        assert "?" in ops

    # PURPOSE: `-` がセパレータとして誤除外されない。
    def test_minus_not_excluded(self):
        """`-` がセパレータとして誤除外されない。"""
        from mekhane.ccl.operator_loader import load_operators
        ops = load_operators()
        assert "-" in ops
        assert ops["-"].name == "縮約"


# PURPOSE: G9: ccl_linter のテスト。
class TestCCLLinter:
    """G9: ccl_linter のテスト。"""

    # PURPOSE: clean_expression をテストする
    def test_clean_expression(self):
        from mekhane.ccl.ccl_linter import lint
        warnings = lint("/noe+")
        # パス接頭辞 / の文字は CCL 演算子として登録済み
        assert len([w for w in warnings if w.level == "error"]) == 0

    # PURPOSE: undefined_operator をテストする
    def test_undefined_operator(self):
        from mekhane.ccl.ccl_linter import lint
        warnings = lint("/noe+$zet")
        assert any("未定義演算子: $" in w.message for w in warnings)

    # PURPOSE: conflicting_operators をテストする
    def test_conflicting_operators(self):
        from mekhane.ccl.ccl_linter import lint
        warnings = lint("/bou+_/dia-")
        assert any("+" in w.message and "-" in w.message for w in warnings)

    # PURPOSE: nesting_depth をテストする
    def test_nesting_depth(self):
        from mekhane.ccl.ccl_linter import lint
        # 深度5: (((((x)))))
        deep = "(((((" + "/noe" + ")))))"
        warnings = lint(deep)
        assert any("ネスト深度" in w.message for w in warnings)


# PURPOSE: G6: spec_injector / failure_db 統合テスト。
class TestDispatchIntegration:
    """G6: spec_injector / failure_db 統合テスト。"""

    # PURPOSE: ! を含む式で warned_operators が返される。
    def test_warned_operators_for_dangerous_ops(self):
        """! を含む式で warned_operators が返される。"""
        from mekhane.ccl.spec_injector import get_warned_operators
        warned = get_warned_operators("/noe!")
        assert len(warned) > 0
        assert any("!" in op for op in warned)

    # PURPOSE: *^ を含む式で warned_operators が返される。
    def test_warned_operators_compound(self):
        """*^ を含む式で warned_operators が返される。"""
        from mekhane.ccl.spec_injector import get_warned_operators
        warned = get_warned_operators("/noe*^/dia")
        assert len(warned) > 0

    # PURPOSE: \ を含む式で warned_operators が返される。
    def test_warned_operators_backslash(self):
        """\\ を含む式で warned_operators が返される。"""
        from mekhane.ccl.spec_injector import get_warned_operators
        warned = get_warned_operators(r"/noe\dia")
        assert len(warned) > 0
