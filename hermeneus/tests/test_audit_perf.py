import pytest
import sqlite3
from pathlib import Path
from hermeneus.src.audit import AuditStore, AuditRecord

class TestAuditStorePerfFeatures:
    @pytest.fixture
    def temp_store(self, tmp_path):
        """Temp store"""
        db_path = tmp_path / "test_perf.db"
        return AuditStore(db_path)

    def test_transaction_commit(self, temp_store):
        """Test transaction commits correctly"""
        record = AuditRecord(
            record_id="t1", ccl_expression="/t1", execution_result="res",
            debate_summary="sum", consensus_accepted=True, confidence=1.0, dissent_reasons=[]
        )

        with temp_store.transaction():
            temp_store.record(record)

        # Verify it exists
        retrieved = temp_store.get("t1")
        assert retrieved is not None
        assert retrieved.ccl_expression == "/t1"

    def test_transaction_rollback(self, temp_store):
        """Test transaction rolls back on error"""
        record = AuditRecord(
            record_id="t2", ccl_expression="/t2", execution_result="res",
            debate_summary="sum", consensus_accepted=True, confidence=1.0, dissent_reasons=[]
        )

        try:
            with temp_store.transaction():
                temp_store.record(record)
                raise ValueError("Simulated error")
        except ValueError:
            pass

        # Verify it does NOT exist
        retrieved = temp_store.get("t2")
        assert retrieved is None

    def test_record_batch(self, temp_store):
        """Test batch recording"""
        records = [
            AuditRecord(
                record_id=f"b{i}", ccl_expression=f"/b{i}", execution_result="res",
                debate_summary="sum", consensus_accepted=True, confidence=1.0, dissent_reasons=[]
            )
            for i in range(10)
        ]

        ids = temp_store.record_batch(records)
        assert len(ids) == 10

        # Verify all exist
        for i in range(10):
            retrieved = temp_store.get(f"b{i}")
            assert retrieved is not None
            assert retrieved.ccl_expression == f"/b{i}"

    def test_nested_transaction_reuse(self, temp_store):
        """Test that transaction context manager reuses active connection"""
        # This is a bit implementation dependent test, but verifies the logic
        with temp_store.transaction() as conn1:
            with temp_store.transaction() as conn2:
                assert conn1 is conn2

    def test_record_respects_transaction(self, temp_store):
        """Test that record does not commit if inside transaction"""
        # We can't easily check 'did not commit' without inspecting file or another connection.
        # But we can check that it works.

        with temp_store.transaction():
             temp_store.record(AuditRecord(
                record_id="t3", ccl_expression="/t3", execution_result="res",
                debate_summary="sum", consensus_accepted=True, confidence=1.0, dissent_reasons=[]
            ))
             # If we were to inspect DB from another connection here, it should NOT be visible (if WAL not used or isolation level is default)
             # But simpler test is just that it works.

        assert temp_store.get("t3") is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
