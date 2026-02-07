# PROOF: [L2/テスト] <- mekhane/fep/tests/
"""Tests for BasinLogger (C) and decompose() (D)"""

import pytest
import json
import tempfile
from pathlib import Path

from mekhane.fep.attractor import SeriesAttractor, DecomposeResult
from mekhane.fep.basin_logger import BasinLogger, AttractorLogEntry, BasinBias


# --- C: BasinLogger tests ---

class TestBasinLogger:
    """BasinLogger のテスト"""

    def test_log_prediction(self):
        logger = BasinLogger(log_dir=Path(tempfile.mkdtemp()))
        entry = logger.log_prediction(
            user_input="Why does this exist?",
            predicted_series=["O"],
            top_similarity=0.633,
            oscillation="clear",
        )
        assert entry.user_input == "Why does this exist?"
        assert entry.predicted_series == ["O"]
        assert entry.actual_series is None

    def test_log_correction_correct(self):
        logger = BasinLogger(log_dir=Path(tempfile.mkdtemp()))
        entry = logger.log_prediction(
            user_input="Design the architecture",
            predicted_series=["S"],
            top_similarity=0.749,
            oscillation="clear",
        )
        logger.log_correction(entry, actual_series="S")
        assert entry.correction is False
        assert entry.actual_series == "S"

    def test_log_correction_wrong(self):
        logger = BasinLogger(log_dir=Path(tempfile.mkdtemp()))
        entry = logger.log_prediction(
            user_input="Some ambiguous input",
            predicted_series=["P"],
            top_similarity=0.5,
            oscillation="positive",
        )
        logger.log_correction(entry, actual_series="K")
        assert entry.correction is True

    def test_bias_report(self):
        logger = BasinLogger(log_dir=Path(tempfile.mkdtemp()))

        # 3 correct predictions for O
        for _ in range(3):
            e = logger.log_prediction("why", ["O"], 0.6, "clear")
            logger.log_correction(e, actual_series="O")

        # 2 wrong: predicted P, actual was S
        for _ in range(2):
            e = logger.log_prediction("scope", ["P"], 0.5, "positive")
            logger.log_correction(e, actual_series="S")

        report = logger.bias_report()
        assert "O" in report
        assert report["O"]["precision"] == 1.0  # 3/3 correct
        assert "P" in report
        assert report["P"]["precision"] == 0.0  # 0/2 correct

    def test_save_and_load(self):
        tmp = Path(tempfile.mkdtemp())
        logger = BasinLogger(log_dir=tmp)

        e = logger.log_prediction("test", ["O"], 0.6, "clear")
        logger.log_correction(e, actual_series="O")
        log_file = logger.save()

        assert log_file.exists()
        with open(log_file) as f:
            data = json.loads(f.readline())
        assert data["user_input"] == "test"
        assert data["actual_series"] == "O"

    def test_suggestions_for_tuning(self):
        logger = BasinLogger(log_dir=Path(tempfile.mkdtemp()))

        # P is over-predicted 6 times
        for _ in range(6):
            e = logger.log_prediction("x", ["P"], 0.5, "clear")
            logger.log_correction(e, actual_series="S")

        suggestions = logger.suggestions_for_tuning
        assert "P" in suggestions
        assert "広すぎる" in suggestions["P"]


class TestBasinBias:
    """BasinBias のプロパティテスト"""

    def test_precision(self):
        bias = BasinBias(series="O", correct_count=3, over_predict_count=1, total_count=4)
        assert bias.precision == 0.75

    def test_recall(self):
        bias = BasinBias(series="O", correct_count=3, under_predict_count=2, total_count=5)
        assert bias.recall == 0.6

    def test_bias_direction_balanced(self):
        bias = BasinBias(series="O", over_predict_count=2, under_predict_count=2, total_count=4)
        assert bias.bias_direction == "balanced"

    def test_bias_direction_too_wide(self):
        bias = BasinBias(series="P", over_predict_count=5, under_predict_count=1, total_count=6)
        assert bias.bias_direction == "too_wide"

    def test_bias_direction_too_narrow(self):
        bias = BasinBias(series="H", over_predict_count=1, under_predict_count=5, total_count=6)
        assert bias.bias_direction == "too_narrow"


# --- D: decompose() tests ---

@pytest.fixture(scope="module")
def attractor():
    return SeriesAttractor(threshold=0.10, oscillation_margin=0.05)


class TestDecompose:
    """decompose() メソッドのテスト"""

    def test_single_sentence(self, attractor: SeriesAttractor):
        """単一文 → 1セグメント"""
        result = attractor.decompose("Why does this exist?")
        assert isinstance(result, DecomposeResult)
        assert len(result.segments) == 1
        assert "O" in result.merged_series

    def test_multi_sentence(self, attractor: SeriesAttractor):
        """複数文 → 複数セグメントに分解"""
        result = attractor.decompose(
            "Why does this project exist? How should we design the architecture?"
        )
        assert len(result.segments) >= 2
        assert result.is_multi is True

    def test_multi_series_merged(self, attractor: SeriesAttractor):
        """O + S の複合入力 → merged_series に両方"""
        result = attractor.decompose(
            "What is the fundamental purpose? Design the implementation plan."
        )
        # O と S が両方含まれるはず
        assert len(result.merged_series) >= 2

    def test_merged_workflows_no_duplicates(self, attractor: SeriesAttractor):
        """マージされた workflows に重複がない"""
        result = attractor.decompose(
            "Why? How to build? Is now the right time?"
        )
        assert len(result.merged_workflows) == len(set(result.merged_workflows))

    def test_empty_input(self, attractor: SeriesAttractor):
        """空入力"""
        result = attractor.decompose("")
        assert isinstance(result, DecomposeResult)

    def test_decompose_repr(self, attractor: SeriesAttractor):
        """DecomposeResult の repr"""
        result = attractor.decompose("Why? How?")
        repr_str = repr(result)
        assert "Decompose:" in repr_str

    def test_is_multi_single(self, attractor: SeriesAttractor):
        """単一 Series → is_multi = False"""
        result = attractor.decompose("Design the architecture")
        assert result.is_multi is False
