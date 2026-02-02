# PROOF: [L2/インフラ] Checkpointer Async Tests
"""
Hermēneus Checkpointer Async Unit Tests
"""

import pytest
import sys
import asyncio
from pathlib import Path
from datetime import datetime

# パッケージパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hermeneus.src.checkpointer import (
    CCLCheckpointer, Checkpoint, CheckpointWrite
)

@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test_state.db"

@pytest.fixture
def checkpointer(db_path):
    return CCLCheckpointer(db_path=db_path)

@pytest.mark.asyncio
class TestCCLCheckpointerAsync:

    async def test_aput_and_aget(self, checkpointer):
        """非同期保存と取得"""
        write = CheckpointWrite(
            thread_id="test-async-001",
            state={"context": "async_test", "val": 123},
            metadata={"meta": "data"}
        )

        checkpoint = await checkpointer.aput(write)
        assert checkpoint.thread_id == "test-async-001"
        assert checkpoint.checkpoint_id is not None
        assert checkpoint.state["context"] == "async_test"

        # Verify sync retrieval works too
        retrieved_sync = checkpointer.get("test-async-001", checkpoint.checkpoint_id)
        assert retrieved_sync.state["val"] == 123

        # Verify async retrieval
        retrieved = await checkpointer.aget("test-async-001", checkpoint.checkpoint_id)
        assert retrieved is not None
        assert retrieved.checkpoint_id == checkpoint.checkpoint_id
        assert retrieved.state["context"] == "async_test"
        assert retrieved.metadata["meta"] == "data"

        # Get latest
        latest = await checkpointer.aget("test-async-001")
        assert latest.checkpoint_id == checkpoint.checkpoint_id

    async def test_alist(self, checkpointer):
        """非同期履歴取得"""
        thread_id = "test-async-002"

        for i in range(5):
            await checkpointer.aput(CheckpointWrite(
                thread_id=thread_id,
                state={"step": i}
            ))
            # Sleep slightly to ensure timestamp difference if needed (though sqlite handles insertion order usually)
            # But we sort by created_at. created_at has microsecond precision in python but sqlite stores as string ISO.
            # ISO format from datetime.now() includes microseconds.

        history = await checkpointer.alist(thread_id, limit=3)
        assert len(history) == 3
        assert history[0].state["step"] == 4  # Newest first
        assert history[1].state["step"] == 3
        assert history[2].state["step"] == 2

        # Pagination using 'before'
        second_page = await checkpointer.alist(thread_id, limit=2, before=history[2].checkpoint_id)
        assert len(second_page) == 2
        assert second_page[0].state["step"] == 1
        assert second_page[1].state["step"] == 0

    async def test_adelete(self, checkpointer):
        """非同期削除"""
        thread_id = "test-async-003"

        cp1 = await checkpointer.aput(CheckpointWrite(thread_id=thread_id, state={"id": 1}))
        cp2 = await checkpointer.aput(CheckpointWrite(thread_id=thread_id, state={"id": 2}))

        # Delete specific
        await checkpointer.adelete(thread_id, cp1.checkpoint_id)

        assert await checkpointer.aget(thread_id, cp1.checkpoint_id) is None
        assert await checkpointer.aget(thread_id, cp2.checkpoint_id) is not None

        # Delete all for thread
        await checkpointer.adelete(thread_id)
        assert await checkpointer.aget(thread_id, cp2.checkpoint_id) is None

    async def test_concurrency(self, checkpointer):
        """並行実行テスト"""
        # Ensure that multiple async calls don't crash or block each other (logic wise)
        # Note: SQLite writes are serialized by the driver/engine, but we want to ensure our locking (implicit or explicit) works.
        # Since we use new connection per operation, SQLite handles locking (busy timeout might occur if heavily contended, but for this test it's fine).

        async def worker(idx):
            thread_id = f"worker-{idx}"
            for i in range(10):
                await checkpointer.aput(CheckpointWrite(
                    thread_id=thread_id,
                    state={"idx": idx, "i": i}
                ))

        tasks = [worker(i) for i in range(5)]
        await asyncio.gather(*tasks)

        for i in range(5):
            thread_id = f"worker-{i}"
            history = await checkpointer.alist(thread_id, limit=100)
            assert len(history) == 10
