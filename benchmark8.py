import asyncio
import time
from hermeneus.src.executor import WorkflowExecutor, PhaseResult, ExecutionPhase

async def run_benchmark(offload=False):
    from dataclasses import dataclass

    @dataclass
    class DummyConsensus:
        accepted: bool = True
        confidence: float = 0.99
        rounds: list = tuple([1,2,3])
        majority_ratio: float = 0.99
        dissent_reasons: list = tuple(["reason1", "reason2"])

        class Verdict:
            class Type:
                value = "dummy"
            type = Type()
            reasoning = "Because dummy"
        verdict = Verdict()

    verify_result = PhaseResult(
        phase=ExecutionPhase.VERIFY,
        success=True,
        output=DummyConsensus(),
        duration_ms=10.0
    )

    delays = []

    # We want to measure the latency of other tasks running on the event loop.
    # When _phase_audit blocks, other tasks can't run.
    async def ticker():
        for _ in range(50):
            start = time.perf_counter()
            await asyncio.sleep(0) # yield control to event loop
            end = time.perf_counter()
            # How long did it take between yielding and getting control back?
            # That's the latency introduced by blocking tasks.
            delays.append(end - start)

    executor = WorkflowExecutor()

    # Simulate DB I/O delay in AuditStore
    from hermeneus.src.audit import AuditStore
    original_record = AuditStore.record
    def slow_record(self, audit):
        time.sleep(0.01) # 10ms simulated IO delay
        return original_record(self, audit)
    AuditStore.record = slow_record

    if offload:
        original_audit = executor._phase_audit
        async def offloaded_audit(ccl, output, verify_result):
            def sync_part():
                from hermeneus.src.audit import record_verification
                from hermeneus.src.audit import AuditStore, AuditRecord
                consensus = verify_result.output if verify_result else None
                if consensus:
                    return record_verification(ccl, output, consensus)
                else:
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

            start = time.time()
            try:
                loop = asyncio.get_event_loop()
                audit_id = await loop.run_in_executor(None, sync_part)
                return PhaseResult(
                    phase=ExecutionPhase.AUDIT,
                    success=True,
                    output=audit_id,
                    duration_ms=(time.time() - start) * 1000
                )
            except Exception as e:
                pass
        executor._phase_audit = offloaded_audit

    # Run tasks concurrently.
    # The worker task does the auditing.
    async def worker():
        # Start audits
        for i in range(10):
            # In sync mode, this will block the loop for ~10ms each call
            await executor._phase_audit(
                ccl=f"/test{i}",
                output="X" * 100,
                verify_result=verify_result
            )

    # Warmup
    await executor._phase_audit("/test", "test", verify_result)

    # Start the ticker first, then the worker
    task1 = asyncio.create_task(ticker())
    task2 = asyncio.create_task(worker())

    await asyncio.gather(task1, task2)

    AuditStore.record = original_record

    # Calculate delays
    max_delay = max(delays)
    avg_delay = sum(delays) / len(delays)
    total_blocked_time = sum(d for d in delays if d > 0.005) # Sum of blocks > 5ms

    return max_delay, avg_delay, total_blocked_time

async def main():
    sync_max, sync_avg, sync_blocked = await run_benchmark(offload=False)
    offload_max, offload_avg, offload_blocked = await run_benchmark(offload=True)

    print("Baseline (Sync DB I/O):")
    print(f"  Max Event Loop Block Time: {sync_max * 1000:.2f} ms")
    print(f"  Avg Event Loop Block Time: {sync_avg * 1000:.2f} ms")
    print(f"  Total Time Blocked (>5ms): {sync_blocked * 1000:.2f} ms")

    print("\nOptimized (run_in_executor DB I/O):")
    print(f"  Max Event Loop Block Time: {offload_max * 1000:.2f} ms")
    print(f"  Avg Event Loop Block Time: {offload_avg * 1000:.2f} ms")
    print(f"  Total Time Blocked (>5ms): {offload_blocked * 1000:.2f} ms")

if __name__ == "__main__":
    asyncio.run(main())
