import asyncio
import time
from hermeneus.src.executor import WorkflowExecutor

async def measure_event_loop_delay():
    # Measure the event loop delay when running _phase_audit
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
                output="X" * 10000, # Large output to increase DB work
                verify_result=None
            )

    # Warmup
    await executor._phase_audit("/test", "test", None)

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
