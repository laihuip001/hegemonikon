import asyncio
import time
import statistics
from pathlib import Path
from hermeneus.src.checkpointer import CCLCheckpointer, CheckpointWrite

DB_PATH = Path("benchmark_checkpoints.db")

async def monitor_loop(stop_event, lags):
    """Monitors the event loop lag."""
    while not stop_event.is_set():
        start = time.perf_counter()
        await asyncio.sleep(0.01)
        end = time.perf_counter()
        lag = (end - start) - 0.01
        lags.append(lag)

async def run_blocking_workload(checkpointer, count=100):
    """Runs synchronous put operations."""
    print(f"Running {count} synchronous put operations...")
    for i in range(count):
        checkpointer.put(CheckpointWrite(
            thread_id=f"thread-{i}",
            state={"count": i, "data": "x" * 1000} # simulate some data
        ))
    print("Finished blocking workload.")

async def run_async_workload(checkpointer, count=100):
    """Runs asynchronous put operations."""
    print(f"Running {count} asynchronous aput operations...")
    tasks = []
    for i in range(count):
        # We await each call to simulate sequential usage but non-blocking loop,
        # or we could gather them. Let's do sequential await to compare fairly with sync loop.
        await checkpointer.aput(CheckpointWrite(
            thread_id=f"thread-async-{i}",
            state={"count": i, "data": "x" * 1000}
        ))
    print("Finished async workload.")

async def measure(checkpointer, workload_func, name):
    lags = []
    stop_event = asyncio.Event()

    # Start monitor
    monitor_task = asyncio.create_task(monitor_loop(stop_event, lags))

    # Allow monitor to start
    await asyncio.sleep(0.05)

    # Run workload
    start_time = time.perf_counter()
    await workload_func(checkpointer, count=200)
    end_time = time.perf_counter()

    # Stop monitor
    stop_event.set()
    await monitor_task

    # Analyze results
    total_time = end_time - start_time
    avg_lag = statistics.mean(lags) if lags else 0
    max_lag = max(lags) if lags else 0

    print(f"\n--- {name} Results ---")
    print(f"Total time for 200 puts: {total_time:.4f}s")
    print(f"Average loop lag: {avg_lag*1000:.2f} ms")
    print(f"Max loop lag: {max_lag*1000:.2f} ms")

async def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    checkpointer = CCLCheckpointer(db_path=DB_PATH)

    await measure(checkpointer, run_blocking_workload, "Baseline (Sync put)")

    # Reset DB for fairness (optional, but good practice)
    if DB_PATH.exists():
        DB_PATH.unlink()
    checkpointer = CCLCheckpointer(db_path=DB_PATH) # Re-init

    await measure(checkpointer, run_async_workload, "Optimization (Async aput)")

    if DB_PATH.exists():
        DB_PATH.unlink()

if __name__ == "__main__":
    asyncio.run(main())
