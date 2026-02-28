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

    async def ticker():
        for _ in range(50):
            start = time.perf_counter()
            await asyncio.sleep(0.001)
            end = time.perf_counter()
            delays.append(end - start - 0.001)

    executor = WorkflowExecutor()

    # We will monkey patch the method if offload is True, just for test
    if offload:
        original_audit = executor._phase_audit
        async def offloaded_audit(ccl, output, verify_result):
            # This is roughly what we'll do in the real code
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

    async def worker():
        for i in range(50):
            await executor._phase_audit(
                ccl=f"/test{i}",
                output="X" * 10000,
                verify_result=verify_result
            )

    # Warmup
    await executor._phase_audit("/test", "test", verify_result)

    task1 = asyncio.create_task(worker())
    task2 = asyncio.create_task(ticker())

    await task1
    await task2

    max_delay = max(delays)
    avg_delay = sum(delays) / len(delays)

    return max_delay, avg_delay

async def main():
    sync_max, sync_avg = await run_benchmark(offload=False)
    offload_max, offload_avg = await run_benchmark(offload=True)

    print("Baseline (Sync):")
    print(f"  Max delay: {sync_max * 1000:.2f} ms")
    print(f"  Avg delay: {sync_avg * 1000:.2f} ms")

    print("\nOptimized (Offload):")
    print(f"  Max delay: {offload_max * 1000:.2f} ms")
    print(f"  Avg delay: {offload_avg * 1000:.2f} ms")

if __name__ == "__main__":
    asyncio.run(main())
