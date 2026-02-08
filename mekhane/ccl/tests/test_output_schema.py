#!/usr/bin/env python3
# PROOF: [L2/テスト] <- mekhane/ccl/tests/
# PURPOSE: CCL Output Schema (Pydantic) の包括テスト
"""CCL Output Schema Tests"""

import pytest
from pydantic import ValidationError

from mekhane.ccl.output_schema import (
    OperatorType,
    OperatorVerification,
    StepOutput,
    OscillationOutput,
    MergeOutput,
    MetaOutput,
    FactorialOutput,
    SelfAudit,
    CCLExecutionOutput,
)


# ── OperatorType ─────────────────────────

class TestOperatorType:
    """CCL 演算子タイプ Enum のテスト"""

    def test_factorial(self):
        assert OperatorType.FACTORIAL.value == "!"

    def test_oscillate(self):
        assert OperatorType.OSCILLATE.value == "~"

    def test_merge(self):
        assert OperatorType.MERGE.value == "*"

    def test_meta(self):
        assert OperatorType.META.value == "^"

    def test_deepen(self):
        assert OperatorType.DEEPEN.value == "+"

    def test_condense(self):
        assert OperatorType.CONDENSE.value == "-"

    def test_sequence(self):
        assert OperatorType.SEQUENCE.value == "_"

    def test_query(self):
        assert OperatorType.QUERY.value == "?"

    def test_invert(self):
        assert OperatorType.INVERT.value == "\\"

    def test_all_count(self):
        assert len(OperatorType) == 9


# ── OperatorVerification ─────────────────

class TestOperatorVerification:
    """演算子理解証明のテスト"""

    def test_valid(self):
        ov = OperatorVerification(
            operator="!",
            official_name="階乗",
            official_action="全派生同時実行",
            my_understanding="ワークフローの全派生を同時に実行する演算子です",
        )
        assert ov.operator == "!"

    def test_invalid_operator(self):
        with pytest.raises(ValidationError):
            OperatorVerification(
                operator="X",
                official_name="Invalid",
                official_action="Nothing",
                my_understanding="This should fail because X is not a valid op",
            )

    def test_too_short_understanding(self):
        with pytest.raises(ValidationError):
            OperatorVerification(
                operator="!",
                official_name="階乗",
                official_action="全派生",
                my_understanding="短い",  # min_length=20
            )


# ── StepOutput ───────────────────────────

class TestStepOutput:
    """CCL ステップ出力のテスト"""

    def test_valid(self):
        so = StepOutput(
            step_name="O1 Noēsis",
            reasoning="これは十分に長い推論過程です。" * 10,
            verification="検証内容をここに詳しく記載します。" * 5,
            result="結果",
        )
        assert so.step_name == "O1 Noēsis"

    def test_reasoning_too_short(self):
        with pytest.raises(ValidationError):
            StepOutput(
                step_name="test",
                reasoning="短い",  # min_length=100
                verification="検証内容をここに詳しく記載します。" * 5,
                result="結果",
            )

    def test_verification_too_short(self):
        with pytest.raises(ValidationError):
            StepOutput(
                step_name="test",
                reasoning="推論" * 50,
                verification="短い",  # min_length=50
                result="結果",
            )


# ── OscillationOutput ────────────────────

class TestOscillationOutput:
    """振動演算子出力のテスト"""

    def test_valid(self):
        oo = OscillationOutput(
            direction_a="A方向の分析内容 " * 20,
            direction_b="B方向の分析内容 " * 20,
            synthesis="統合結果",
        )
        assert "A方向" in oo.direction_a

    def test_direction_too_short(self):
        with pytest.raises(ValidationError):
            OscillationOutput(
                direction_a="短い",  # min_length=100
                direction_b="B" * 100,
                synthesis="統合",
            )


# ── MergeOutput ──────────────────────────

class TestMergeOutput:
    """融合演算子出力のテスト"""

    def test_valid(self):
        mo = MergeOutput(
            elements=["要素A", "要素B"],
            merge_process="融合過程の説明 " * 20,
            merged_result="融合結果",
        )
        assert len(mo.elements) == 2

    def test_too_few_elements(self):
        with pytest.raises(ValidationError):
            MergeOutput(
                elements=["only_one"],  # min_items=2
                merge_process="プロセス " * 20,
                merged_result="結果",
            )


# ── MetaOutput ───────────────────────────

class TestMetaOutput:
    """メタ演算子出力のテスト"""

    def test_valid(self):
        mo = MetaOutput(
            target="分析対象",
            meta_perspective="メタ視点からの詳細な分析 " * 20,
            insights=["洞察1"],
        )
        assert mo.target == "分析対象"

    def test_empty_insights(self):
        with pytest.raises(ValidationError):
            MetaOutput(
                target="対象",
                meta_perspective="メタ " * 50,
                insights=[],  # min_items=1
            )


# ── SelfAudit ────────────────────────────

class TestSelfAudit:
    """自己監査のテスト"""

    def test_valid(self):
        sa = SelfAudit(
            completeness_check="全ステップ完了",
            operator_compliance="全演算子の要件を満たした",
        )
        assert sa.potential_issues == []

    def test_with_issues(self):
        sa = SelfAudit(
            completeness_check="完了",
            operator_compliance="準拠",
            potential_issues=["問題1", "問題2"],
        )
        assert len(sa.potential_issues) == 2


# ── CCLExecutionOutput ───────────────────

class TestCCLExecutionOutput:
    """CCL 完全実行出力のテスト"""

    @pytest.fixture
    def valid_output(self):
        return CCLExecutionOutput(
            ccl_expression="/noe!",
            operator_verifications=[
                OperatorVerification(
                    operator="!",
                    official_name="階乗",
                    official_action="全派生同時実行",
                    my_understanding="ワークフローの全派生を同時に実行する演算子",
                )
            ],
            steps=[
                StepOutput(
                    step_name="O1 Noēsis",
                    reasoning="推論過程 " * 30,
                    verification="検証内容 " * 15,
                    result="結果",
                )
            ],
            final_result="最終結果 " * 30,
            self_audit=SelfAudit(
                completeness_check="完了",
                operator_compliance="準拠",
            ),
        )

    def test_valid(self, valid_output):
        assert valid_output.ccl_expression == "/noe!"

    def test_has_schema_extra(self):
        assert hasattr(CCLExecutionOutput, "Config")
        assert hasattr(CCLExecutionOutput.Config, "schema_extra")

    def test_optional_fields_none(self, valid_output):
        assert valid_output.oscillations is None
        assert valid_output.merges is None
        assert valid_output.metas is None
        assert valid_output.factorials is None

    def test_no_operator_verifications(self):
        with pytest.raises(ValidationError):
            CCLExecutionOutput(
                ccl_expression="/noe",
                operator_verifications=[],  # min_items=1
                steps=[
                    StepOutput(
                        step_name="test",
                        reasoning="推論 " * 30,
                        verification="検証 " * 15,
                        result="結果",
                    )
                ],
                final_result="最終結果 " * 30,
                self_audit=SelfAudit(
                    completeness_check="完了",
                    operator_compliance="準拠",
                ),
            )
