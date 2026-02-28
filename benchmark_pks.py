import asyncio
import time
import sys
from typing import List

# Mock fastapi and pydantic
class MockFastAPI:
    def APIRouter(self, *args, **kwargs):
        class Router:
            def get(self, *args, **kwargs): return lambda f: f
            def post(self, *args, **kwargs): return lambda f: f
        return Router()
    def Query(self, *args, **kwargs): return None

sys.modules['fastapi'] = MockFastAPI()

class MockPydantic:
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    def Field(self, *args, **kwargs): return None

sys.modules['pydantic'] = MockPydantic()

import mekhane.api.routes.pks as pks_module

class DummyNugget:
    def __init__(self):
        self.title = "Test"
        self.abstract = "Abstract"
        self.source = "Source"
        self.relevance_score = 0.9
        self.url = "url"
        self.authors = "authors"
        self.push_reason = "reason"
        self.serendipity_score = 0.5
        self.suggested_questions = []

class DummyEngine:
    def auto_context_from_handoff(self) -> List[str]:
        # Block event loop
        start = time.time()
        while time.time() - start < 1.0:
            pass
        return ["topic1", "topic2"]

    def proactive_push(self, k: int) -> List[DummyNugget]:
        # Block event loop
        start = time.time()
        while time.time() - start < 1.0:
            pass
        return [DummyNugget() for _ in range(k)]

def mock_get_engine():
    return DummyEngine()

pks_module._get_engine = mock_get_engine

async def loop_monitor(stop_event):
    max_delay = 0.0
    while not stop_event.is_set():
        start = time.perf_counter()
        await asyncio.sleep(0.01)
        delay = time.perf_counter() - start - 0.01
        if delay > max_delay:
            max_delay = delay
    return max_delay

async def run_benchmark():
    stop_event = asyncio.Event()

    # Start loop monitor
    monitor_task = asyncio.create_task(loop_monitor(stop_event))

    # Let monitor task start properly
    await asyncio.sleep(0.05)

    # Run the endpoint
    start_time = time.perf_counter()
    res = await pks_module.run_push(k=5)
    end_time = time.perf_counter()

    stop_event.set()
    max_delay = await monitor_task

    print(f"Endpoint execution time: {end_time - start_time:.4f} seconds")
    print(f"Maximum event loop block delay: {max_delay:.4f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
