import asyncio
import time
from unittest.mock import MagicMock
import sys

from hermeneus.src.executor import WorkflowExecutor
from hermeneus.src.executor import PhaseResult, ExecutionPhase

async def benchmark(n: int, executor: WorkflowExecutor, ccl: str, output: str, verify_result: PhaseResult):
    start = time.time()

    tasks = []
    for _ in range(n):
        tasks.append(executor._phase_audit(ccl, output, verify_result))

    await asyncio.gather(*tasks)

    end = time.time()
    return end - start

async def main():
    executor = WorkflowExecutor()
    ccl = "test ccl"
    output = "test output"
    verify_result = PhaseResult(phase=ExecutionPhase.VERIFY, success=True, output=MagicMock())

    n = 50
    duration = await benchmark(n, executor, ccl, output, verify_result)
    print(f"Time for {n} _phase_audit calls: {duration:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
