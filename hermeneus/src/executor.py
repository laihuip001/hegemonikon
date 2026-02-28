# PROOF: [L2/インフラ] <- hermeneus/src/ Workflow Executor
"""
Hermēneus Executor — ワークフロー実行エンジン

CCL ワークフローを完全なパイプラインで実行:
compile → execute → verify → audit

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager


# =============================================================================
# Types
# =============================================================================

# PURPOSE: [L2-auto] 実行フェーズ
class ExecutionPhase(Enum):
    """実行フェーズ"""
    INIT = "init"
    COMPILE = "compile"
    EXECUTE = "execute"
    VERIFY = "verify"
    AUDIT = "audit"
    COMPLETE = "complete"
    FAILED = "failed"


# PURPOSE: [L2-auto] フェーズ結果
@dataclass
class PhaseResult:
    """フェーズ結果"""
    phase: ExecutionPhase
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0


# PURPOSE: [L2-auto] 実行パイプライン結果
@dataclass
class ExecutionPipeline:
    """実行パイプライン結果"""
    ccl: str
    context: str
    workflow_name: str = ""
    
    # フェーズ結果
    compile_result: Optional[PhaseResult] = None
    execute_result: Optional[PhaseResult] = None
    verify_result: Optional[PhaseResult] = None
    audit_result: Optional[PhaseResult] = None
    
    # 最終結果
    success: bool = False
    output: str = ""
    lmql_code: str = ""
    
    # 検証情報
    verified: bool = False
    confidence: float = 0.0
    
    # 監査情報
    audit_id: str = ""
    
    # メタデータ
    total_duration_ms: float = 0.0
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    model: str = ""
    
    # PURPOSE: 辞書に変換
    def to_dict(self) -> Dict[str, Any]:
        """辞書に変換"""
        return {
            "ccl": self.ccl,
            "context": self.context,
            "workflow_name": self.workflow_name,
            "success": self.success,
            "output": self.output,
            "verified": self.verified,
            "confidence": self.confidence,
            "audit_id": self.audit_id,
            "total_duration_ms": self.total_duration_ms
        }


# =============================================================================
# Executor
# =============================================================================

# PURPOSE: [L2-auto] ワークフロー実行エンジン
class WorkflowExecutor:
    """ワークフロー実行エンジン
    
    CCL を完全なパイプラインで実行する。
    
    Usage:
        executor = WorkflowExecutor()
        result = await executor.execute("/noe+", context="分析対象")
        print(result.output)
    """
    
    # PURPOSE: Initialize instance
    def __init__(
        self,
        registry: Optional["WorkflowRegistry"] = None,
        model: str = "openai/gpt-4o",
        verify_by_default: bool = True,
        audit_by_default: bool = True,
        min_confidence: float = 0.7
    ):
        self._registry = registry
        self.model = model
        self.verify_by_default = verify_by_default
        self.audit_by_default = audit_by_default
        self.min_confidence = min_confidence
        self._tape = None
    
    # PURPOSE: レジストリを取得 (遅延初期化)
    @property
    def registry(self):
        """レジストリを取得 (遅延初期化)"""
        if self._registry is None:
            from .registry import WorkflowRegistry
            self._registry = WorkflowRegistry()
        return self._registry
    
    # PURPOSE: CCL ワークフローを実行
    async def execute(
        self,
        ccl: str,
        context: str = "",
        verify: Optional[bool] = None,
        audit: Optional[bool] = None,
        model: Optional[str] = None,
        **kwargs
    ) -> ExecutionPipeline:
        """CCL ワークフローを実行
        
        Args:
            ccl: CCL 式 (例: "/noe+", "/bou+ >> /ene+")
            context: 実行コンテキスト
            verify: 検証するか (デフォルト: verify_by_default)
            audit: 監査記録するか (デフォルト: audit_by_default)
            model: 使用するモデル
            
        Returns:
            ExecutionPipeline
        """
        start_time = time.time()
        
        verify = verify if verify is not None else self.verify_by_default
        audit = audit if audit is not None else self.audit_by_default
        model = model or self.model
        
        pipeline = ExecutionPipeline(
            ccl=ccl,
            context=context,
            model=model
        )
        
        try:
            # Phase 1: Compile
            pipeline.compile_result = await self._phase_compile(ccl, model)
            self._tape_phase(pipeline, pipeline.compile_result)
            if not pipeline.compile_result.success:
                pipeline.success = False
                return self._finalize(pipeline, start_time)
            
            pipeline.lmql_code = pipeline.compile_result.output
            
            # ワークフロー名を取得
            pipeline.workflow_name = self._extract_workflow_name(ccl)
            
            # Phase 2: Execute
            pipeline.execute_result = await self._phase_execute(
                ccl, context, model
            )
            self._tape_phase(pipeline, pipeline.execute_result)
            if not pipeline.execute_result.success:
                pipeline.success = False
                return self._finalize(pipeline, start_time)
            
            pipeline.output = pipeline.execute_result.output
            
            # Phase 2.5: Canvas-CoT ノード登録
            canvas = self._create_canvas(ccl)
            if canvas and pipeline.output:
                canvas.insert(
                    pipeline.output[:500],
                    source="execution",
                    confidence=50,  # 初期確信度
                )
            
            # Phase 3: Verify (オプション)
            if verify:
                # dynamic_voices: 確信度に基づく Voice 選択
                voices_prompt = self._build_voices_prompt(
                    pipeline.output, pipeline.confidence
                )
                verify_context = context
                if voices_prompt:
                    verify_context = f"{context}\n\n{voices_prompt}" if context else voices_prompt
                
                pipeline.verify_result = await self._phase_verify(
                    ccl, pipeline.output, verify_context
                )
                self._tape_phase(pipeline, pipeline.verify_result)
                pipeline.verified = pipeline.verify_result.success
                if pipeline.verify_result.output:
                    pipeline.confidence = getattr(
                        pipeline.verify_result.output, 
                        "confidence", 
                        0.0
                    )
                
                # Canvas: 検証結果に基づくノード更新
                if canvas and canvas.active_nodes():
                    node = canvas.active_nodes()[0]
                    if pipeline.verified:
                        canvas.modify(node.id, node.content, reason=f"verified (conf={pipeline.confidence:.0%})")
                    else:
                        canvas.modify(node.id, node.content, reason="verification failed")
            
            # Phase 4: Audit (オプション)
            if audit:
                pipeline.audit_result = await self._phase_audit(
                    ccl, pipeline.output, pipeline.verify_result
                )
                self._tape_phase(pipeline, pipeline.audit_result)
                if pipeline.audit_result.output:
                    pipeline.audit_id = pipeline.audit_result.output
            
            pipeline.success = True
            
        except Exception as e:
            pipeline.success = False
            pipeline.execute_result = PhaseResult(
                phase=ExecutionPhase.FAILED,
                success=False,
                error=str(e)
            )
        
        return self._finalize(pipeline, start_time)
    
    # PURPOSE: 同期版の実行
    def execute_sync(
        self,
        ccl: str,
        context: str = "",
        **kwargs
    ) -> ExecutionPipeline:
        """同期版の実行"""
        return asyncio.run(self.execute(ccl, context, **kwargs))
    
    # PURPOSE: コンパイルフェーズ
    async def _phase_compile(
        self,
        ccl: str,
        model: str
    ) -> PhaseResult:
        """コンパイルフェーズ"""
        start = time.time()
        
        try:
            from hermeneus.src import compile_ccl
            from hermeneus.src.macros import get_all_macros

            # Auto-load all registered macros (builtin + ccl/macros/)
            macros = get_all_macros()
            lmql_code = compile_ccl(ccl, macros=macros, model=model)
            
            return PhaseResult(
                phase=ExecutionPhase.COMPILE,
                success=True,
                output=lmql_code,
                duration_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return PhaseResult(
                phase=ExecutionPhase.COMPILE,
                success=False,
                error=str(e),
                duration_ms=(time.time() - start) * 1000
            )
    
    # PURPOSE: 実行フェーズ
    async def _phase_execute(
        self,
        ccl: str,
        context: str,
        model: str
    ) -> PhaseResult:
        """実行フェーズ
        
        compile_ccl → LMQLExecutor.execute_async の非同期パイプライン。
        同期版 execute_ccl は asyncio.run() を内部で呼ぶため、
        既に async コンテキストにいる executor.execute() からは使えない。
        """
        start = time.time()
        
        try:
            from hermeneus.src import compile_ccl
            from hermeneus.src.macros import get_all_macros
            from hermeneus.src.runtime import LMQLExecutor, ExecutionConfig
            
            # Step 1: compile (LMQL コード生成)
            macros = get_all_macros()
            lmql_code = compile_ccl(ccl, macros=macros, model=model)
            
            # Step 2: LLM で実行 (非同期)
            config = ExecutionConfig(model=model)
            llm = LMQLExecutor(config)
            result = await llm.execute_async(lmql_code, context=context)
            
            return PhaseResult(
                phase=ExecutionPhase.EXECUTE,
                success=result.status.value == "success",
                output=result.output,
                error=result.error if hasattr(result, "error") else None,
                duration_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return PhaseResult(
                phase=ExecutionPhase.EXECUTE,
                success=False,
                error=str(e),
                duration_ms=(time.time() - start) * 1000
            )
    
    # PURPOSE: 検証フェーズ
    async def _phase_verify(
        self,
        ccl: str,
        output: str,
        context: str
    ) -> PhaseResult:
        """検証フェーズ"""
        start = time.time()
        
        try:
            from hermeneus.src.verifier import verify_execution_async
            
            result = await verify_execution_async(
                ccl=ccl,
                execution_output=output,
                context=context
            )
            
            return PhaseResult(
                phase=ExecutionPhase.VERIFY,
                success=result.accepted,
                output=result,
                duration_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return PhaseResult(
                phase=ExecutionPhase.VERIFY,
                success=False,
                error=str(e),
                duration_ms=(time.time() - start) * 1000
            )
    
    # PURPOSE: 監査フェーズ
    async def _phase_audit(
        self,
        ccl: str,
        output: str,
        verify_result: Optional[PhaseResult]
    ) -> PhaseResult:
        """監査フェーズ"""
        start = time.time()
        
        try:
            def _record_sync():
                from hermeneus.src.audit import record_verification

                consensus = verify_result.output if verify_result else None

                if consensus:
                    return record_verification(ccl, output, consensus)
                else:
                    # 検証なしの場合はダミー記録
                    from .audit import AuditStore, AuditRecord
                    store = AuditStore()
                    record = AuditRecord(
                        record_id="",
                        ccl_expression=ccl,
                        execution_result=output[:500],
                        debate_summary="検証スキップ",
                        consensus_accepted=True,
                        confidence=0.5,
                        dissent_reasons=[]
                    )
                    return store.record(record)

            import asyncio
            audit_id = await asyncio.to_thread(_record_sync)
            
            return PhaseResult(
                phase=ExecutionPhase.AUDIT,
                success=True,
                output=audit_id,
                duration_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            return PhaseResult(
                phase=ExecutionPhase.AUDIT,
                success=False,
                error=str(e),
                duration_ms=(time.time() - start) * 1000
            )
    
    # PURPOSE: CCL からワークフロー名を抽出
    def _extract_workflow_name(self, ccl: str) -> str:
        """CCL からワークフロー名を抽出"""
        # /noe+ → noe, /bou+ >> /ene+ → bou
        import re
        match = re.search(r"/([a-zA-Z]+)[+\-]?", ccl)
        return match.group(1) if match else ""
    
    # PURPOSE: Canvas-CoT インスタンスを生成
    def _create_canvas(self, ccl: str):
        """Canvas-CoT インスタンスを生成。失敗時は None。"""
        try:
            from hermeneus.src.canvas import Canvas
            tape = self._get_tape()
            return Canvas(tape=tape, wf=ccl)
        except Exception:
            return None
    
    # PURPOSE: dynamic_voices プロンプトを構築
    def _build_voices_prompt(self, output: str, confidence: float) -> str:
        """確信度に基づいて Voice セットを選択し、検証プロンプトを構築。
        
        Args:
            output: 実行結果の出力
            confidence: 現在の確信度 (0.0-1.0)
            
        Returns:
            Voice プロンプト文字列 (Voice 追加なしなら空文字)
        """
        try:
            from hermeneus.src.voices import select_voices, format_voices_prompt
            
            # confidence は 0.0-1.0 → 0-100 に変換
            conf_pct = confidence * 100 if confidence <= 1.0 else confidence
            voices = select_voices(conf_pct)
            
            # Base voices のみ (3) なら追加プロンプト不要
            if len(voices) <= 3:
                return ""
            
            return format_voices_prompt(voices, hypothesis=output[:200])
        except Exception:
            return ""
    
    # PURPOSE: CCL から全ワークフロー ID を抽出
    def _extract_all_workflow_ids(self, ccl: str) -> list:
        """CCL 内の全ワークフロー ID を抽出
        
        例: /bou+_/chr_/hod → ['bou', 'chr', 'hod']
        """
        import re
        return re.findall(r"/([a-zA-Z]+)[+\-]?", ccl)
    
    # PURPOSE: 定理使用を記録
    def _record_theorem_usage(self, pipeline: ExecutionPipeline) -> None:
        """成功した WF 実行から定理使用を自動記録する。"""
        if not pipeline.success:
            return
        
        try:
            from mekhane.fep.theorem_recommender import record_usage, THEOREM_KEYWORDS
            
            # command → theorem_id の逆引きテーブル
            cmd_to_theorem = {
                t["command"].lstrip("/"): t["id"]
                for t in THEOREM_KEYWORDS
            }
            
            wf_ids = self._extract_all_workflow_ids(pipeline.ccl)
            context = pipeline.context[:80] if pipeline.context else ""
            
            for wf_id in wf_ids:
                theorem_id = cmd_to_theorem.get(wf_id)
                if theorem_id:
                    record_usage(theorem_id, context)
        except Exception:
            # 定理記録の失敗はパイプライン実行を妨げない
            pass
    
    # PURPOSE: パイプラインを完了
    def _finalize(
        self,
        pipeline: ExecutionPipeline,
        start_time: float
    ) -> ExecutionPipeline:
        """パイプラインを完了"""
        pipeline.total_duration_ms = (time.time() - start_time) * 1000
        pipeline.completed_at = datetime.now()
        
        # 定理使用を自動記録
        self._record_theorem_usage(pipeline)
        
        # WF 実行トレースを tape に記録
        self._record_tape(pipeline)
        
        return pipeline
    
    # PURPOSE: Tape インスタンスを遅延取得
    def _get_tape(self):
        """TapeWriter を遅延初期化して共有する。"""
        if self._tape is None:
            try:
                from mekhane.tape import TapeWriter
                self._tape = TapeWriter()
            except Exception:
                pass
        return self._tape
    
    # PURPOSE: フェーズ完了時の tape 記録
    def _tape_phase(self, pipeline: ExecutionPipeline, result: PhaseResult) -> None:
        """各フェーズ完了時に tape へ記録。失敗してもパイプラインをブロックしない。"""
        try:
            tape = self._get_tape()
            if tape:
                tape.log(
                    wf=pipeline.ccl,
                    step=result.phase.value.upper(),
                    success=result.success,
                    duration_ms=round(result.duration_ms, 1),
                    error=result.error,
                )
        except Exception:
            pass
    
    # PURPOSE: WF 実行トレースの最終サマリーを tape に記録
    def _record_tape(self, pipeline: ExecutionPipeline) -> None:
        """パイプライン完了時の最終サマリーを記録。"""
        try:
            tape = self._get_tape()
            if tape:
                tape.log(
                    wf=pipeline.ccl,
                    step="COMPLETE" if pipeline.success else "FAILED",
                    workflow_name=pipeline.workflow_name,
                    confidence=pipeline.confidence,
                    duration_ms=round(pipeline.total_duration_ms, 1),
                    verified=pipeline.verified,
                    model=pipeline.model,
                )
        except Exception:
            pass


# =============================================================================
# Batch Executor
# =============================================================================

# PURPOSE: [L2-auto] バッチ実行エンジン
class BatchExecutor:
    """バッチ実行エンジン"""
    
    # PURPOSE: Initialize instance
    def __init__(self, executor: Optional[WorkflowExecutor] = None):
        self.executor = executor or WorkflowExecutor()
    
    # PURPOSE: 複数タスクをバッチ実行
    async def execute_batch(
        self,
        tasks: List[Dict[str, Any]],
        parallel: bool = True,
        max_concurrent: int = 5
    ) -> List[ExecutionPipeline]:
        """複数タスクをバッチ実行
        
        Args:
            tasks: タスクリスト [{"ccl": "/noe+", "context": "..."}, ...]
            parallel: 並列実行するか
            max_concurrent: 最大並列数
            
        Returns:
            結果リスト
        """
        if parallel:
            semaphore = asyncio.Semaphore(max_concurrent)
            
            # PURPOSE: Execute with semaphore
            async def execute_with_semaphore(task):
                async with semaphore:
                    return await self.executor.execute(**task)
            
            results = await asyncio.gather(
                *[execute_with_semaphore(task) for task in tasks]
            )
        else:
            results = []
            for task in tasks:
                result = await self.executor.execute(**task)
                results.append(result)
        
        return results


# =============================================================================
# Convenience Functions
# =============================================================================

_default_executor: Optional[WorkflowExecutor] = None


# PURPOSE: デフォルトエグゼキューターを取得
def get_executor() -> WorkflowExecutor:
    """デフォルトエグゼキューターを取得"""
    global _default_executor
    if _default_executor is None:
        _default_executor = WorkflowExecutor()
    return _default_executor


# PURPOSE: ワークフローを実行 (便利関数)
async def run_workflow(
    ccl: str,
    context: str = "",
    verify: bool = True,
    audit: bool = True
) -> ExecutionPipeline:
    """ワークフローを実行 (便利関数)
    
    Example:
        >>> result = await run_workflow("/noe+", context="分析対象")
        >>> print(result.output)
    """
    return await get_executor().execute(
        ccl=ccl,
        context=context,
        verify=verify,
        audit=audit
    )


# PURPOSE: ワークフローを同期実行 (便利関数)
def run_workflow_sync(
    ccl: str,
    context: str = "",
    verify: bool = True,
    audit: bool = True
) -> ExecutionPipeline:
    """ワークフローを同期実行 (便利関数)"""
    return asyncio.run(run_workflow(ccl, context, verify, audit))
