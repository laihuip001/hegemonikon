import asyncio
import time
from hermeneus.src.executor import WorkflowExecutor, PhaseResult, ExecutionPhase

async def blocking_task():
    # A task that runs frequently and measures its own delay
    delays = []
    for _ in range(100):
        start = time.perf_counter()
        await asyncio.sleep(0.01)
        end = time.perf_counter()
        delays.append(end - start - 0.01)
    return sum(delays) / len(delays)

async def run_audits(executor):
    for i in range(50):
        await executor._phase_audit(
            ccl=f"/test{i}",
            output="test output",
            verify_result=None
        )

async def main():
    executor = WorkflowExecutor()

    # Run the audits and the blocking task concurrently
    # The blocking task should experience higher delays if _phase_audit blocks the event loop

    task1 = asyncio.create_task(run_audits(executor))
    task2 = asyncio.create_task(blocking_task())

    await task1
    avg_delay = await task2

    print(f"Average event loop delay: {avg_delay * 1000:.2f} ms")

if __name__ == "__main__":
    asyncio.run(main())
