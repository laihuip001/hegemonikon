import asyncio
import time
from hermeneus.src.executor import WorkflowExecutor, PhaseResult, ExecutionPhase

async def main():
    executor = WorkflowExecutor()

    # We will measure how long it blocks the event loop
    # If we run it in an executor, the event loop should be able to run other tasks.

    # Let's run _phase_audit 50 times synchronously (currently) vs async (after)
    # Actually, we can just measure the time it takes to run _phase_audit

    start = time.perf_counter()
    for i in range(50):
        await executor._phase_audit(
            ccl=f"/test{i}",
            output="test output",
            verify_result=None
        )
    end = time.perf_counter()
    print(f"Time for 50 audits: {end - start:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
