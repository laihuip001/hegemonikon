# PROOF: [L1/テスト] <- mekhane/symploke/tests/ O4→F15/F16テスト
"""F15: perspective_evolver / F16: adaptive_rotation のテスト。"""
from __future__ import annotations

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
import sys

# mekhane/symploke を sys.path に追加
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


# PURPOSE: F16: adaptive_rotation のテスト。
class TestAdaptiveRotation:
    """F16: adaptive_rotation のテスト。"""

    # PURPOSE: データ不足時はフォールバック (静的ローテーション)。
    def test_static_fallback_no_data(self):
        """データ不足時はフォールバック (静的ローテーション)。"""
        from adaptive_rotation import recommend_mode

        with tempfile.TemporaryDirectory() as tmpdir:
            result = recommend_mode(1, log_dir=Path(tmpdir))
            assert result == "basanos"  # Mon

            result = recommend_mode(6, log_dir=Path(tmpdir))
            assert result == "specialist"  # Sat

    # PURPOSE: 5件未満のデータではフォールバック。
    def test_static_fallback_too_few_data(self):
        """5件未満のデータではフォールバック。"""
        from adaptive_rotation import recommend_mode

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            # 3件のログを作成 (5件未満)
            for i in range(3):
                date = datetime.now() - timedelta(days=i)
                fname = f"scheduler_{date.strftime('%Y%m%d')}_0600.json"
                (log_dir / fname).write_text(json.dumps({
                    "mode": "basanos",
                    "total_started": 10,
                    "total_failed": 1,
                }))

            result = recommend_mode(1, log_dir=log_dir)
            assert result == "basanos"  # フォールバック

    # PURPOSE: 十分なデータで最高スコアのモードを選択。
    def test_adaptive_selection(self):
        """十分なデータで最高スコアのモードを選択。"""
        from adaptive_rotation import recommend_mode

        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir)
            # basanos: 高成功率
            for i in range(5):
                date = datetime.now() - timedelta(days=i)
                fname = f"scheduler_{date.strftime('%Y%m%d')}_0600.json"
                (log_dir / fname).write_text(json.dumps({
                    "mode": "basanos",
                    "total_started": 20,
                    "total_failed": 1,
                }))
            # specialist: 低成功率
            for i in range(5):
                date = datetime.now() - timedelta(days=i)
                fname = f"scheduler_{date.strftime('%Y%m%d')}_1200.json"
                (log_dir / fname).write_text(json.dumps({
                    "mode": "specialist",
                    "total_started": 5,
                    "total_failed": 10,
                }))
            # hybrid: 中成功率 (全 VALID_MODES をカバーして untried 探索を回避)
            for i in range(5):
                date = datetime.now() - timedelta(days=i)
                fname = f"scheduler_{date.strftime('%Y%m%d')}_1800.json"
                (log_dir / fname).write_text(json.dumps({
                    "mode": "hybrid",
                    "total_started": 10,
                    "total_failed": 3,
                }))

            # 平日: basanos が最高スコア (95%) > hybrid (70%) > specialist (負値)
            # random を固定: 常に exploit パス (ε=0.1 の探索パスを排除)
            with patch("random.random", return_value=1.0), \
                 patch("random.choice", return_value="basanos"):
                result = recommend_mode(1, log_dir=log_dir)
            assert result == "basanos"

    # PURPOSE: ローテーションレポートの構造を検証。
    def test_rotation_report(self):
        """ローテーションレポートの構造を検証。"""
        from adaptive_rotation import get_rotation_report

        with tempfile.TemporaryDirectory() as tmpdir:
            report = get_rotation_report(log_dir=Path(tmpdir))
            assert "mode_scores" in report
            assert "rotation" in report
            assert "Mon" in report["rotation"]
            assert report["rotation"]["Mon"]["static"] == "basanos"

    # PURPOSE: 加重平均の計算を検証。
    def test_weighted_avg(self):
        """加重平均の計算を検証。"""
        from adaptive_rotation import _weighted_avg

        assert _weighted_avg([]) == 0.0
        assert _weighted_avg([1.0]) == 1.0
        # 最新のデータほど重い
        result = _weighted_avg([0.5, 1.0])
        assert result > 0.75  # 最新の 1.0 が重い


# PURPOSE: F15: perspective_evolver のテスト。
class TestPerspectiveEvolver:
    """F15: perspective_evolver のテスト。"""

    # PURPOSE: 空の FeedbackStore では提案なし。
    def test_propose_empty_store(self):
        """空の FeedbackStore では提案なし。"""
        from perspective_evolver import propose_new_perspectives
        from basanos_feedback import FeedbackStore

        with tempfile.TemporaryDirectory() as tmpdir:
            store = FeedbackStore(state_file=Path(tmpdir) / "fb.json")
            proposals = propose_new_perspectives(store)
            assert proposals == []

    # PURPOSE: evolve の dry_run モードが正常動作。
    def test_evolve_dry_run(self):
        """evolve の dry_run モードが正常動作。"""
        from perspective_evolver import evolve
        from basanos_feedback import FeedbackStore

        with tempfile.TemporaryDirectory() as tmpdir:
            store = FeedbackStore(state_file=Path(tmpdir) / "fb.json")
            result = evolve(store, dry_run=True)
            assert result["dry_run"] is True
            assert result["applied"] == 0
            assert "proposals" in result


# PURPOSE: F14: basanos_feedback の get_exclusion_report テスト。
class TestExclusionReport:
    """F14: basanos_feedback の get_exclusion_report テスト。"""

    # PURPOSE: 空データで淘汰レポート。
    def test_exclusion_report_empty(self):
        """空データで淘汰レポート。"""
        from basanos_feedback import FeedbackStore

        with tempfile.TemporaryDirectory() as tmpdir:
            store = FeedbackStore(state_file=Path(tmpdir) / "fb.json")
            report = store.get_exclusion_report()
            assert report["excluded_count"] == 0
            assert report["total_perspectives"] == 0
            assert report["exclusion_rate"] == 0.0
