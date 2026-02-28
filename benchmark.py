import asyncio
import time
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from mekhane.symploke.jules_daily_scheduler import run_slot_batch
import mekhane.symploke.run_specialists as rs
import mekhane.symploke.jules_daily_scheduler as jds

# Let's mock both jds.run_batch and rs.run_batch because of imports
async def mock_run_batch(specs, target_file, max_concurrent):
    sem = asyncio.Semaphore(max_concurrent)
    async def process(spec):
        async with sem:
            await asyncio.sleep(0.1) # pretend this is network time
            # must return "session_id" to not be counted as error
            return {"session_id": f"mock_{id(spec)}"}
    tasks = [process(s) for s in specs]
    return await asyncio.gather(*tasks)

rs.run_batch = mock_run_batch
jds.run_batch = mock_run_batch

# Actually monkeypatch the imported reference inside jules_daily_scheduler
# since it uses `from run_specialists import run_batch` internally!
async def main():
    # Because `run_slot_batch` does `from run_specialists import run_batch` inside it!
    # Let's monkeypatch sys.modules['run_specialists']
    import run_specialists
    run_specialists.run_batch = mock_run_batch

    files = [f"file_{i}.py" for i in range(10)]
    specs_per_file = 5
    api_keys = ["mock_key_1", "mock_key_2"]

    start_time = time.time()
    result = await run_slot_batch(
        files=files,
        specialists_per_file=specs_per_file,
        api_keys=api_keys,
        max_concurrent=6,
        dry_run=False,
        exclude_low_quality=False
    )
    end_time = time.time()

    print(f"Total time: {end_time - start_time:.2f} seconds")
    print(f"Total tasks: {result['total_tasks']}")

if __name__ == "__main__":
    asyncio.run(main())
