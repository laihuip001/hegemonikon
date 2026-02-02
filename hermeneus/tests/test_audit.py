
import pytest
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from hermeneus.src.audit import AuditStore, AuditRecord

class TestAuditStore:
    @pytest.fixture
    def store(self, tmp_path):
        db_path = tmp_path / "test_audit.db"
        return AuditStore(db_path)

    def test_record_batch(self, store):
        records = [
            AuditRecord(
                record_id=f"id_{i}",
                ccl_expression=f"/test{i}",
                execution_result="success",
                debate_summary="none",
                consensus_accepted=True,
                confidence=0.9,
                dissent_reasons=[],
                timestamp=datetime.now(),
                metadata={"i": i}
            )
            for i in range(10)
        ]

        ids = store.record_batch(records)
        assert len(ids) == 10
        assert ids[0] == "id_0"

        # Verify in DB
        saved_records = store.query(limit=20)
        assert len(saved_records) == 10

        # Verify specific fields
        r0 = store.get("id_0")
        assert r0 is not None
        assert r0.ccl_expression == "/test0"
        assert r0.metadata["i"] == 0

    def test_transaction(self, store):
        records = [
            AuditRecord(
                record_id=f"txn_{i}",
                ccl_expression=f"/txn{i}",
                execution_result="success",
                debate_summary="none",
                consensus_accepted=True,
                confidence=0.9,
                dissent_reasons=[],
                timestamp=datetime.now(),
                metadata={}
            )
            for i in range(5)
        ]

        with store.transaction() as conn:
            for record in records:
                store.record(record, conn=conn)

        # Verify
        assert len(store.query(limit=10)) == 5
        assert store.get("txn_0") is not None

    def test_transaction_rollback(self, store):
        # Initial state
        store.record(AuditRecord(
            record_id="initial",
            ccl_expression="/init",
            execution_result="ok",
            debate_summary="",
            consensus_accepted=True,
            confidence=1.0,
            dissent_reasons=[]
        ))

        try:
            with store.transaction() as conn:
                store.record(AuditRecord(
                    record_id="fail",
                    ccl_expression="/fail",
                    execution_result="ok",
                    debate_summary="",
                    consensus_accepted=True,
                    confidence=1.0,
                    dissent_reasons=[]
                ), conn=conn)
                raise RuntimeError("Boom")
        except RuntimeError:
            pass

        # Verify rollback
        assert store.get("initial") is not None
        assert store.get("fail") is None

    def test_record_backward_compatibility(self, store):
        # Single record without conn
        rec = AuditRecord(
            record_id="compat",
            ccl_expression="/compat",
            execution_result="ok",
            debate_summary="",
            consensus_accepted=True,
            confidence=1.0,
            dissent_reasons=[]
        )
        store.record(rec)

        assert store.get("compat") is not None
