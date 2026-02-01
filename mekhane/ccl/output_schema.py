# PROOF: [L2/インフラ]
# Phase 1: CCL 出力スキーマ定義

"""
CCL Output Schema - Pydantic モデルによる出力構造強制

目的:
- 出力構造を型安全に制約
- 必須セクションの存在を保証
- 省略を防止 (min_length)
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum


class OperatorType(str, Enum):
    """CCL 演算子タイプ"""

    FACTORIAL = "!"  # 全派生同時実行
    OSCILLATE = "~"  # 振動
    MERGE = "*"  # 融合
    META = "^"  # メタ分析
    DEEPEN = "+"  # 深化
    CONDENSE = "-"  # 縮約
    SEQUENCE = "_"  # シーケンス
    QUERY = "?"  # 照会
    INVERT = "\\"  # 反転


class OperatorVerification(BaseModel):
    """演算子理解の証明"""

    operator: str = Field(..., description="使用する演算子")
    official_name: str = Field(..., description="演算子の正式名称")
    official_action: str = Field(..., description="演算子の正式な作用")
    my_understanding: str = Field(
        ..., min_length=20, description="自分の言葉での説明（省略禁止）"
    )

    @validator("operator")
    def validate_operator(cls, v):
        valid_ops = set("!~*^+-_?\\")
        if v not in valid_ops:
            raise ValueError(f"無効な演算子: {v}")
        return v


class StepOutput(BaseModel):
    """CCL ステップの出力"""

    step_name: str = Field(..., description="ステップ名")
    reasoning: str = Field(..., min_length=100, description="推論過程（省略禁止）")
    verification: str = Field(..., min_length=50, description="検証内容")
    result: str = Field(..., description="結果")


class OscillationOutput(BaseModel):
    """振動演算子 (~) の出力"""

    direction_a: str = Field(..., min_length=100, description="A → B 方向の分析")
    direction_b: str = Field(..., min_length=100, description="B → A 方向の分析")
    synthesis: str = Field(..., description="振動の統合結果")


class MergeOutput(BaseModel):
    """融合演算子 (*) の出力"""

    elements: List[str] = Field(..., min_items=2, description="融合する要素リスト")
    merge_process: str = Field(..., min_length=100, description="融合過程の説明")
    merged_result: str = Field(..., description="融合結果")


class MetaOutput(BaseModel):
    """メタ演算子 (^) の出力"""

    target: str = Field(..., description="メタ分析対象")
    meta_perspective: str = Field(..., min_length=100, description="メタ視点からの分析")
    insights: List[str] = Field(
        ..., min_items=1, description="メタ分析から得られた洞察"
    )


class FactorialOutput(BaseModel):
    """階乗演算子 (!) の出力"""

    base_workflow: str = Field(..., description="基底ワークフロー")
    all_derivatives: List[str] = Field(..., min_items=1, description="全派生リスト")
    simultaneous_execution: List[StepOutput] = Field(
        ..., min_items=1, description="同時実行結果"
    )


class SelfAudit(BaseModel):
    """自己監査"""

    completeness_check: str = Field(..., description="全ステップ完了の確認")
    operator_compliance: str = Field(..., description="演算子要件への準拠確認")
    potential_issues: List[str] = Field(
        default_factory=list, description="潜在的問題点"
    )


class CCLExecutionOutput(BaseModel):
    """CCL 完全実行出力"""

    ccl_expression: str = Field(..., description="実行した CCL 式")

    operator_verifications: List[OperatorVerification] = Field(
        ..., min_items=1, description="使用した演算子の理解証明"
    )

    steps: List[StepOutput] = Field(..., min_items=1, description="実行ステップ")

    oscillations: Optional[List[OscillationOutput]] = Field(
        None, description="振動演算子の出力（使用時のみ）"
    )

    merges: Optional[List[MergeOutput]] = Field(
        None, description="融合演算子の出力（使用時のみ）"
    )

    metas: Optional[List[MetaOutput]] = Field(
        None, description="メタ演算子の出力（使用時のみ）"
    )

    factorials: Optional[List[FactorialOutput]] = Field(
        None, description="階乗演算子の出力（使用時のみ）"
    )

    final_result: str = Field(..., min_length=100, description="最終結果")

    self_audit: SelfAudit = Field(..., description="自己監査")

    class Config:
        schema_extra = {
            "example": {
                "ccl_expression": "/noe!~/u+",
                "operator_verifications": [
                    {
                        "operator": "!",
                        "official_name": "階乗",
                        "official_action": "全派生同時実行",
                        "my_understanding": "ワークフローの全派生を同時に実行する",
                    }
                ],
                "steps": [
                    {
                        "step_name": "O1 Noēsis 全派生",
                        "reasoning": "...",
                        "verification": "...",
                        "result": "...",
                    }
                ],
                "final_result": "...",
                "self_audit": {
                    "completeness_check": "全ステップ完了",
                    "operator_compliance": "全演算子の要件を満たした",
                    "potential_issues": [],
                },
            }
        }


# テスト用
if __name__ == "__main__":
    # バリデーションテスト
    try:
        output = CCLExecutionOutput(
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
                    reasoning="これは100文字以上の推論過程です。" * 5,
                    verification="検証内容をここに記載します。" * 3,
                    result="結果",
                )
            ],
            final_result="最終結果をここに記載します。" * 5,
            self_audit=SelfAudit(
                completeness_check="完了",
                operator_compliance="準拠",
                potential_issues=[],
            ),
        )
        print("✅ バリデーション成功")
        print(output.json(indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ バリデーション失敗: {e}")
