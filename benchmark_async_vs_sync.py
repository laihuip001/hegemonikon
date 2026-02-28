import asyncio
import time
from unittest.mock import MagicMock
from hermeneus.src.executor import WorkflowExecutor, PhaseResult, ExecutionPhase
import sqlite3
import concurrent.futures

class OriginalExecutor(WorkflowExecutor):
    async def _phase_audit(self, ccl: str, output: str, verify_result: PhaseResult):
        start = time.time()
        try:
            from hermeneus.src.audit import record_verification
            consensus = verify_result.output if verify_result else None
            if consensus:
                audit_id = record_verification(ccl, output, consensus)
            else:
                from hermeneus.src.audit import AuditStore, AuditRecord
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
            return PhaseResult(phase=ExecutionPhase.AUDIT, success=True, output=audit_id, duration_ms=(time.time() - start) * 1000)
        except Exception as e:
            return PhaseResult(phase=ExecutionPhase.AUDIT, success=False, error=str(e), duration_ms=(time.time() - start) * 1000)

class NewExecutor(WorkflowExecutor):
    async def _phase_audit(self, ccl: str, output: str, verify_result: PhaseResult):
        start = time.time()
        try:
            loop = asyncio.get_running_loop()
            consensus = verify_result.output if verify_result else None

            def _sync_audit():
                if consensus:
                    from hermeneus.src.audit import record_verification
                    return record_verification(ccl, output, consensus)
                else:
                    from hermeneus.src.audit import AuditStore, AuditRecord
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

            audit_id = await loop.run_in_executor(None, _sync_audit)
            return PhaseResult(phase=ExecutionPhase.AUDIT, success=True, output=audit_id, duration_ms=(time.time() - start) * 1000)
        except Exception as e:
            return PhaseResult(phase=ExecutionPhase.AUDIT, success=False, error=str(e), duration_ms=(time.time() - start) * 1000)

async def test_blocking_impact(n_calls: int, delay: float):
    print(f"Testing with {n_calls} DB calls while running a background counter")

    # Background task to show event loop blocking
    counter = [0]
    async def ticker():
        try:
            while True:
                await asyncio.sleep(0.01)
                counter[0] += 1
        except asyncio.CancelledError:
            pass

    async def run_test(executor_class):
        executor = executor_class()

        # Setup DB delay mocking
        import hermeneus.src.audit
        original_connect = hermeneus.src.audit.AuditStore._connect

        from contextlib import contextmanager
        @contextmanager
        def delayed_connect(*args, **kwargs):
            time.sleep(delay)  # Simulate slow DB I/O
            with original_connect(*args, **kwargs) as conn:
                yield conn

        hermeneus.src.audit.AuditStore._connect = delayed_connect

        try:
            ccl = "test"
            output = "test"
            verify_result = PhaseResult(phase=ExecutionPhase.VERIFY, success=True, output=MagicMock())
            verify_result.output.accepted = True
            verify_result.output.confidence = 0.9
            verify_result.output.dissent_reasons = []
            verify_result.output.rounds = []
            verify_result.output.majority_ratio = 1.0
            verify_result.output.verdict = MagicMock()
            verify_result.output.verdict.type.value = "test"
            verify_result.output.verdict.reasoning = "test"

            # Reset counter
            counter[0] = 0
            ticker_task = asyncio.create_task(ticker())

            start_time = time.time()
            tasks = [executor._phase_audit(ccl, output, verify_result) for _ in range(n_calls)]
            await asyncio.gather(*tasks)
            end_time = time.time()

            ticker_task.cancel()

            return end_time - start_time, counter[0]
        finally:
            # Restore
            hermeneus.src.audit.AuditStore._connect = original_connect


    orig_time, orig_ticks = await run_test(OriginalExecutor)
    print(f"Original (Sync): Time={orig_time:.3f}s, Background Ticks={orig_ticks} (Blocked event loop)")

    new_time, new_ticks = await run_test(NewExecutor)
    print(f"New (Async with run_in_executor): Time={new_time:.3f}s, Background Ticks={new_ticks} (Free event loop)")

if __name__ == "__main__":
    asyncio.run(test_blocking_impact(10, 0.1))
