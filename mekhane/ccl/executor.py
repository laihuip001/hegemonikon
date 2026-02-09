# PROOF: [L2/インフラ] <- mekhane/ccl/
# CCL Zero-Trust Executor - 統合エントリポイント

"""
Zero-Trust CCL Executor

5段階の強制機構を統合:
- Phase 0: 仕様強制注入
- Phase 1: 出力構造強制 (Pydantic)
- Phase 2: 出力検証
- Phase 3: 論理監査 (Multi-Agent) - 将来実装
- Phase 4: 失敗パターン学習
"""

from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path

from .spec_injector import SpecInjector, OPERATOR_DEFINITIONS
from .guardrails.validators import CCLOutputValidator, ValidationResult
from .learning.failure_db import get_failure_db, FailureDB


# PURPOSE: CCL 実行コンテキスト
@dataclass
class ExecutionContext:
    """CCL 実行コンテキスト"""

    ccl_expr: str
    injected_prompt: str
    warnings: List[str]


# PURPOSE: CCL 実行結果
@dataclass
class ExecutionResult:
    """CCL 実行結果"""

    success: bool
    output: str
    validation: ValidationResult
    context: ExecutionContext


# PURPOSE: Zero-Trust CCL 実行エンジン
class ZeroTrustCCLExecutor:
    """Zero-Trust CCL 実行エンジン

    LLM を信用せず、構造的に正しい実行を強制する。
    """

    # PURPOSE: ZeroTrustCCLExecutor の初期化
    def __init__(self):
        self.injector = SpecInjector()
        self.validator = CCLOutputValidator()
        self.failure_db = get_failure_db()

    # PURPOSE: Phase 0: 実行準備
    def prepare(self, ccl_expr: str) -> ExecutionContext:
        """
        Phase 0: 実行準備

        1. 演算子仕様を注入
        2. 過去の失敗から警告を生成
        """
        # 仕様注入
        injected_prompt = self.injector.inject(ccl_expr)

        # 警告を取得
        warnings_records = self.failure_db.get_warnings(ccl_expr)
        warnings_text = self.failure_db.format_warnings(warnings_records)

        # 警告をプロンプトに追加
        if warnings_text:
            injected_prompt = warnings_text + "\n" + injected_prompt

        return ExecutionContext(
            ccl_expr=ccl_expr,
            injected_prompt=injected_prompt,
            warnings=[w.message for w in warnings_records],
        )

    # PURPOSE: Phase 2: 出力検証
    def validate(self, output: str, context: ExecutionContext) -> ValidationResult:
        """
        Phase 2: 出力検証
        """
        return self.validator.validate(output, context.ccl_expr)

    # PURPOSE: Phase 4: 結果を記録
    def record_result(
        self, context: ExecutionContext, validation: ValidationResult, output: str
    ) -> None:
        """
        Phase 4: 結果を記録
        """
        if validation.valid:
            self.failure_db.record_success(
                ccl_expr=context.ccl_expr, output_summary=output[:200]
            )
        else:
            for error in validation.errors:
                self.failure_db.record_failure(
                    ccl_expr=context.ccl_expr,
                    operator=error.operator,
                    failure_type=error.error_type,
                    cause=error.message,
                )

    # PURPOSE: CCL 実行フロー全体
    def execute(
        self, ccl_expr: str, output: str, record: bool = True
    ) -> ExecutionResult:
        """
        CCL 実行フロー全体

        Args:
            ccl_expr: CCL 式
            output: LLM が生成した出力
            record: 結果を記録するか

        Returns:
            ExecutionResult
        """
        # Phase 0: 準備
        context = self.prepare(ccl_expr)

        # Phase 2: 検証
        validation = self.validate(output, context)

        # Phase 4: 記録
        if record:
            self.record_result(context, validation, output)

        return ExecutionResult(
            success=validation.valid,
            output=output,
            validation=validation,
            context=context,
        )

    # PURPOSE: 再生成用のプロンプトを取得
    def get_regeneration_prompt(self, result: ExecutionResult) -> str:
        """再生成用のプロンプトを取得"""
        if result.success:
            return ""

        return f"""
{result.validation.regeneration_instruction}

---

## 元の CCL 式

`{result.context.ccl_expr}`

---

## 再生成してください

上記の問題を修正した出力を生成してください。
"""


# 便利関数
# PURPOSE: CCL 式から LLM に渡すプロンプトを生成
def create_ccl_prompt(ccl_expr: str) -> str:
    """CCL 式から LLM に渡すプロンプトを生成"""
    executor = ZeroTrustCCLExecutor()
    context = executor.prepare(ccl_expr)
    return context.injected_prompt


# PURPOSE: CCL 出力を検証
def validate_ccl_output(ccl_expr: str, output: str) -> ValidationResult:
    """CCL 出力を検証"""
    executor = ZeroTrustCCLExecutor()
    context = executor.prepare(ccl_expr)
    return executor.validate(output, context)


# テスト用
if __name__ == "__main__":
    executor = ZeroTrustCCLExecutor()

    # プロンプト生成テスト
    print("=" * 60)
    print("Phase 0: プロンプト生成")
    print("=" * 60)
    context = executor.prepare("/noe!~/u+")
    print(context.injected_prompt)

    # 検証テスト
    print("\n" + "=" * 60)
    print("Phase 2: 出力検証 (不完全な出力)")
    print("=" * 60)
    bad_output = "分析結果です。終わり。"
    result = executor.execute("/noe!~/u+", bad_output, record=False)
    print(f"Success: {result.success}")
    print(f"Errors: {len(result.validation.errors)}")
    print(result.validation.regeneration_instruction)
