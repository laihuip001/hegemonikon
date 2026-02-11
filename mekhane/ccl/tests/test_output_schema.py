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

# PURPOSE: Test suite validating operator type correctness
class TestOperatorType:
    """CCL 演算子タイプ Enum のテスト"""

    # PURPOSE: Verify factorial behaves correctly
    def test_factorial(self):
        """Verify factorial behavior."""
        assert OperatorType.FACTORIAL.value == "!"

    # PURPOSE: Verify oscillate behaves correctly
    def test_oscillate(self):
        """Verify oscillate behavior."""
        assert OperatorType.OSCILLATE.value == "~"

    # PURPOSE: Verify merge behaves correctly
    def test_merge(self):
        """Verify merge behavior."""
        assert OperatorType.MERGE.value == "*"

    # PURPOSE: Verify meta behaves correctly
    def test_meta(self):
        """Verify meta behavior."""
        assert OperatorType.META.value == "^"

    # PURPOSE: Verify deepen behaves correctly
    def test_deepen(self):
        """Verify deepen behavior."""
        assert OperatorType.DEEPEN.value == "+"

    # PURPOSE: Verify condense behaves correctly
    def test_condense(self):
        """Verify condense behavior."""
        assert OperatorType.CONDENSE.value == "-"

    # PURPOSE: Verify sequence behaves correctly
    def test_sequence(self):
        """Verify sequence behavior."""
        assert OperatorType.SEQUENCE.value == "_"

    # PURPOSE: Verify query behaves correctly
    def test_query(self):
        """Verify query behavior."""
        assert OperatorType.QUERY.value == "?"

    # PURPOSE: Verify invert behaves correctly
    def test_invert(self):
        """Verify invert behavior."""
        assert OperatorType.INVERT.value == "\\"

    # PURPOSE: Verify all count behaves correctly
    def test_all_count(self):
        """Verify all count behavior."""
        assert len(OperatorType) == 9


# ── OperatorVerification ─────────────────

# PURPOSE: Test suite validating operator verification correctness
class TestOperatorVerification:
    """演算子理解証明のテスト"""

    # PURPOSE: Verify valid behaves correctly
    def test_valid(self):
        """Verify valid behavior."""
        ov = OperatorVerification(
            operator="!",
            official_name="階乗",
            official_action="全派生同時実行",
            my_understanding="ワークフローの全派生を同時に実行する演算子です",
        )
        assert ov.operator == "!"

    # PURPOSE: Verify invalid operator behaves correctly
    def test_invalid_operator(self):
        """Verify invalid operator behavior."""
        with pytest.raises(ValidationError):
            OperatorVerification(
                operator="X",
                official_name="Invalid",
                official_action="Nothing",
                my_understanding="This should fail because X is not a valid op",
            )

    # PURPOSE: Verify too short understanding behaves correctly
    def test_too_short_understanding(self):
        """Verify too short understanding behavior."""
        with pytest.raises(ValidationError):
            OperatorVerification(
                operator="!",
                official_name="階乗",
                official_action="全派生",
                my_understanding="短い",  # min_length=20
            )


# ── StepOutput ───────────────────────────

# PURPOSE: Test suite validating step output correctness
class TestStepOutput:
    """CCL ステップ出力のテスト"""

    # PURPOSE: Verify valid behaves correctly
    def test_valid(self):
        """Verify valid behavior."""
        so = StepOutput(
            step_name="O1 Noēsis",
            reasoning="これは十分に長い推論過程です。" * 10,
            verification="検証内容をここに詳しく記載します。" * 5,
            result="結果",
        )
        assert so.step_name == "O1 Noēsis"

    # PURPOSE: Verify reasoning too short behaves correctly
    def test_reasoning_too_short(self):
        """Verify reasoning too short behavior."""
        with pytest.raises(ValidationError):
            StepOutput(
                step_name="test",
                reasoning="短い",  # min_length=100
                verification="検証内容をここに詳しく記載します。" * 5,
                result="結果",
            )

    # PURPOSE: Verify verification too short behaves correctly
    def test_verification_too_short(self):
        """Verify verification too short behavior."""
        with pytest.raises(ValidationError):
            StepOutput(
                step_name="test",
                reasoning="推論" * 50,
                verification="短い",  # min_length=50
                result="結果",
            )


# ── OscillationOutput ────────────────────

# PURPOSE: Test suite validating oscillation output correctness
class TestOscillationOutput:
    """振動演算子出力のテスト"""

    # PURPOSE: Verify valid behaves correctly
    def test_valid(self):
        """Verify valid behavior."""
        oo = OscillationOutput(
            direction_a="A方向の分析内容 " * 20,
            direction_b="B方向の分析内容 " * 20,
            synthesis="統合結果",
        )
        assert "A方向" in oo.direction_a

    # PURPOSE: Verify direction too short behaves correctly
    def test_direction_too_short(self):
        """Verify direction too short behavior."""
        with pytest.raises(ValidationError):
            OscillationOutput(
                direction_a="短い",  # min_length=100
                direction_b="B" * 100,
                synthesis="統合",
            )


# ── MergeOutput ──────────────────────────

# PURPOSE: Test suite validating merge output correctness
class TestMergeOutput:
    """融合演算子出力のテスト"""

    # PURPOSE: Verify valid behaves correctly
    def test_valid(self):
        """Verify valid behavior."""
        mo = MergeOutput(
            elements=["要素A", "要素B"],
            merge_process="融合過程の説明 " * 20,
            merged_result="融合結果",
        )
        assert len(mo.elements) == 2

    # PURPOSE: Verify too few elements behaves correctly
    def test_too_few_elements(self):
        """Verify too few elements behavior."""
        with pytest.raises(ValidationError):
            MergeOutput(
                elements=["only_one"],  # min_items=2
                merge_process="プロセス " * 20,
                merged_result="結果",
            )


# ── MetaOutput ───────────────────────────

# PURPOSE: Test suite validating meta output correctness
class TestMetaOutput:
    """メタ演算子出力のテスト"""

    # PURPOSE: Verify valid behaves correctly
    def test_valid(self):
        """Verify valid behavior."""
        mo = MetaOutput(
            target="分析対象",
            meta_perspective="メタ視点からの詳細な分析 " * 20,
            insights=["洞察1"],
        )
        assert mo.target == "分析対象"

    # PURPOSE: Verify empty insights behaves correctly
    def test_empty_insights(self):
        """Verify empty insights behavior."""
        with pytest.raises(ValidationError):
            MetaOutput(
                target="対象",
                meta_perspective="メタ " * 50,
                insights=[],  # min_items=1
            )


# ── SelfAudit ────────────────────────────

# PURPOSE: Test suite validating self audit correctness
class TestSelfAudit:
    """自己監査のテスト"""

    # PURPOSE: Verify valid behaves correctly
    def test_valid(self):
        """Verify valid behavior."""
        sa = SelfAudit(
            completeness_check="全ステップ完了",
            operator_compliance="全演算子の要件を満たした",
        )
        assert sa.potential_issues == []

    # PURPOSE: Verify with issues behaves correctly
    def test_with_issues(self):
        """Verify with issues behavior."""
        sa = SelfAudit(
            completeness_check="完了",
            operator_compliance="準拠",
            potential_issues=["問題1", "問題2"],
        )
        assert len(sa.potential_issues) == 2


# ── CCLExecutionOutput ───────────────────

# PURPOSE: Test suite validating c c l execution output correctness
class TestCCLExecutionOutput:
    """CCL 完全実行出力のテスト"""

    # PURPOSE: Verify valid output behaves correctly
    @pytest.fixture
    def valid_output(self):
        """Verify valid output behavior."""
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

    # PURPOSE: Verify valid behaves correctly
    def test_valid(self, valid_output):
        """Verify valid behavior."""
        assert valid_output.ccl_expression == "/noe!"

    # PURPOSE: Verify has schema extra behaves correctly
    def test_has_schema_extra(self):
        """Verify has schema extra behavior."""
        assert hasattr(CCLExecutionOutput, "Config")
        assert hasattr(CCLExecutionOutput.Config, "schema_extra")

    # PURPOSE: Verify optional fields none behaves correctly
    def test_optional_fields_none(self, valid_output):
        """Verify optional fields none behavior."""
        assert valid_output.oscillations is None
        assert valid_output.merges is None
        assert valid_output.metas is None
        assert valid_output.factorials is None

    # PURPOSE: Verify no operator verifications behaves correctly
    def test_no_operator_verifications(self):
        """Verify no operator verifications behavior."""
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
