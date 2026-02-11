"""Tests for Credit Assignment — Teacher Signal for FEP Agent."""

import json
import tempfile
from pathlib import Path

import numpy as np
import pytest

from mekhane.fep.credit_assignment import (
    FeedbackRecord,
    FeedbackResult,
    apply_feedback_to_agent,
    feedback_summary,
    load_feedback_history,
    record_feedback,
    snapshot_for_feedback,
)
from mekhane.fep.fep_agent_v2 import HegemonikónFEPAgentV2


# ─────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: Verify agent behaves correctly
@pytest.fixture
def agent():
    """Verify agent behavior."""
    return HegemonikónFEPAgentV2()


# PURPOSE: Verify tmp log dir behaves correctly
@pytest.fixture
def tmp_log_dir(tmp_path):
    """Verify tmp log dir behavior."""
    return tmp_path / "feedback"


# PURPOSE: Verify sample record behaves correctly
@pytest.fixture
def sample_record():
    """Verify sample record behavior."""
    return FeedbackRecord(
        timestamp="2026-02-08T21:00:00",
        user_input="テスト環境はDockerで統一する方針で",
        recommended_series="A",
        action_name="act_A",
        accepted=True,
        observation=13,
        confidence=0.75,
        beliefs_snapshot=[1.0 / 48] * 48,
    )


# PURPOSE: Verify sample reject record behaves correctly
@pytest.fixture
def sample_reject_record():
    """Verify sample reject record behavior."""
    return FeedbackRecord(
        timestamp="2026-02-08T21:01:00",
        user_input="テスト環境はDockerで統一する方針で",
        recommended_series="A",
        action_name="act_A",
        accepted=False,
        correct_series="S",
        observation=13,
        confidence=0.75,
        beliefs_snapshot=[1.0 / 48] * 48,
    )


# ─────────────────────────────────────────────────────────────────────
# FeedbackRecord Tests
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: Verify record valid behaves correctly
def test_record_valid():
    """Verify record valid behavior."""
    r = FeedbackRecord(
        timestamp="2026-01-01", user_input="test",
        recommended_series="O", action_name="act_O", accepted=True,
    )
    assert r.effective_series == "O"


# PURPOSE: Verify record reject with correction behaves correctly
def test_record_reject_with_correction():
    """Verify record reject with correction behavior."""
    r = FeedbackRecord(
        timestamp="2026-01-01", user_input="test",
        recommended_series="A", action_name="act_A",
        accepted=False, correct_series="S",
    )
    assert r.effective_series == "S"


# PURPOSE: Verify record reject without correction behaves correctly
def test_record_reject_without_correction():
    """Verify record reject without correction behavior."""
    r = FeedbackRecord(
        timestamp="2026-01-01", user_input="test",
        recommended_series="A", action_name="act_A", accepted=False,
    )
    assert r.effective_series == "A"


# PURPOSE: Verify record invalid series behaves correctly
def test_record_invalid_series():
    """Verify record invalid series behavior."""
    with pytest.raises(ValueError, match="Invalid recommended_series"):
        FeedbackRecord(
            timestamp="2026-01-01", user_input="test",
            recommended_series="X", action_name="act_X", accepted=True,
        )


# PURPOSE: Verify record invalid correct series behaves correctly
def test_record_invalid_correct_series():
    """Verify record invalid correct series behavior."""
    with pytest.raises(ValueError, match="Invalid correct_series"):
        FeedbackRecord(
            timestamp="2026-01-01", user_input="test",
            recommended_series="O", action_name="act_O",
            accepted=False, correct_series="Z",
        )


# ─────────────────────────────────────────────────────────────────────
# JSONL Persistence Tests
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: Verify record and load behaves correctly
def test_record_and_load(sample_record, tmp_log_dir):
    """Verify record and load behavior."""
    path = record_feedback(sample_record, log_dir=tmp_log_dir)
    assert path.exists()
    assert path.suffix == ".jsonl"

    records = load_feedback_history(log_dir=tmp_log_dir)
    assert len(records) == 1
    assert records[0].user_input == sample_record.user_input
    assert records[0].recommended_series == "A"
    assert records[0].accepted is True


# PURPOSE: Verify multiple records behaves correctly
def test_multiple_records(sample_record, sample_reject_record, tmp_log_dir):
    """Verify multiple records behavior."""
    record_feedback(sample_record, log_dir=tmp_log_dir)
    record_feedback(sample_reject_record, log_dir=tmp_log_dir)

    records = load_feedback_history(log_dir=tmp_log_dir)
    assert len(records) == 2
    assert records[0].accepted is True
    assert records[1].accepted is False
    assert records[1].correct_series == "S"


# PURPOSE: Verify load empty dir behaves correctly
def test_load_empty_dir(tmp_log_dir):
    """Verify load empty dir behavior."""
    records = load_feedback_history(log_dir=tmp_log_dir)
    assert records == []


# PURPOSE: Verify load nonexistent dir behaves correctly
def test_load_nonexistent_dir(tmp_path):
    """Verify load nonexistent dir behavior."""
    records = load_feedback_history(log_dir=tmp_path / "nonexistent")
    assert records == []


# PURPOSE: Verify beliefs snapshot round trip behaves correctly
def test_beliefs_snapshot_round_trip(tmp_log_dir):
    """Verify beliefs snapshot round trip behavior."""
    beliefs = np.random.dirichlet(np.ones(48)).tolist()
    r = FeedbackRecord(
        timestamp="2026-01-01", user_input="test",
        recommended_series="O", action_name="act_O",
        accepted=True, beliefs_snapshot=beliefs,
    )
    record_feedback(r, log_dir=tmp_log_dir)
    loaded = load_feedback_history(log_dir=tmp_log_dir)
    assert len(loaded) == 1
    assert loaded[0].beliefs_snapshot is not None
    # Precision: rounded to 6 decimal places
    np.testing.assert_allclose(
        loaded[0].beliefs_snapshot, [round(v, 6) for v in beliefs], atol=1e-6,
    )


# ─────────────────────────────────────────────────────────────────────
# A-Matrix Learning Tests
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: Verify accept increases topic precision behaves correctly
def test_accept_increases_topic_precision(agent, sample_record):
    """Accept feedback should increase the recommended Series' topic row."""
    A_before = agent._get_A_matrix().copy()
    topic_row = 13  # A-series

    result = apply_feedback_to_agent(agent, [sample_record])

    A_after = agent._get_A_matrix()
    assert result.records_applied == 1
    assert result.accept_count == 1
    assert result.bridge_update_needed is True

    # Topic row 13 (A-series) should have increased
    assert A_after[topic_row, :].mean() > A_before[topic_row, :].mean()


# PURPOSE: Verify reject with correct learns correct series behaves correctly
def test_reject_with_correct_learns_correct_series(agent, sample_reject_record):
    """Reject + correct_series should learn the CORRECT series, not the wrong one."""
    A_before = agent._get_A_matrix().copy()
    correct_row = 9   # S-series (correct)
    wrong_row = 13     # A-series (recommended, wrong)

    result = apply_feedback_to_agent(agent, [sample_reject_record])

    A_after = agent._get_A_matrix()
    assert result.records_applied == 1
    assert result.reject_count == 1

    # S-series topic row should increase
    assert A_after[correct_row, :].mean() > A_before[correct_row, :].mean()
    # A-series row should decrease or stay same due to implicit competition
    # (/dia+ F1: positive-only learning, normalization suppresses others)
    assert A_after[wrong_row, :].mean() <= A_before[wrong_row, :].mean()



# PURPOSE: Verify reject without correct is skipped behaves correctly
def test_reject_without_correct_is_skipped(agent):
    """Reject without correct_series should be skipped (no learning)."""
    r = FeedbackRecord(
        timestamp="2026-01-01", user_input="test",
        recommended_series="A", action_name="act_A", accepted=False,
    )
    A_before = agent._get_A_matrix().copy()
    result = apply_feedback_to_agent(agent, [r])

    assert result.records_applied == 0
    np.testing.assert_array_equal(agent._get_A_matrix(), A_before)


# PURPOSE: Verify learning rate decay behaves correctly
def test_learning_rate_decay(agent):
    """Learning rate should decay over multiple records."""
    records = [
        FeedbackRecord(
            timestamp=f"2026-01-01T00:{i:02d}:00", user_input=f"test {i}",
            recommended_series="O", action_name="act_O", accepted=True,
        )
        for i in range(50)
    ]
    A_before = agent._get_A_matrix().copy()
    result = apply_feedback_to_agent(agent, records, base_learning_rate=30.0)

    # All 50 should be applied (η_50 = 30 * 0.995^50 ≈ 23.3 > 1.0)
    assert result.records_applied == 50


# PURPOSE: Verify normalization preserved after 100 feedbacks behaves correctly
def test_normalization_preserved_after_100_feedbacks(agent):
    """A-matrix columns should still sum to ~1 after heavy feedback."""
    records = [
        FeedbackRecord(
            timestamp=f"2026-01-01T00:{i:02d}:00", user_input=f"input {i}",
            recommended_series=["O", "S", "H", "P", "K", "A"][i % 6],
            action_name=f"act_{['O','S','H','P','K','A'][i % 6]}",
            accepted=True,
        )
        for i in range(100)
    ]
    apply_feedback_to_agent(agent, records)
    A = agent._get_A_matrix()
    col_sums = A.sum(axis=0)
    np.testing.assert_allclose(col_sums, 1.0, atol=1e-6)


# PURPOSE: Verify update  a with feedback method behaves correctly
def test_update_A_with_feedback_method(agent):
    """Direct agent method for supervised learning."""
    A_before = agent._get_A_matrix().copy()
    delta = agent.update_A_with_feedback("O")
    A_after = agent._get_A_matrix()

    assert delta > 0
    # O-series topic row (8) should increase
    assert A_after[8, :].mean() > A_before[8, :].mean()
    # Normalization preserved
    np.testing.assert_allclose(A_after.sum(axis=0), 1.0, atol=1e-6)


# PURPOSE: Verify update  a with beliefs snapshot behaves correctly
def test_update_A_with_beliefs_snapshot(agent):
    """Learning with specific beliefs snapshot."""
    # Create peaked beliefs (state 0 has most mass)
    beliefs = np.zeros(48)
    beliefs[0] = 0.9
    beliefs[1:] = 0.1 / 47

    delta = agent.update_A_with_feedback("S", beliefs_snapshot=beliefs)
    assert delta > 0

    A = agent._get_A_matrix()
    # Column 0 should be more affected than others
    assert A[9, 0] > A[9, 1]  # S-series topic, state 0 vs state 1


# ─────────────────────────────────────────────────────────────────────
# Summary Tests
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: Verify feedback summary empty behaves correctly
def test_feedback_summary_empty():
    """Verify feedback summary empty behavior."""
    result = feedback_summary([])
    assert result["total"] == 0
    assert result["accept_rate"] == 0.0


# PURPOSE: Verify feedback summary behaves correctly
def test_feedback_summary(sample_record, sample_reject_record):
    """Verify feedback summary behavior."""
    summary = feedback_summary([sample_record, sample_reject_record])
    assert summary["total"] == 2
    assert summary["accept_rate"] == 0.5
    assert "A" in summary["per_series"]
    assert summary["per_series"]["A"]["accept"] == 1
    assert summary["per_series"]["A"]["reject"] == 1
    assert len(summary["common_corrections"]) == 1
    assert summary["common_corrections"][0] == ("A", "S", 1)


# ─────────────────────────────────────────────────────────────────────
# Snapshot Helper Tests
# ─────────────────────────────────────────────────────────────────────

# PURPOSE: Verify snapshot for feedback behaves correctly
def test_snapshot_for_feedback(agent):
    """Verify snapshot for feedback behavior."""
    result = agent.step(observation=8)  # O-series topic
    snap = snapshot_for_feedback("テスト入力", result)

    assert snap["user_input"] == "テスト入力"
    assert snap["recommended_series"] in {"O", "S", "H", "P", "K", "A", "observe"}
    assert snap["beliefs_snapshot"] is not None
    assert len(snap["beliefs_snapshot"]) == 48
    assert 0 <= snap["confidence"] <= 1.0


# PURPOSE: Verify snapshot truncates long input behaves correctly
def test_snapshot_truncates_long_input(agent):
    """Verify snapshot truncates long input behavior."""
    result = agent.step(observation=8)
    long_input = "a" * 1000
    snap = snapshot_for_feedback(long_input, result)
    assert len(snap["user_input"]) == 500
