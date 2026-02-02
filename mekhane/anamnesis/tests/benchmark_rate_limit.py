import asyncio
import time
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from mekhane.anamnesis.collectors.base import BaseCollector
from mekhane.anamnesis.models.paper import Paper

class TestCollector(BaseCollector):
    name = "test"
    rate_limit = 1.0 # 1 request per second

    def search(self, query, max_results=10, categories=None):
        # Simulate work
        self._rate_limit_wait()
        return []

    def fetch_by_id(self, paper_id):
        return None

async def heartbeat(interval=0.1, duration=2.0):
    """Records max delay between wakeups."""
    max_delay = 0
    start = time.time()
    last_time = start

    while time.time() - start < duration:
        await asyncio.sleep(interval)
        now = time.time()
        delay = now - last_time - interval
        if delay > max_delay:
            max_delay = delay
        last_time = now

    return max_delay

async def run_blocking_test():
    collector = TestCollector()
    # Pre-set last request time to force a wait
    collector._last_request_time = time.time()

    print("Running blocking test (sync collect called directly in loop)...")

    # Run heartbeat in background
    heartbeat_task = asyncio.create_task(heartbeat(duration=1.5))

    # Wait a bit to let heartbeat start
    await asyncio.sleep(0.2)

    start_time = time.time()
    # Call blocking method directly
    # rate_limit is 1.0, so it should wait ~1.0s (since we just set last_request_time)
    # Actually, we need to ensure elapsed < min_interval.
    # min_interval = 1.0. elapsed ~ 0.2. So wait ~0.8s.
    collector.collect("test")
    duration = time.time() - start_time

    max_heartbeat_delay = await heartbeat_task

    print(f"Blocking Call Duration: {duration:.4f}s")
    print(f"Max Heartbeat Delay: {max_heartbeat_delay:.4f}s")

    if max_heartbeat_delay > 0.5:
        print("FAIL: Event loop was blocked!")
    else:
        print("PASS: Event loop was NOT blocked.")

async def run_async_test():
    collector = TestCollector()
    collector._last_request_time = time.time()

    print("\nRunning async test (using collect_async if available)...")

    heartbeat_task = asyncio.create_task(heartbeat(duration=1.5))
    await asyncio.sleep(0.2)

    start_time = time.time()

    if hasattr(collector, 'collect_async'):
        await collector.collect_async("test")
    else:
        print("collect_async not implemented yet.")

    duration = time.time() - start_time
    max_heartbeat_delay = await heartbeat_task

    print(f"Async Call Duration: {duration:.4f}s")
    print(f"Max Heartbeat Delay: {max_heartbeat_delay:.4f}s")

    if max_heartbeat_delay > 0.5:
        print("FAIL: Event loop was blocked!")
    else:
        print("PASS: Event loop was NOT blocked.")

if __name__ == "__main__":
    try:
        print("--- Baseline (Sync) ---")
        asyncio.run(run_blocking_test())
        print("\n--- Optimized (Async) ---")
        asyncio.run(run_async_test())
    except KeyboardInterrupt:
        pass
