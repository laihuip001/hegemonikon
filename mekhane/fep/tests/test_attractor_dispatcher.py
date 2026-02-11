# PROOF: [L2/テスト] <- mekhane/fep/tests/
"""Tests for AttractorDispatcher — Problem A verification"""

import pytest
from pathlib import Path

from mekhane.fep.attractor import OscillationType
from mekhane.fep.attractor_dispatcher import (
    AttractorDispatcher,
    DispatchPlan,
    DispatchResult,
    _extract_field,
    _extract_multiline_field,
)


# PURPOSE: dispatcher の処理
@pytest.fixture(scope="module")
def dispatcher():
    """Verify dispatcher behavior."""
    return AttractorDispatcher()


# ---------------------------------------------------------------------------
# Frontmatter parser tests (unit, no embedding)
# ---------------------------------------------------------------------------

# PURPOSE: 軽量 frontmatter パーサのテスト
class TestFrontmatterParser:
    """軽量 frontmatter パーサのテスト"""

    # PURPOSE: extract_field_quoted をテストする
    def test_extract_field_quoted(self):
        """Verify extract field quoted behavior."""
        content = '---\nversion: "4.6"\nskill_ref: ".agent/skills/ousia/o1-noesis/SKILL.md"\n---\n'
        assert _extract_field(content, "skill_ref") == ".agent/skills/ousia/o1-noesis/SKILL.md"

    # PURPOSE: extract_field_unquoted をテストする
    def test_extract_field_unquoted(self):
        """Verify extract field unquoted behavior."""
        content = '---\nlcm_state: beta\n---\n'
        assert _extract_field(content, "lcm_state") == "beta"

    # PURPOSE: extract_field_missing をテストする
    def test_extract_field_missing(self):
        """Verify extract field missing behavior."""
        content = '---\nversion: "1.0"\n---\n'
        assert _extract_field(content, "skill_ref") == ""

    # PURPOSE: extract_field_no_frontmatter をテストする
    def test_extract_field_no_frontmatter(self):
        """Verify extract field no frontmatter behavior."""
        content = "# Just a heading\nSome text"
        assert _extract_field(content, "anything") == ""

    # PURPOSE: extract_multiline_inline をテストする
    def test_extract_multiline_inline(self):
        """Verify extract multiline inline behavior."""
        content = '---\ndescription: "Short description"\n---\n'
        assert _extract_multiline_field(content, "description") == "Short description"


# ---------------------------------------------------------------------------
# Integration tests (require embedding model)
# ---------------------------------------------------------------------------

# PURPOSE: AttractorDispatcher 統合テスト
class TestDispatchIntegration:
    """AttractorDispatcher 統合テスト"""

    # PURPOSE: 明確な O-series 入力 → /noe or /bou 系の WF が primary
    def test_dispatch_clear_ousia(self, dispatcher: AttractorDispatcher):
        """明確な O-series 入力 → /noe or /bou 系の WF が primary"""
        plan = dispatcher.dispatch(
            "Why does this project exist? What is its fundamental purpose?"
        )
        assert plan is not None
        assert isinstance(plan, DispatchPlan)
        assert plan.primary.series == "O"
        assert plan.primary.workflow.startswith("/")

    # PURPOSE: 明確な S-series 入力 → 設計系 WF
    def test_dispatch_clear_schema(self, dispatcher: AttractorDispatcher):
        """明確な S-series 入力 → 設計系 WF"""
        plan = dispatcher.dispatch(
            "How should we design the architecture and implementation plan?"
        )
        assert plan is not None
        assert plan.primary.series == "S"

    # PURPOSE: WF パスが実在する
    def test_dispatch_returns_valid_paths(self, dispatcher: AttractorDispatcher):
        """WF パスが実在する"""
        plan = dispatcher.dispatch("Why does this exist?")
        assert plan is not None
        assert plan.primary.wf_path.exists()

    # PURPOSE: skill_path がある場合、実在する
    def test_dispatch_skill_path_exists(self, dispatcher: AttractorDispatcher):
        """skill_path がある場合、実在する"""
        plan = dispatcher.dispatch("Why does this exist?")
        assert plan is not None
        if plan.primary.skill_path:
            assert plan.primary.skill_path.exists()

    # PURPOSE: 推薦理由が生成される
    def test_dispatch_has_reason(self, dispatcher: AttractorDispatcher):
        """推薦理由が生成される"""
        plan = dispatcher.dispatch("Why does this project exist?")
        assert plan is not None
        assert len(plan.primary.reason) > 0

    # PURPOSE: WF description が取得される
    def test_dispatch_has_description(self, dispatcher: AttractorDispatcher):
        """WF description が取得される"""
        plan = dispatcher.dispatch("Why does this exist?")
        assert plan is not None
        assert len(plan.primary.description) > 0

    # PURPOSE: confidence が 0 より大きい
    def test_dispatch_confidence(self, dispatcher: AttractorDispatcher):
        """confidence が 0 より大きい"""
        plan = dispatcher.dispatch("Design the architecture")
        assert plan is not None
        assert plan.primary.confidence > 0.0

    # PURPOSE: oscillation が正しく伝播する
    def test_dispatch_oscillation_propagated(self, dispatcher: AttractorDispatcher):
        """oscillation が正しく伝播する"""
        plan = dispatcher.dispatch("Define the boundaries and scope of this domain")
        assert plan is not None
        assert isinstance(plan.oscillation, OscillationType)

    # PURPOSE: all_dispatches は primary + alternatives
    def test_dispatch_all_dispatches(self, dispatcher: AttractorDispatcher):
        """all_dispatches は primary + alternatives"""
        plan = dispatcher.dispatch("Why?")
        assert plan is not None
        assert len(plan.all_dispatches) >= 1
        assert plan.all_dispatches[0] == plan.primary


# ---------------------------------------------------------------------------
# Format tests
# ---------------------------------------------------------------------------

# PURPOSE: 出力フォーマットのテスト
class TestFormatting:
    """出力フォーマットのテスト"""

    # PURPOSE: format_dispatch に WF 名が含まれる
    def test_format_dispatch_contains_workflow(self, dispatcher: AttractorDispatcher):
        """format_dispatch に WF 名が含まれる"""
        plan = dispatcher.dispatch("Why does this exist?")
        assert plan is not None
        formatted = dispatcher.format_dispatch(plan)
        assert plan.primary.workflow in formatted
        assert "Attractor Dispatch" in formatted

    # PURPOSE: format_compact が compact 文字列を返す
    def test_format_compact(self, dispatcher: AttractorDispatcher):
        """format_compact が compact 文字列を返す"""
        plan = dispatcher.dispatch("Design the architecture")
        assert plan is not None
        compact = dispatcher.format_compact(plan)
        assert "→" in compact

    # PURPOSE: DispatchResult の repr
    def test_dispatch_result_repr(self, dispatcher: AttractorDispatcher):
        """DispatchResult の repr"""
        plan = dispatcher.dispatch("Why?")
        assert plan is not None
        repr_str = repr(plan.primary)
        assert "Dispatch:" in repr_str

    # PURPOSE: DispatchPlan の repr
    def test_dispatch_plan_repr(self, dispatcher: AttractorDispatcher):
        """DispatchPlan の repr"""
        plan = dispatcher.dispatch("Why?")
        assert plan is not None
        repr_str = repr(plan)
        assert "DispatchPlan:" in repr_str


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

# PURPOSE: エッジケースのテスト
class TestEdgeCases:
    """エッジケースのテスト"""

    # PURPOSE: 空文字でもクラッシュしない
    def test_dispatch_empty_input(self, dispatcher: AttractorDispatcher):
        """空文字でもクラッシュしない"""
        plan = dispatcher.dispatch("")
        # plan は None かもしれないが、例外は投げない

    # PURPOSE: 長い入力でもクラッシュしない
    def test_dispatch_very_long_input(self, dispatcher: AttractorDispatcher):
        """長い入力でもクラッシュしない"""
        plan = dispatcher.dispatch("Why? " * 100)
        # plan が返る (None でもOK)
