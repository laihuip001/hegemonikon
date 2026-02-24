# PROOF: [L2/Mekhane] <- hermeneus/tests/test_dispatch_warnings.py A0->Auto->AddedByCI
"""F7: dispatch.py の警告統合テスト。

spec_injector / failure_db の警告が plan_template に正しく注入されることを検証する。
"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


class TestDispatchWarnings:
    """dispatch の Step 7 警告統合テスト。"""

    def test_expand_operator_triggers_warning(self):
        """'!' 演算子を含む CCL 式で 演算子注意 ブロックが表示される。"""
        from hermeneus.src.dispatch import dispatch

        result = dispatch("/dia!")

        plan = result.get("plan_template", "")
        assert "演算子注意" in plan, "! 含有時に【⚠️ 演算子注意】が表示されるべき"
        assert "階乗" in plan or "全派生同時実行" in plan, "! の正しい意味が表示されるべき"

    def test_deepen_operator_no_warning(self):
        """'+' のみの CCL 式で演算子注意ブロックが表示されない。"""
        from hermeneus.src.dispatch import dispatch

        result = dispatch("/noe+")

        plan = result.get("plan_template", "")
        assert "演算子注意" not in plan, "+ のみでは警告不要"

    def test_expand_operator_triggers_quiz(self):
        """'!' 演算子を含む CCL 式で理解確認クイズが挿入される。"""
        from hermeneus.src.dispatch import dispatch

        result = dispatch("/dia!")

        plan = result.get("plan_template", "")
        assert "理解確認" in plan, "危険演算子含有時に【理解確認】が表示されるべき"

    def test_deepen_operator_no_quiz(self):
        """'+' のみの CCL 式で理解確認クイズが表示されない。"""
        from hermeneus.src.dispatch import dispatch

        result = dispatch("/noe+")

        plan = result.get("plan_template", "")
        assert "理解確認" not in plan, "+ のみではクイズ不要"

    def test_multiple_dangerous_ops(self):
        """複数の危険演算子で複数の警告/クイズが生成される。"""
        from hermeneus.src.dispatch import dispatch

        result = dispatch("/noe!*^/dia")

        plan = result.get("plan_template", "")
        assert "演算子注意" in plan

    def test_spec_injector_definitions_complete(self):
        """spec_injector が基本演算子11個を定義している。"""
        from mekhane.ccl.spec_injector import OPERATOR_DEFINITIONS

        required = {"+", "-", "^", "/", "?", "\\", "*", "~", "_", "!", "'"}
        actual = set(OPERATOR_DEFINITIONS.keys())
        missing = required - actual
        assert not missing, f"OPERATOR_DEFINITIONS に不足: {missing}"


class TestFailureDBIntegration:
    """failure_db の dispatch 連携テスト。"""

    def test_failure_db_warnings_for_expand(self):
        """failure_db が '!' に対して critical 警告を返す。"""
        from mekhane.ccl.learning.failure_db import get_failure_db

        db = get_failure_db()
        warnings = db.get_warnings("/dia!")

        bang_warnings = [w for w in warnings if w.operator == "!"]
        assert len(bang_warnings) >= 1, "! に対する警告がない"
        assert bang_warnings[0].severity == "critical"

    def test_failure_db_no_warnings_for_safe(self):
        """安全な式に対して failure_db が不要な警告を返さない。"""
        from mekhane.ccl.learning.failure_db import get_failure_db

        db = get_failure_db()
        warnings = db.get_warnings("/noe+")

        assert len(warnings) == 0, f"+ のみで警告が出力された: {warnings}"

    def test_failure_db_backslash_warning(self):
        r"""failure_db が '\' に対して warning を返す。"""
        from mekhane.ccl.learning.failure_db import get_failure_db

        db = get_failure_db()
        warnings = db.get_warnings("/noe\\")

        bs_warnings = [w for w in warnings if w.operator == "\\"]
        assert len(bs_warnings) >= 1, r"\ に対する警告がない"
        assert bs_warnings[0].severity == "warning"


class TestCompoundOperators:
    """F8/F10: 複合演算子の parse_operators テスト。"""

    def test_parse_star_caret(self):
        """'*^' が単一の複合演算子として検出される。"""
        from mekhane.ccl.spec_injector import SpecInjector

        injector = SpecInjector()
        ops = injector.parse_operators("/noe*^/dia")
        assert "*^" in ops, "*^ が検出されない"
        # * と ^ が個別に検出されてはいけない (貪欲マッチ)
        assert "*" not in ops, "* が単独で検出された (貪欲マッチ失敗)"
        assert "^" not in ops, "^ が単独で検出された (貪欲マッチ失敗)"

    def test_parse_tilde_star(self):
        """'~*' が単一の複合演算子として検出される。"""
        from mekhane.ccl.spec_injector import SpecInjector

        injector = SpecInjector()
        ops = injector.parse_operators("/noe~*/dia")
        assert "~*" in ops, "~* が検出されない"

    def test_parse_pipeline(self):
        """'>>' が単一の複合演算子として検出される。"""
        from mekhane.ccl.spec_injector import SpecInjector

        injector = SpecInjector()
        ops = injector.parse_operators("/noe >> /dia")
        assert ">>" in ops, ">> が検出されない"

    def test_parse_mixed_operators(self):
        """複合+単一の混在式で正しく分離される。"""
        from mekhane.ccl.spec_injector import SpecInjector

        injector = SpecInjector()
        ops = injector.parse_operators("/noe!*^/dia+")
        assert "*^" in ops, "*^ が検出されない"
        assert "!" in ops, "! が検出されない"
        assert "+" in ops, "+ が検出されない"

    def test_compound_definitions_exist(self):
        """COMPOUND_OPERATORS に 3 種の複合演算子が定義されている。"""
        from mekhane.ccl.spec_injector import COMPOUND_OPERATORS

        required = {"*^", "~*", ">>"}
        actual = set(COMPOUND_OPERATORS.keys())
        missing = required - actual
        assert not missing, f"COMPOUND_OPERATORS に不足: {missing}"

    def test_all_operators_unified(self):
        """ALL_OPERATORS が COMPOUND + SINGLE の合計を含む。"""
        from mekhane.ccl.spec_injector import ALL_OPERATORS, OPERATOR_DEFINITIONS, COMPOUND_OPERATORS

        assert len(ALL_OPERATORS) == len(OPERATOR_DEFINITIONS) + len(COMPOUND_OPERATORS)


class TestGetWarnedOperators:
    """F9: get_warned_operators のテスト。"""

    def test_bang_warned(self):
        """'!' 含有式で '!' が warned set に含まれる。"""
        from mekhane.ccl.spec_injector import get_warned_operators

        warned = get_warned_operators("/dia!")
        assert "!" in warned

    def test_star_caret_warned(self):
        """'*^' 含有式で '*^' が warned set に含まれる。"""
        from mekhane.ccl.spec_injector import get_warned_operators

        warned = get_warned_operators("/noe*^/dia")
        assert "*^" in warned

    def test_backslash_warned(self):
        r"""'\' 含有式で '\' が warned set に含まれる。"""
        from mekhane.ccl.spec_injector import get_warned_operators

        warned = get_warned_operators(r"/noe\dia")
        assert "\\" in warned

    def test_safe_expr_no_warned(self):
        """安全な式で warned set が空。"""
        from mekhane.ccl.spec_injector import get_warned_operators

        warned = get_warned_operators("/noe+")
        assert len(warned) == 0


class TestBackslashOperator:
    r"""F12: '\' 演算子の統合テスト。"""

    def test_backslash_triggers_warning(self):
        r"""'\' 含有式で演算子注意ブロックが表示される。"""
        from hermeneus.src.dispatch import dispatch

        result = dispatch(r"/noe\dia")
        plan = result.get("plan_template", "")
        assert "演算子注意" in plan, r"\ 含有時に警告が表示されるべき"

    def test_backslash_triggers_quiz(self):
        r"""'\' 含有式で理解確認クイズが挿入される。"""
        from hermeneus.src.dispatch import dispatch

        result = dispatch(r"/noe\dia")
        plan = result.get("plan_template", "")
        assert "理解確認" in plan, r"\ は危険演算子なのでクイズが表示されるべき"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
