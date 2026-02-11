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

class ExecutionPhase(Enum):
    """実行フェーズ"""
    INIT = "init"
    COMPILE = "compile"
    EXECUTE = "execute"
    VERIFY = "verify"
    AUDIT = "audit"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class PhaseResult:
    """フェーズ結果"""
    phase: ExecutionPhase
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0


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

class WorkflowExecutor:
    """ワークフロー実行エンジン
    
    CCL を完全なパイプラインで実行する。
    
    Usage:
        executor = WorkflowExecutor()
        result = await executor.execute("/noe+", context="分析対象")
        print(result.output)
    """
    
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
    
    @property
    def registry(self):
        """レジストリを取得 (遅延初期化)"""
        if self._registry is None:
            from .registry import WorkflowRegistry
            self._registry = WorkflowRegistry()
        return self._registry
    
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
            if not pipeline.compile_result.success:
                pipeline.success = False
                return self._finalize(pipeline, start_time)
            
            pipeline.lmql_code = pipeline.compile_result.output
            
            # ワークフロー名を取得
            pipeline.workflow_name = self._extract_workflow_name(ccl)
            
            # Phase 2: Execute
            pipeline.execute_result = await self._phase_execute(
                ccl, context, model, lmql_code=pipeline.lmql_code
            )
            if not pipeline.execute_result.success:
                pipeline.success = False
                return self._finalize(pipeline, start_time)
            
            pipeline.output = pipeline.execute_result.output
            
            # Phase 3: Verify (オプション)
            if verify:
                pipeline.verify_result = await self._phase_verify(
                    ccl, pipeline.output, context
                )
                pipeline.verified = pipeline.verify_result.success
                if pipeline.verify_result.output:
                    pipeline.confidence = getattr(
                        pipeline.verify_result.output, 
                        "confidence", 
                        0.0
                    )
            
            # Phase 4: Audit (オプション)
            if audit:
                pipeline.audit_result = await self._phase_audit(
                    ccl, pipeline.output, pipeline.verify_result
                )
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
    
    def execute_sync(
        self,
        ccl: str,
        context: str = "",
        **kwargs
    ) -> ExecutionPipeline:
        """同期版の実行"""
        return asyncio.run(self.execute(ccl, context, **kwargs))
    
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
            # Run in thread to avoid blocking loop (file I/O in get_all_macros, CPU in compile_ccl)
            macros = await asyncio.to_thread(get_all_macros)
            lmql_code = await asyncio.to_thread(compile_ccl, ccl, macros=macros, model=model)
            
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
    
    async def _phase_execute(
        self,
        ccl: str,
        context: str,
        model: str,
        lmql_code: Optional[str] = None
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
            # If lmql_code is provided (from _phase_compile), use it.
            if lmql_code is None:
                # Run in thread to avoid blocking loop (fallback compilation)
                macros = await asyncio.to_thread(get_all_macros)
                lmql_code = await asyncio.to_thread(compile_ccl, ccl, macros=macros, model=model)
            
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
    
    async def _phase_audit(
        self,
        ccl: str,
        output: str,
        verify_result: Optional[PhaseResult]
    ) -> PhaseResult:
        """監査フェーズ"""
        start = time.time()
        
        try:
            from hermeneus.src.audit import record_verification
            
            consensus = verify_result.output if verify_result else None
            
            if consensus:
                audit_id = record_verification(ccl, output, consensus)
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
                audit_id = store.record(record)
            
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
    
    def _extract_workflow_name(self, ccl: str) -> str:
        """CCL からワークフロー名を抽出"""
        # /noe+ → noe, /bou+ >> /ene+ → bou
        import re
        match = re.search(r"/(\w+)[+\-]?", ccl)
        return match.group(1) if match else ""
    
    def _finalize(
        self,
        pipeline: ExecutionPipeline,
        start_time: float
    ) -> ExecutionPipeline:
        """パイプラインを完了"""
        pipeline.total_duration_ms = (time.time() - start_time) * 1000
        pipeline.completed_at = datetime.now()
        return pipeline


# =============================================================================
# Batch Executor
# =============================================================================

class BatchExecutor:
    """バッチ実行エンジン"""
    
    def __init__(self, executor: Optional[WorkflowExecutor] = None):
        self.executor = executor or WorkflowExecutor()
    
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


def get_executor() -> WorkflowExecutor:
    """デフォルトエグゼキューターを取得"""
    global _default_executor
    if _default_executor is None:
        _default_executor = WorkflowExecutor()
    return _default_executor


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


def run_workflow_sync(
    ccl: str,
    context: str = "",
    verify: bool = True,
    audit: bool = True
) -> ExecutionPipeline:
    """ワークフローを同期実行 (便利関数)"""
    return asyncio.run(run_workflow(ccl, context, verify, audit))
