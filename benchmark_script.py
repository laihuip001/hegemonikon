import asyncio
import time
import sys

# Mock objects and functions
class MockSpecialist:
    def __init__(self, id, name, category="Test"):
        self.id = id
        self.name = name
        self.category = category

class MockBasanosBridge:
    def get_perspectives_as_specialists(self, domains=None):
        return [MockSpecialist(f"spec_{i}", f"Specialist {i}") for i in range(10)]

async def mock_run_batch(specs, target_file, max_concurrent):
    await asyncio.sleep(0.5) # simulate network call taking 0.5 seconds per file
    return [{"session_id": "mock_id"} for _ in specs]

# Replace run_batch in original logic
original_run_batch = None

async def run_baseline(files, specs_per_file):
    bridge = MockBasanosBridge()
    total_started = 0
    total_failed = 0
    all_results = []

    start_time = time.time()
    for file_idx, target_file in enumerate(files, 1):
        specs = bridge.get_perspectives_as_specialists()[:specs_per_file]
        results = await mock_run_batch(specs, target_file, 6)

        started = sum(1 for r in results if "session_id" in r)
        failed = sum(1 for r in results if "error" in r)
        total_started += started
        total_failed += failed
    end_time = time.time()

    return end_time - start_time, total_started

async def run_optimized(files, specs_per_file):
    bridge = MockBasanosBridge()
    total_started = 0
    total_failed = 0
    all_results = []

    start_time = time.time()

    # Simulate what we'd change to
    async def process_file(file_idx, target_file):
        specs = bridge.get_perspectives_as_specialists()[:specs_per_file]
        results = await mock_run_batch(specs, target_file, 6)
        return results, target_file, specs

    tasks = [process_file(idx, f) for idx, f in enumerate(files, 1)]
    file_results = await asyncio.gather(*tasks)

    for results, target_file, specs in file_results:
        started = sum(1 for r in results if "session_id" in r)
        failed = sum(1 for r in results if "error" in r)
        total_started += started
        total_failed += failed

    end_time = time.time()

    return end_time - start_time, total_started

async def main():
    files = [f"file_{i}.py" for i in range(10)]
    specs_per_file = 3

    print("Running baseline...")
    base_time, base_started = await run_baseline(files, specs_per_file)
    print(f"Baseline time: {base_time:.2f}s, Started: {base_started}")

    print("Running optimized...")
    opt_time, opt_started = await run_optimized(files, specs_per_file)
    print(f"Optimized time: {opt_time:.2f}s, Started: {opt_started}")

if __name__ == "__main__":
    asyncio.run(main())
