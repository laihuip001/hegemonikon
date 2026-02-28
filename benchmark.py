import time
import asyncio
import json
import os
import shutil
from pathlib import Path
from mekhane.api.routes.digestor import list_reports, DIGESTOR_DIR
from concurrent.futures import ThreadPoolExecutor

def setup_dummy_files(num_files=1000):
    os.makedirs(DIGESTOR_DIR, exist_ok=True)
    for i in range(num_files):
        data = {
            "timestamp": f"2023-10-10T10:00:00.{i}",
            "source": "gnosis",
            "total_papers": 10,
            "candidates_selected": 2,
            "dry_run": True,
            "candidates": [
                {"title": "Paper 1", "score": 0.9},
                {"title": "Paper 2", "score": 0.8}
            ]
        }
        with open(DIGESTOR_DIR / f"digest_report_{i}.json", "w") as f:
            json.dump(data, f)

async def measure_concurrent(num_concurrent=100):
    start_time = time.perf_counter()
    tasks = [list_reports(limit=50, offset=0) for _ in range(num_concurrent)]
    await asyncio.gather(*tasks)
    end_time = time.perf_counter()
    return end_time - start_time

async def main():
    setup_dummy_files(500)

    # Warmup
    await list_reports(limit=50, offset=0)

    # Run concurrent test
    time_taken = await measure_concurrent(20) # Reduded to avoid ulimit
    print(f"Time taken for 20 concurrent requests: {time_taken:.4f} seconds")

    shutil.rmtree(DIGESTOR_DIR)

if __name__ == "__main__":
    asyncio.run(main())
