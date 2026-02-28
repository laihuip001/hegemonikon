import asyncio
import time
from hermeneus.src.executor import WorkflowExecutor, PhaseResult, ExecutionPhase

async def measure_event_loop_delay():
    # Let's create a verify result with large output to increase DB work
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

    print(f"Max event loop delay: {max_delay * 1000:.2f} ms")
    print(f"Average event loop delay: {avg_delay * 1000:.2f} ms")

if __name__ == "__main__":
    asyncio.run(measure_event_loop_delay())
