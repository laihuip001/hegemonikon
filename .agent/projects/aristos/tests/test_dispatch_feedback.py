# F5: dispatch → log_from_dispatch E2E テスト
"""
dispatch() の実結果を入力として log_from_dispatch() を呼び出し、
YAML ファイルに正しくフィードバックが保存されることを検証する。
"""
import tempfile
from pathlib import Path

import pytest
from aristos.route_feedback import (
    RouteFeedback,
    load_route_feedback,
    log_from_dispatch,
)


@pytest.fixture
def tmp_feedback_path(tmp_path):
    return tmp_path / "route_feedback.yaml"


class TestLogFromDispatchBasic:
    """log_from_dispatch の基本動作"""

    def test_single_wf_returns_none(self, tmp_feedback_path):
        """単一 WF (ルーティングなし) は None を返す"""
        result = {
            "success": True,
            "workflows": ["/noe"],
        }
        fb = log_from_dispatch(result, path=tmp_feedback_path)
        assert fb is None

    def test_failed_dispatch_returns_none(self, tmp_feedback_path):
        """dispatch 失敗時は None を返す"""
        result = {"success": False, "workflows": ["/noe", "/dia"]}
        fb = log_from_dispatch(result, path=tmp_feedback_path)
        assert fb is None

    def test_no_workflows_returns_none(self, tmp_feedback_path):
        """workflows なしは None を返す"""
        result = {"success": True}
        fb = log_from_dispatch(result, path=tmp_feedback_path)
        assert fb is None

    def test_empty_workflows_returns_none(self, tmp_feedback_path):
        """空リストは None を返す"""
        result = {"success": True, "workflows": []}
        fb = log_from_dispatch(result, path=tmp_feedback_path)
        assert fb is None


class TestLogFromDispatchMultiWF:
    """複数 WF でのフィードバック生成"""

    def test_two_wf_creates_feedback(self, tmp_feedback_path):
        """2 WF → フィードバック生成"""
        result = {
            "success": True,
            "workflows": ["/noe", "/dia"],
        }
        fb = log_from_dispatch(
            result,
            actual_time_min=5.0,
            path=tmp_feedback_path,
        )
        assert fb is not None
        assert fb.source == "noe"
        assert fb.target == "dia"
        assert fb.chosen_route == ["noe", "dia"]
        assert 0.0 <= fb.quality <= 1.0

    def test_multi_wf_creates_feedback(self, tmp_feedback_path):
        """多段 WF → source/target 正しい"""
        result = {
            "success": True,
            "workflows": ["/bou", "/s", "/ene", "/dia", "/dox"],
            "depth_level": 1,
        }
        fb = log_from_dispatch(
            result,
            actual_time_min=10.0,
            path=tmp_feedback_path,
        )
        assert fb is not None
        assert fb.source == "bou"
        assert fb.target == "dox"
        assert len(fb.chosen_route) == 5
        assert fb.depth == "L1"

    def test_manual_quality_overrides(self, tmp_feedback_path):
        """手動指定 quality が推定を上書き"""
        result = {
            "success": True,
            "workflows": ["/noe", "/dia"],
        }
        fb = log_from_dispatch(
            result,
            quality=0.95,
            path=tmp_feedback_path,
        )
        assert fb is not None
        assert fb.quality == 0.95

    def test_error_flag_reduces_quality(self, tmp_feedback_path):
        """had_errors=True → 低品質"""
        result = {
            "success": True,
            "workflows": ["/noe", "/dia"],
        }
        fb_clean = log_from_dispatch(
            result, had_errors=False, path=tmp_feedback_path,
        )
        fb_error = log_from_dispatch(
            result, had_errors=True, path=tmp_feedback_path,
        )
        assert fb_clean is not None and fb_error is not None
        assert fb_error.quality < fb_clean.quality


class TestLogFromDispatchPersistence:
    """YAML への保存検証"""

    def test_feedback_saved_to_yaml(self, tmp_feedback_path):
        """フィードバックが YAML に保存される"""
        result = {
            "success": True,
            "workflows": ["/bou", "/ene", "/dia"],
        }
        log_from_dispatch(result, actual_time_min=3.0, path=tmp_feedback_path)

        # YAML から読み込んで検証
        loaded = load_route_feedback(tmp_feedback_path)
        assert len(loaded) == 1
        assert loaded[0].source == "bou"
        assert loaded[0].target == "dia"

    def test_multiple_feedbacks_accumulate(self, tmp_feedback_path):
        """複数回ログが蓄積される"""
        for wfs in [["/noe", "/dia"], ["/bou", "/ene"], ["/s", "/pra", "/dox"]]:
            result = {"success": True, "workflows": wfs}
            log_from_dispatch(result, path=tmp_feedback_path)

        loaded = load_route_feedback(tmp_feedback_path)
        assert len(loaded) == 3

    def test_cost_scalar_computed(self, tmp_feedback_path):
        """コストスカラーが計算される"""
        result = {
            "success": True,
            "workflows": ["/noe", "/dia"],
        }
        fb = log_from_dispatch(result, path=tmp_feedback_path)
        assert fb is not None
        assert fb.cost_scalar >= 0.0

    def test_notes_preserved(self, tmp_feedback_path):
        """notes が保存される"""
        result = {
            "success": True,
            "workflows": ["/noe", "/dia"],
        }
        fb = log_from_dispatch(
            result,
            notes="テスト実行",
            path=tmp_feedback_path,
        )
        assert fb is not None
        assert fb.notes == "テスト実行"


class TestLogFromDispatchWithRealDispatch:
    """dispatch() の実結果との統合テスト"""

    def test_with_simulated_dispatch_result(self, tmp_feedback_path):
        """dispatch 相当の dict を入力"""
        # dispatch() が返す形式をシミュレート
        result = {
            "success": True,
            "tree": "...",
            "workflows": ["/bou", "/s", "/ene", "/dia", "/dox"],
            "plan_template": "...",
            "depth_level": 1,
            "route_context": {
                "source": "bou",
                "target": "dox",
                "route": ["bou", "s", "ene", "dia", "dox"],
                "depth": "L1",
                "wf_count": 5,
            },
        }
        fb = log_from_dispatch(
            result,
            actual_time_min=8.0,
            had_errors=False,
            was_corrected=False,
            notes="ccl-build 実行",
            path=tmp_feedback_path,
        )
        assert fb is not None
        assert fb.source == "bou"
        assert fb.target == "dox"
        assert fb.depth == "L1"
        assert fb.quality > 0.5  # エラーなし → 高品質
        assert fb.cost_scalar > 0.0
        assert fb.notes == "ccl-build 実行"

        # 永続化確認
        loaded = load_route_feedback(tmp_feedback_path)
        assert len(loaded) == 1
        assert loaded[0].source == "bou"
