#!/usr/bin/env python3
# PROOF: [L3/テスト] <- hermeneus/tests/
"""
PROOF: [L3/テスト] このファイルは存在しなければならない

CCL v2.0 表現力実証テスト。
20+個の実践的 CCL 式をパースし、表現力のギャップを検出する。
"""

import pytest
from hermeneus.src.parser import CCLParser, parse_ccl
from hermeneus.src.ccl_ast import (
    Workflow, Sequence, Oscillation, Fusion,
    ConvergenceLoop, ColimitExpansion,
    ForLoop, IfCondition, WhileLoop, Lambda,
    MacroRef, OpType,
)


# =============================================================================
# 1. 基本ワークフロー（6シリーズ × 派生）
# =============================================================================


class TestBasicWorkflows:
    """基本ワークフロー式の表現力。"""

    # PURPOSE: Parser
    @pytest.fixture
    def parser(self):
        return CCLParser()

    # --- 1. 単一WF + 派生 ---
    # PURPOSE: /noe+ — 深化
    def test_01_simple_deepen(self, parser):
        """/noe+ — 深化"""
        ast = parser.parse("/noe+")
        assert isinstance(ast, Workflow)
        assert ast.id == "noe"
        assert OpType.DEEPEN in ast.operators

    # PURPOSE: /boot- — 圧縮
    def test_02_simple_condense(self, parser):
        """/boot- — 圧縮"""
        ast = parser.parse("/boot-")
        assert isinstance(ast, Workflow)
        assert ast.id == "boot"
        assert OpType.CONDENSE in ast.operators

    # PURPOSE: /zet? — 問い
    def test_03_query_operator(self, parser):
        """/zet? — 問い"""
        ast = parser.parse("/zet?")
        assert isinstance(ast, Workflow)
        assert OpType.QUERY in ast.operators

    # PURPOSE: /dox' — 変化率
    def test_04_diff_operator(self, parser):
        """/dox' — 変化率"""
        ast = parser.parse("/dox'")
        assert isinstance(ast, Workflow)
        assert OpType.DIFF in ast.operators


# =============================================================================
# 2. 二項演算子（シーケンス、振動、融合、収束）
# =============================================================================


class TestBinaryOperators:
    """二項演算子の表現力。"""

    # PURPOSE: Parser
    @pytest.fixture
    def parser(self):
        return CCLParser()

    # --- 5. シーケンス ---
    # PURPOSE: /noe+_/dia — 逐次実行
    def test_05_sequence(self, parser):
        """/noe+_/dia — 逐次実行"""
        ast = parser.parse("/noe+_/dia")
        assert isinstance(ast, Sequence)
        assert len(ast.steps) == 2
        assert ast.steps[0].id == "noe"
        assert ast.steps[1].id == "dia"

    # --- 6. 三段シーケンス ---
    # PURPOSE: /zet_/noe+_/ene — 問い→認識→行為
    def test_06_triple_sequence(self, parser):
        """/zet_/noe+_/ene — 問い→認識→行為"""
        ast = parser.parse("/zet_/noe+_/ene")
        assert isinstance(ast, Sequence)
        assert len(ast.steps) == 3

    # --- 7. 収束振動 ---
    # PURPOSE: /noe~*/dia — 認識⇄判定（収束）
    def test_07_convergent_oscillation(self, parser):
        """/noe~*/dia — 認識⇄判定（収束）"""
        ast = parser.parse("/noe~*/dia")
        assert isinstance(ast, Oscillation)
        assert ast.convergent is True

    # --- 8. 発散振動 ---
    # PURPOSE: /zet~!/bou — 探求⇄意志（発散）
    def test_08_divergent_oscillation(self, parser):
        """/zet~!/bou — 探求⇄意志（発散）"""
        ast = parser.parse("/zet~!/bou")
        assert isinstance(ast, Oscillation)
        assert ast.divergent is True

    # --- 9. 通常振動 ---
    # PURPOSE: /u~noe — 主観と認識の交互
    def test_09_plain_oscillation(self, parser):
        """/u~noe — 主観と認識の交互"""
        ast = parser.parse("/u~/noe")
        assert isinstance(ast, Oscillation)

    # --- 10. 融合 ---
    # PURPOSE: /noe*/dia — 認識と判定の融合
    def test_10_fusion(self, parser):
        """/noe*/dia — 認識と判定の融合"""
        ast = parser.parse("/noe*/dia")
        assert isinstance(ast, Fusion)

    # --- 11. 収束ループ ---
    # PURPOSE: /noe+ >> V[] < 0.3 — 自由エネルギー最小化
    def test_11_convergence_loop(self, parser):
        """/noe+ >> V[] < 0.3 — 自由エネルギー最小化"""
        ast = parser.parse("/noe+ >> V[] < 0.3")
        assert isinstance(ast, ConvergenceLoop)
        assert ast.condition.var == "V[]"
        assert ast.condition.value == 0.3

    # --- 11a. 融合メタ結合 (*^) ---
    # PURPOSE: /u+*^/u^ — @nous (問いの深化)
    def test_11a_fusion_meta_binding(self, parser):
        """/u+*^/u^ — @nous (問いの深化)"""
        ast = parser.parse("/u+*^/u^")
        assert isinstance(ast, Fusion)
        assert ast.meta_display is True
        assert ast.left.id == "u"
        assert ast.right.id == "u"
        assert OpType.ASCEND in ast.right.operators

    # PURPOSE: /dox+*^/u+_/bye+ — @learn (学習永続化)
    def test_11b_fusion_meta_in_sequence(self, parser):
        """/dox+*^/u+_/bye+ — @learn (学習永続化)"""
        ast = parser.parse("/dox+*^/u+_/bye+")
        assert isinstance(ast, Sequence)
        assert len(ast.steps) == 2
        fusion = ast.steps[0]
        assert isinstance(fusion, Fusion)
        assert fusion.meta_display is True
        assert fusion.left.id == "dox"
        assert fusion.right.id == "u"
        assert ast.steps[1].id == "bye"

    # PURPOSE: /noe*/dia — 通常融合は meta_display=False
    def test_11c_normal_fusion_not_meta(self, parser):
        """/noe*/dia — 通常融合は meta_display=False"""
        ast = parser.parse("/noe*/dia")
        assert isinstance(ast, Fusion)
        assert ast.meta_display is False

    # --- 11d. グループ振動 ~(...) ---
    # PURPOSE: ~(/sop_/noe_/ene_/dia-) — @kyc (認知循環)
    def test_11d_group_oscillation(self, parser):
        """~(/sop_/noe_/ene_/dia-) — @kyc (認知循環)"""
        ast = parser.parse("~(/sop_/noe_/ene_/dia-)")
        assert isinstance(ast, Oscillation)
        # left == right (自己振動 = 反復)
        assert isinstance(ast.left, Sequence)
        assert len(ast.left.steps) == 4
        assert ast.left.steps[0].id == "sop"
        assert ast.left.steps[3].id == "dia"


# =============================================================================
# 3. 制御構文 (CPL v2.0)
# =============================================================================


class TestControlStructures:
    """CPL v2.0 制御構文の表現力。"""

    # PURPOSE: Parser
    @pytest.fixture
    def parser(self):
        return CCLParser()

    # --- 12. FOR ループ (回数) ---
    # PURPOSE: F:[×3]{/dia} — 3回判定
    def test_12_for_loop_count(self, parser):
        """F:[×3]{/dia} — 3回判定"""
        ast = parser.parse("F:[×3]{/dia}")
        assert isinstance(ast, ForLoop)
        assert ast.iterations == 3

    # --- 13. FOR ループ (リスト) ---
    # PURPOSE: F:[O,S,A]{/met} — 各シリーズで尺度
    def test_13_for_loop_list(self, parser):
        """F:[O,S,A]{/met} — 各シリーズで尺度"""
        ast = parser.parse("F:[O,S,A]{/met}")
        assert isinstance(ast, ForLoop)
        assert ast.iterations == ["O", "S", "A"]

    # --- 14. IF 条件分岐 ---
    # PURPOSE: I:[V[] > 0.5]{/noe+} E:{/noe-} — 確信度分岐
    def test_14_if_condition(self, parser):
        """I:[V[] > 0.5]{/noe+} E:{/noe-} — 確信度分岐"""
        ast = parser.parse("I:[V[] > 0.5]{/noe+} E:{/noe-}")
        assert isinstance(ast, IfCondition)
        assert ast.then_branch.id == "noe"
        assert ast.else_branch.id == "noe"

    # --- 15. WHILE ループ ---
    # PURPOSE: W:[E[] > 0.3]{/dia} — エネルギー条件
    def test_15_while_loop(self, parser):
        """W:[E[] > 0.3]{/dia} — エネルギー条件"""
        ast = parser.parse("W:[E[] > 0.3]{/dia}")
        assert isinstance(ast, WhileLoop)

    # --- 16. Lambda ---
    # PURPOSE: L:[wf]{wf+} — 任意WFを深化
    def test_16_lambda(self, parser):
        """L:[wf]{wf+} — 任意WFを深化"""
        ast = parser.parse("L:[wf]{wf+}")
        assert isinstance(ast, Lambda)
        assert ast.params == ["wf"]

    # --- 17. lim 正式形 ---
    # PURPOSE: lim[V[] < 0.3]{/noe+} — 極限収束
    def test_17_lim(self, parser):
        """lim[V[] < 0.3]{/noe+} — 極限収束"""
        ast = parser.parse("lim[V[] < 0.3]{/noe+}")
        assert isinstance(ast, ConvergenceLoop)


# =============================================================================
# 4. 高度な組み合わせ
# =============================================================================


class TestAdvancedCombinations:
    """高度な組み合わせ式。"""

    # PURPOSE: Parser
    @pytest.fixture
    def parser(self):
        return CCLParser()

    # --- 18. Colimit 展開 ---
    # PURPOSE: \noe — 余極限展開
    def test_18_colimit(self, parser):
        """\\noe — 余極限展開"""
        ast = parser.parse("\\noe")
        assert isinstance(ast, ColimitExpansion)

    # --- 19. マクロ ---
    # PURPOSE: @syn — Synedrion マクロ
    def test_19_macro(self, parser):
        """@syn — Synedrion マクロ"""
        ast = parser.parse("@syn")
        assert isinstance(ast, MacroRef)
        assert ast.name == "syn"

    # --- 20. マクロ + セレクタ ---
    # PURPOSE: @S{O,A,K} — シリーズ Peras
    def test_20_macro_selector(self, parser):
        """@S{O,A,K} — シリーズ Peras"""
        ast = parser.parse("@S{O,A,K}")
        assert isinstance(ast, MacroRef)
        assert ast.args == ["O,A,K"]


# =============================================================================
# 5. 表現力ギャップ分析
# =============================================================================


class TestExpressivenessGaps:
    """パーサーの表現力ギャップ分析。

    結論: パーサーは予想以上に柔軟。
    唯一の真ギャップは WF の {params} 構文。
    """

    # PURPOSE: Parser
    @pytest.fixture
    def parser(self):
        return CCLParser()

    # PURPOSE: |> パイプライン — パースは成功する（AST は Workflow fallback）
    def test_gap_pipeline_parses(self, parser):
        """|> パイプライン — パースは成功する（AST は Workflow fallback）"""
        ast = parser.parse("/noe+ |> /dia")
        # パーサーは |> を二項演算子として認識するが
        # _handle_binary が Workflow にフォールバック
        assert ast is not None

    # PURPOSE: || 並列 — パースは成功する（Workflow fallback）
    def test_gap_parallel_parses(self, parser):
        """|| 並列 — パースは成功する（Workflow fallback）"""
        ast = parser.parse("/noe || /dia")
        assert ast is not None

    # PURPOSE: シーケンス内に IF — パースが成功する
    def test_gap_nested_control_in_sequence(self, parser):
        """シーケンス内に IF — パースが成功する"""
        ast = parser.parse("/noe+_I:[V[] > 0.5]{/dia}")
        assert isinstance(ast, Sequence)
        # 2番目のステップが IfCondition になるか確認
        assert isinstance(ast.steps[1], IfCondition)

    # PURPOSE: GAP: /dia+{depth=3} — WF にパラメータを直接渡す
    @pytest.mark.xfail(reason="WF直後の{params}構文未対応 — 唯一の真ギャップ", strict=True)
    def test_gap_wf_params(self, parser):
        """GAP: /dia+{depth=3} — WF にパラメータを直接渡す"""
        ast = parser.parse("/dia+{depth=3}")
        assert isinstance(ast, Workflow)
        assert ast.modifiers.get("depth") == 3

    # PURPOSE: 条件付きマクロ — パースは成功する
    def test_gap_conditional_macro_parses(self, parser):
        """条件付きマクロ — パースは成功する"""
        ast = parser.parse("@syn{mode=cold}")
        assert isinstance(ast, MacroRef)
        assert "mode=cold" in ast.args
