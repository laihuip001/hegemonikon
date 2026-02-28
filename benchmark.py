import asyncio
import time
from unittest.mock import patch, MagicMock

# Import the module to be optimized
import sys
sys.path.append("mekhane/symploke")
import jules_daily_scheduler

# Mock out dependencies to just measure the concurrent scheduling part
async def mock_run_batch(specs, target_file, max_concurrent):
    await asyncio.sleep(0.1) # Simulate network/API delay
    return [{"session_id": "test_id"} for _ in specs]

async def benchmark_run_slot_batch():
    jules_daily_scheduler.run_batch = mock_run_batch

    # Setup test data
    files = [f"file_{i}.py" for i in range(10)]
    specialists_per_file = 5
    api_keys = ["key1", "key2"]

    class DummySpec:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    import run_specialists
    run_specialists.run_batch = mock_run_batch
    run_specialists.ALL_SPECIALISTS = [DummySpec(f"id_{i}", f"name_{i}") for i in range(100)]
    jules_daily_scheduler.ALL_SPECIALISTS = run_specialists.ALL_SPECIALISTS

    start_time = time.time()
    await jules_daily_scheduler.run_slot_batch(
        files=files,
        specialists_per_file=specialists_per_file,
        api_keys=api_keys,
        max_concurrent=6
    )
    end_time = time.time()

    print(f"Total time taken: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(benchmark_run_slot_batch())
