# PROOF: [L2/インフラ] Synergeia Adapter
"""
Hermēneus Synergeia Adapter — Synergeia 統合

Synergeia 分散実行システムと Hermēneus を統合し、
CCL ワークフローを分散スレッドで実行可能にする。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


# =============================================================================
# Types
# =============================================================================

class ThreadStatus(Enum):
    """スレッドステータス"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ThreadConfig:
    """スレッド設定"""
    name: str
    ccl: str
    context: str = ""
    model: str = "openai/gpt-4o"
    priority: int = 0
    timeout_seconds: int = 300
    verify: bool = True
    audit: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreadResult:
    """スレッド実行結果"""
    thread_name: str
    ccl: str
    status: ThreadStatus
    output: str = ""
    verified: bool = False
    confidence: float = 0.0
    audit_id: str = ""
    error: Optional[str] = None
    duration_ms: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書に変換"""
        return {
            "thread_name": self.thread_name,
            "ccl": self.ccl,
            "status": self.status.value,
            "output": self.output,
            "verified": self.verified,
            "confidence": self.confidence,
            "audit_id": self.audit_id,
            "error": self.error,
            "duration_ms": self.duration_ms
        }


@dataclass
class ExecutionPlan:
    """実行プラン"""
    threads: List[ThreadConfig]
    parallel: bool = True
    max_concurrent: int = 5
    total_timeout_seconds: int = 600


# =============================================================================
# Synergeia Adapter
# =============================================================================

class SynergeiaAdapter:
    """Synergeia 統合アダプター
    
    Synergeia 分散実行システムと Hermēneus を統合する。
    
    Usage:
        adapter = SynergeiaAdapter()
        result = await adapter.execute_thread(thread_config)
    """
    
    def __init__(self, executor: Optional["WorkflowExecutor"] = None):
        self._executor = executor
    
    @property
    def executor(self):
        """エグゼキューターを取得 (遅延初期化)"""
        if self._executor is None:
            from .executor import WorkflowExecutor
            self._executor = WorkflowExecutor()
        return self._executor
    
    async def execute_thread(
        self,
        config: ThreadConfig
    ) -> ThreadResult:
        """単一スレッドを実行
        
        Args:
            config: スレッド設定
            
        Returns:
            ThreadResult
        """
        started_at = datetime.now()
        
        try:
            pipeline = await asyncio.wait_for(
                self.executor.execute(
                    ccl=config.ccl,
                    context=config.context,
                    verify=config.verify,
                    audit=config.audit,
                    model=config.model
                ),
                timeout=config.timeout_seconds
            )
            
            return ThreadResult(
                thread_name=config.name,
                ccl=config.ccl,
                status=ThreadStatus.COMPLETED if pipeline.success else ThreadStatus.FAILED,
                output=pipeline.output,
                verified=pipeline.verified,
                confidence=pipeline.confidence,
                audit_id=pipeline.audit_id,
                duration_ms=pipeline.total_duration_ms,
                started_at=started_at,
                completed_at=datetime.now()
            )
            
        except asyncio.TimeoutError:
            return ThreadResult(
                thread_name=config.name,
                ccl=config.ccl,
                status=ThreadStatus.FAILED,
                error=f"Timeout after {config.timeout_seconds}s",
                started_at=started_at,
                completed_at=datetime.now()
            )
        except Exception as e:
            return ThreadResult(
                thread_name=config.name,
                ccl=config.ccl,
                status=ThreadStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.now()
            )
    
    async def execute_plan(
        self,
        plan: ExecutionPlan
    ) -> List[ThreadResult]:
        """実行プランを実行
        
        Args:
            plan: 実行プラン
            
        Returns:
            スレッド結果リスト
        """
        if plan.parallel:
            return await self._execute_parallel(
                plan.threads,
                plan.max_concurrent,
                plan.total_timeout_seconds
            )
        else:
            return await self._execute_sequential(
                plan.threads,
                plan.total_timeout_seconds
            )
    
    async def _execute_parallel(
        self,
        threads: List[ThreadConfig],
        max_concurrent: int,
        timeout: int
    ) -> List[ThreadResult]:
        """並列実行"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(config):
            async with semaphore:
                return await self.execute_thread(config)
        
        try:
            results = await asyncio.wait_for(
                asyncio.gather(
                    *[execute_with_semaphore(t) for t in threads],
                    return_exceptions=True
                ),
                timeout=timeout
            )
            
            # 例外を ThreadResult に変換
            processed = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed.append(ThreadResult(
                        thread_name=threads[i].name,
                        ccl=threads[i].ccl,
                        status=ThreadStatus.FAILED,
                        error=str(result)
                    ))
                else:
                    processed.append(result)
            
            return processed
            
        except asyncio.TimeoutError:
            return [
                ThreadResult(
                    thread_name=t.name,
                    ccl=t.ccl,
                    status=ThreadStatus.CANCELLED,
                    error="Plan timeout"
                )
                for t in threads
            ]
    
    async def _execute_sequential(
        self,
        threads: List[ThreadConfig],
        timeout: int
    ) -> List[ThreadResult]:
        """順次実行"""
        results = []
        start_time = asyncio.get_event_loop().time()
        
        for config in threads:
            elapsed = asyncio.get_event_loop().time() - start_time
            remaining = timeout - elapsed
            
            if remaining <= 0:
                results.append(ThreadResult(
                    thread_name=config.name,
                    ccl=config.ccl,
                    status=ThreadStatus.CANCELLED,
                    error="Plan timeout"
                ))
                continue
            
            # 個別タイムアウトを調整
            config.timeout_seconds = min(
                config.timeout_seconds,
                int(remaining)
            )
            
            result = await self.execute_thread(config)
            results.append(result)
        
        return results
    
    def to_synergeia_format(
        self,
        results: List[ThreadResult]
    ) -> Dict[str, Any]:
        """Synergeia 形式に変換
        
        Synergeia Coordinator が期待する形式に変換する。
        """
        return {
            "execution_id": f"herm_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "total_threads": len(results),
            "completed": sum(
                1 for r in results 
                if r.status == ThreadStatus.COMPLETED
            ),
            "failed": sum(
                1 for r in results 
                if r.status == ThreadStatus.FAILED
            ),
            "results": [r.to_dict() for r in results],
            "summary": self._generate_summary(results)
        }
    
    def _generate_summary(self, results: List[ThreadResult]) -> str:
        """サマリーを生成"""
        completed = [r for r in results if r.status == ThreadStatus.COMPLETED]
        failed = [r for r in results if r.status == ThreadStatus.FAILED]
        
        lines = [
            f"# Hermēneus 実行サマリー",
            f"",
            f"- 総スレッド: {len(results)}",
            f"- 成功: {len(completed)}",
            f"- 失敗: {len(failed)}",
        ]
        
        if completed:
            avg_conf = sum(r.confidence for r in completed) / len(completed)
            lines.append(f"- 平均確信度: {avg_conf:.1%}")
        
        return "\n".join(lines)


# =============================================================================
# Plan Builder
# =============================================================================

class PlanBuilder:
    """実行プラン構築器"""
    
    def __init__(self):
        self.threads: List[ThreadConfig] = []
        self.parallel = True
        self.max_concurrent = 5
        self.timeout = 600
    
    def add_thread(
        self,
        name: str,
        ccl: str,
        context: str = "",
        **kwargs
    ) -> "PlanBuilder":
        """スレッドを追加"""
        self.threads.append(ThreadConfig(
            name=name,
            ccl=ccl,
            context=context,
            **kwargs
        ))
        return self
    
    def set_parallel(self, parallel: bool) -> "PlanBuilder":
        """並列実行を設定"""
        self.parallel = parallel
        return self
    
    def set_concurrency(self, max_concurrent: int) -> "PlanBuilder":
        """最大並列数を設定"""
        self.max_concurrent = max_concurrent
        return self
    
    def set_timeout(self, seconds: int) -> "PlanBuilder":
        """タイムアウトを設定"""
        self.timeout = seconds
        return self
    
    def build(self) -> ExecutionPlan:
        """プランを構築"""
        return ExecutionPlan(
            threads=self.threads,
            parallel=self.parallel,
            max_concurrent=self.max_concurrent,
            total_timeout_seconds=self.timeout
        )


# =============================================================================
# Convenience Functions
# =============================================================================

_default_adapter: Optional[SynergeiaAdapter] = None


def get_adapter() -> SynergeiaAdapter:
    """デフォルトアダプターを取得"""
    global _default_adapter
    if _default_adapter is None:
        _default_adapter = SynergeiaAdapter()
    return _default_adapter


async def execute_synergeia_thread(
    name: str,
    ccl: str,
    context: str = "",
    **kwargs
) -> ThreadResult:
    """Synergeia スレッドを実行 (便利関数)"""
    config = ThreadConfig(
        name=name,
        ccl=ccl,
        context=context,
        **kwargs
    )
    return await get_adapter().execute_thread(config)


def create_plan() -> PlanBuilder:
    """プランビルダーを作成 (便利関数)"""
    return PlanBuilder()
