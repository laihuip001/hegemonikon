# PROOF: [L1/定理] <- mekhane/fep/
"""
PROOF: [L1/定理] このファイルは存在しなければならない

A0 → 認知には行為 (Energeia) がある
   → O4 で行動選択と実行を制御
   → energeia_executor が担う

Q.E.D.

---

O4 Energeia Executor — 行為実行エンジン

Hegemonikón O-series (Ousia) 定理: O4 Energeia
FEP層での行動選択と実行制御を担当。

Architecture:
- O4 Energeia = FEP の sample_action() に対応
- K3 Telos を参照して目的整合を確認
- P4 Tekhnē を参照して技法を選択

References:
- /ene ワークフロー (6段階実行フレームワーク)
- FEP: 行動選択 = 期待自由エネルギー最小化
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
from datetime import datetime

from .telos_checker import check_alignment, TelосResult, AlignmentStatus
from .tekhne_registry import (
    TekhnēRegistry,
    Technique,
    get_registry,
    search_techniques,
    ActionCategory,
)


# PURPOSE: 実行フェーズ (6段階)
class ExecutionPhase(Enum):
    """実行フェーズ (6段階)"""

    INIT = "init"  # PHASE 0: 入口確認
    EXECUTE = "execute"  # PHASE 1: 実行
    VERIFY = "verify"  # PHASE 2: 検証
    DEVIATION = "deviation"  # PHASE 3: 偏差検知
    CONFIRM = "confirm"  # PHASE 4: 完了確認
    ROLLBACK = "rollback"  # PHASE 5: 安全弁


# PURPOSE: 実行状態
class ExecutionStatus(Enum):
    """実行状態"""

    PENDING = "pending"  # 未開始
    RUNNING = "running"  # 実行中
    PAUSED = "paused"  # 一時停止
    COMPLETED = "completed"  # 完了
    FAILED = "failed"  # 失敗
    ABORTED = "aborted"  # 中断


# PURPOSE: の統一的インターフェースを実現する
@dataclass
# PURPOSE: 実行コンテキスト
class ExecutionContext:
    """実行コンテキスト

    O4 Energeia の実行状態を保持。
    """

    goal: str  # 目的
    plan: str  # 計画
    technique: Optional[Technique]  # 選択された技法
    phase: ExecutionPhase  # 現在フェーズ
    status: ExecutionStatus  # 実行状態
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    telos_result: Optional[TelосResult] = None  # K3 Telos 評価結果
    artifacts: List[str] = field(default_factory=list)  # 生成物
    errors: List[str] = field(default_factory=list)  # エラー
    checkpoints: Dict[str, Any] = field(default_factory=dict)  # 各フェーズの結果

    # PURPOSE: 実行結果をJSON永続化可能な形式に変換
    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "plan": self.plan,
            "technique": self.technique.id if self.technique else None,
            "phase": self.phase.value,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "artifacts": self.artifacts,
            "errors": self.errors,
        }


# PURPOSE: 実行結果
@dataclass
class ExecutionResult:
    """実行結果

    Attributes:
        success: 成功したか
        context: 実行コンテキスト
        output: 出力データ
        commit_message: 提案されるコミットメッセージ
    """

    success: bool
    context: ExecutionContext
    output: Optional[Any] = None
    commit_message: Optional[str] = None

# PURPOSE: O4 Energeia 実行エンジン

class EnergеiaExecutor:
    """O4 Energeia 実行エンジン

    6段階の実行フローを管理し、K3 Telos と P4 Tekhnē を統合。
    """

    # PURPOSE: Args:
    def __init__(
        self,
        registry: Optional[TekhnēRegistry] = None,
        max_retries: int = 3,
    ):
        """
        Args:
            registry: 技法レジストリ (None でデフォルト使用)
            max_retries: 最大リトライ回数
        """
        self._registry = registry or get_registry()
        self._max_retries = max_retries
        self._current_context: Optional[ExecutionContext] = None

    # PURPOSE: energeia_executor の current context 処理を実行する
    @property
    # PURPOSE: 現在の実行コンテキスト
    def current_context(self) -> Optional[ExecutionContext]:
        """現在の実行コンテキスト"""
        return self._current_context

    # PURPOSE: PHASE 0: 入口確認 + 実行コンテキスト作成
    def initiate(
        self,
        goal: str,
        plan: str,
        technique_id: Optional[str] = None,
    ) -> ExecutionContext:
        """PHASE 0: 入口確認 + 実行コンテキスト作成

        K3 Telos で目的整合を確認し、P4 Tekhnē で技法を選択。

        Args:
            goal: 目的
            plan: 計画
            technique_id: 指定された技法ID (None で自動選択)

        Returns:
            ExecutionContext

        Raises:
            ValueError: 目的整合が取れない場合
        """
        # Step 1: K3 Telos による目的整合確認
        telos_result = check_alignment(goal=goal, action=plan)

        if telos_result.status == AlignmentStatus.INVERTED:
            raise ValueError(
                f"目的と計画が逆転しています: {telos_result.rationale}\n"
                f"提案: {', '.join(telos_result.suggestions)}"
            )

        # Step 2: P4 Tekhnē による技法選択
        if technique_id:
            technique = self._registry.get(technique_id)
        else:
            # キーワードベースで自動選択
            candidates = search_techniques(goal[:50])
            if candidates:
                # 最初のマッチを選択 (将来的には S2 Mekhanē が選択)
                technique = candidates[0]
            else:
                technique = None

        # Step 3: コンテキスト作成
        context = ExecutionContext(
            goal=goal,
            plan=plan,
            technique=technique,
            phase=ExecutionPhase.INIT,
            status=ExecutionStatus.PENDING,
            telos_result=telos_result,
        )

        context.checkpoints["phase_0"] = {
            "telos": {
                "status": telos_result.status.value,
                "score": telos_result.alignment_score,
            },
            "technique": technique.id if technique else None,
        }

        self._current_context = context
        return context

    # PURPOSE: PHASE 1: 実行
    def execute(
        self,
        context: ExecutionContext,
        action_fn: Callable[[], Any],
    ) -> ExecutionContext:
        """PHASE 1: 実行

        Args:
            context: 実行コンテキスト
            action_fn: 実行する関数

        Returns:
            更新されたコンテキスト
        """
        context.phase = ExecutionPhase.EXECUTE
        context.status = ExecutionStatus.RUNNING
        context.started_at = datetime.now()

        try:
            output = action_fn()
            context.checkpoints["phase_1"] = {
                "success": True,
                "output_type": type(output).__name__,
            }
            # 技法使用を記録
            if context.technique:
                self._registry.record_usage(context.technique.id, True)
            return context
        except Exception as e:
            context.errors.append(str(e))
            context.checkpoints["phase_1"] = {
                "success": False,
                "error": str(e),
            }
            if context.technique:
                self._registry.record_usage(context.technique.id, False)
            raise

    # PURPOSE: PHASE 2: 検証
    def verify(
        self,
        context: ExecutionContext,
        verify_fns: List[Callable[[], bool]],
    ) -> ExecutionContext:
        """PHASE 2: 検証

        Args:
            context: 実行コンテキスト
            verify_fns: 検証関数のリスト

        Returns:
            更新されたコンテキスト
        """
        context.phase = ExecutionPhase.VERIFY

        results = []
        all_passed = True

        for i, fn in enumerate(verify_fns):
            try:
                passed = fn()
                results.append({"gate": i, "passed": passed})
                if not passed:
                    all_passed = False
            except Exception as e:
                results.append({"gate": i, "passed": False, "error": str(e)})
                all_passed = False

        context.checkpoints["phase_2"] = {
            "all_passed": all_passed,
            "results": results,
        }

        return context

    # PURPOSE: PHASE 3: 偏差検知
    def check_deviation(
        self,
        context: ExecutionContext,
        expected_artifacts: Optional[List[str]] = None,
    ) -> ExecutionContext:
        """PHASE 3: 偏差検知

        Args:
            context: 実行コンテキスト
            expected_artifacts: 期待される成果物

        Returns:
            更新されたコンテキスト
        """
        context.phase = ExecutionPhase.DEVIATION

        deviations = []

        # 成果物チェック
        if expected_artifacts:
            missing = set(expected_artifacts) - set(context.artifacts)
            if missing:
                deviations.append(f"不足成果物: {missing}")
            extra = set(context.artifacts) - set(expected_artifacts)
            if extra:
                deviations.append(f"追加成果物: {extra}")

        # 目的整合再確認
        if (
            context.telos_result
            and context.telos_result.status == AlignmentStatus.DRIFTING
        ):
            deviations.append(f"ドリフト検出: {context.telos_result.drift_indicators}")

        context.checkpoints["phase_3"] = {
            "deviations": deviations,
            "has_deviation": len(deviations) > 0,
        }

        return context

    # PURPOSE: PHASE 4: 完了確認
    def confirm(
        self,
        context: ExecutionContext,
        commit_prefix: str = "feat",
    ) -> ExecutionResult:
        """PHASE 4: 完了確認

        Args:
            context: 実行コンテキスト
            commit_prefix: コミットプレフィックス

        Returns:
            ExecutionResult
        """
        context.phase = ExecutionPhase.CONFIRM
        context.status = ExecutionStatus.COMPLETED
        context.completed_at = datetime.now()

        # コミットメッセージ生成
        scope = context.technique.id if context.technique else "core"
        commit_message = f"{commit_prefix}({scope}): {context.goal[:50]}"

        context.checkpoints["phase_4"] = {
            "commit_message": commit_message,
            "duration_seconds": (
                (context.completed_at - context.started_at).total_seconds()
                if context.started_at
                else None
            ),
        }

        return ExecutionResult(
            success=True,
            context=context,
            commit_message=commit_message,
        )

    # PURPOSE: PHASE 5: 安全弁 (中断)
    def abort(
        self,
        context: ExecutionContext,
        reason: str,
    ) -> ExecutionResult:
        """PHASE 5: 安全弁 (中断)

        Args:
            context: 実行コンテキスト
            reason: 中断理由

        Returns:
            ExecutionResult
        """
        context.phase = ExecutionPhase.ROLLBACK
        context.status = ExecutionStatus.ABORTED
        context.completed_at = datetime.now()
        context.errors.append(f"Aborted: {reason}")

        context.checkpoints["phase_5"] = {
            "abort_reason": reason,
            "rollback_needed": True,
        }

        return ExecutionResult(
            success=False,
            context=context,
        )

    # PURPOSE: 全6フェーズを一括実行
    def full_cycle(
        self,
        goal: str,
        plan: str,
        action_fn: Callable[[], Any],
        verify_fns: Optional[List[Callable[[], bool]]] = None,
        expected_artifacts: Optional[List[str]] = None,
        technique_id: Optional[str] = None,
    ) -> ExecutionResult:
        """全6フェーズを一括実行

        Args:
            goal: 目的
            plan: 計画
            action_fn: 実行関数
            verify_fns: 検証関数リスト (省略可)
            expected_artifacts: 期待成果物 (省略可)
            technique_id: 技法ID (省略可)

        Returns:
            ExecutionResult
        """
        try:
            # PHASE 0: 入口確認
            context = self.initiate(goal, plan, technique_id)

            # PHASE 1: 実行
            context = self.execute(context, action_fn)

            # PHASE 2: 検証
            if verify_fns:
                context = self.verify(context, verify_fns)
                if not context.checkpoints.get("phase_2", {}).get("all_passed"):
                    return ExecutionResult(
                        success=False,
                        context=context,
                    )

            # PHASE 3: 偏差検知
            context = self.check_deviation(context, expected_artifacts)

            # PHASE 4: 完了確認
            return self.confirm(context)

        except ValueError as e:
            # 目的整合エラー
# PURPOSE: 実行結果をMarkdown形式でフォーマット
            if self._current_context:
                return self.abort(self._current_context, str(e))
            raise
        except Exception as e:
            # その他のエラー
            if self._current_context:
                return self.abort(self._current_context, str(e))
            raise


# PURPOSE: 実行結果をMarkdown形式でフォーマット
def format_execution_markdown(result: ExecutionResult) -> str:
    """実行結果をMarkdown形式でフォーマット"""
    ctx = result.context
    status_emoji = "✅" if result.success else "❌"

    lines = [
        "═══════════════════════════════════════════════════════════",
        "[Hegemonikón] O4 Energeia: 行為完了",
        "═══════════════════════════════════════════════════════════",
        "",
        f"📋 目的: {ctx.goal}",
        "",
    ]

    # PHASE 0
    p0 = ctx.checkpoints.get("phase_0", {})
    lines.extend(
        [
            "━━━ PHASE 0: 入口確認 ━━━",
            f"  K3 Telos: {p0.get('telos', {}).get('status', 'N/A')} ({p0.get('telos', {}).get('score', 0):.0%})",
            f"  P4 Tekhnē: {p0.get('technique', 'auto')}",
            "",
        ]
    )

    # PHASE 1
    p1 = ctx.checkpoints.get("phase_1", {})
    lines.extend(
        [
            "━━━ PHASE 1: 実行 ━━━",
            f"  結果: {'✅ 成功' if p1.get('success') else '❌ 失敗'}",
            "",
        ]
    )

    # PHASE 2
    p2 = ctx.checkpoints.get("phase_2", {})
    if p2:
        lines.extend(
            [
                "━━━ PHASE 2: 検証 ━━━",
                f"  全ゲート: {'✅ Pass' if p2.get('all_passed') else '❌ Fail'}",
                "",
            ]
        )

    # PHASE 3
    p3 = ctx.checkpoints.get("phase_3", {})
    if p3:
        lines.extend(
            [
                "━━━ PHASE 3: 偏差検知 ━━━",
                f"  偏差: {'なし' if not p3.get('has_deviation') else ', '.join(p3.get('deviations', []))}",
                "",
            ]
        )

    # PHASE 4
    p4 = ctx.checkpoints.get("phase_4", {})
    if p4:
        lines.extend(
            [
                "━━━ PHASE 4: 完了確認 ━━━",
                f"  コミット: {p4.get('commit_message', 'N/A')}",
                "",
            ]
        )

    lines.extend(
        [
            "═══════════════════════════════════════════════════════════",
# PURPOSE: FEP観察空間へのエンコード
            f"📌 状態: {status_emoji} {ctx.status.value.upper()}",
            f"📝 提案: {result.commit_message or 'N/A'}",
            "═══════════════════════════════════════════════════════════",
        ]
    )

    return "\n".join(lines)


# FEP Integration
# PURPOSE: FEP観察空間へのエンコード
def encode_execution_observation(result: ExecutionResult) -> dict:
    """FEP観察空間へのエンコード

    ExecutionResult を FEP agent の観察形式に変換。

    Returns:
        dict with context_clarity, urgency, confidence
    """
    ctx = result.context

    # 成功/失敗を context_clarity にマップ
    context_clarity = 0.9 if result.success else 0.3

    # エラー数を urgency にマップ
    urgency = min(1.0, len(ctx.errors) * 0.3)

    # Telos 整合度を confidence にマップ
    if ctx.telos_result:
        confidence = ctx.telos_result.alignment_score
    else:
        confidence = 0.5

    return {
        "context_clarity": context_clarity,
        "urgency": urgency,
        "confidence": confidence,
    }
