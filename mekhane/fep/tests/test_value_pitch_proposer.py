#!/usr/bin/env python3
# PROOF: [L3/テスト] <- mekhane/fep/tests/
"""
PROOF: [L3/テスト] このファイルは存在しなければならない

A0 → Value Pitch 自動提案の正しさを検証
   → 角度分類、骨格生成、入力パーサー
   → test_value_pitch_proposer.py が担う

Q.E.D.
"""

import pytest

from mekhane.symploke.value_pitch_proposer import (
    BENEFIT_ANGLES,
    AngleScore,
    CompletedTask,
    PitchProposal,
    _classify_angle,
    _generate_skeleton,
    _generate_title,
    format_proposals,
    propose_pitches,
    tasks_from_dispatch_log,
    tasks_from_git_stat,
)


# =============================================================================
# Angle Classification
# =============================================================================


# PURPOSE: Test suite validating angle classification correctness
class TestAngleClassification:
    """Benefit Angle 分類テスト。"""

    # PURPOSE: Verify test task maps to sodatsu behaves correctly
    def test_test_task_maps_to_sodatsu(self):
        """テスト追加タスク → 育つ。"""
        task = CompletedTask(
            title="テスト追加 — 検証を自動化",
            tests_added=10,
            tests_passed=10,
        )
        scores = _classify_angle(task)
        assert len(scores) > 0
        assert scores[0].label == "育つ"

    # PURPOSE: Verify new feature maps to dekiru behaves correctly
    def test_new_feature_maps_to_dekiru(self):
        """新機能実装タスク → できる。"""
        task = CompletedTask(
            title="新規パイプライン実装 — 機能を追加して接続",
        )
        scores = _classify_angle(task)
        primary = scores[0]
        assert primary.label == "できる"

    # PURPOSE: Verify cleanup maps to karui behaves correctly
    def test_cleanup_maps_to_karui(self):
        """整理・削減タスク → 軽い。"""
        task = CompletedTask(
            title="マクロ整理 — 不要なものを削減して統合",
        )
        scores = _classify_angle(task)
        primary = scores[0]
        assert primary.label == "軽い"

    # PURPOSE: Verify bugfix maps to mamoru behaves correctly
    def test_bugfix_maps_to_mamoru(self):
        """バグ修正タスク → 守る。"""
        task = CompletedTask(
            title="バグ修正: 二重登録防止 guard を追加",
        )
        scores = _classify_angle(task)
        primary = scores[0]
        assert primary.label == "守る"

    # PURPOSE: Verify fep theory maps to fukai behaves correctly
    def test_fep_theory_maps_to_fukai(self):
        """理論的作業 → 深い。"""
        task = CompletedTask(
            title="FEP 公理から定理を演繹。圏論の随伴関手で接続",
        )
        scores = _classify_angle(task)
        primary = scores[0]
        assert primary.label == "深い"

    # PURPOSE: Verify dashboard maps to wakaru behaves correctly
    def test_dashboard_maps_to_wakaru(self):
        """可視化タスク → わかる。"""
        task = CompletedTask(
            title="ダッシュボード可視化 — 因果分析を表示",
        )
        scores = _classify_angle(task)
        primary = scores[0]
        assert primary.label == "わかる"

    # PURPOSE: Verify calibration maps to tashika behaves correctly
    def test_calibration_maps_to_tashika(self):
        """計測タスク → 確か。"""
        task = CompletedTask(
            title="閾値calibrate — パラメータの根拠を数値で測定",
        )
        scores = _classify_angle(task)
        primary = scores[0]
        assert primary.label == "確か"

    # PURPOSE: Verify no match returns empty behaves correctly
    def test_no_match_returns_empty(self):
        """キーワードなしタスク → 空スコアリスト。"""
        task = CompletedTask(title="zzz xyz abc")
        scores = _classify_angle(task)
        assert len(scores) == 0

    # PURPOSE: Verify multiple angles sorted by score behaves correctly
    def test_multiple_angles_sorted_by_score(self):
        """複数角度マッチ → スコア降順。"""
        task = CompletedTask(
            title="新規テスト自動化パイプラインを実装して検証",
        )
        scores = _classify_angle(task)
        assert len(scores) >= 2
        assert scores[0].score >= scores[1].score


# =============================================================================
# Title Generation
# =============================================================================


# PURPOSE: Test suite validating title generation correctness
class TestTitleGeneration:
    """タイトル生成テスト。"""

    # PURPOSE: Verify basic title behaves correctly
    def test_basic_title(self):
        """Verify basic title behavior."""
        task = CompletedTask(title="Doxa 昇格")
        angle = AngleScore(
            angle_key="dekiru", label="できる", axiom="Flow", score=0.5
        )
        title = _generate_title(task, angle)
        assert "Doxa 昇格" in title
        assert "できる" in title

    # PURPOSE: Verify long title truncated behaves correctly
    def test_long_title_truncated(self):
        """Verify long title truncated behavior."""
        task = CompletedTask(title="非常に長いタスク名" * 5)
        angle = AngleScore(
            angle_key="wakaru", label="わかる", axiom="FEP", score=0.3
        )
        title = _generate_title(task, angle)
        assert "…" in title


# =============================================================================
# Skeleton Generation
# =============================================================================


# PURPOSE: Test suite validating skeleton generation correctness
class TestSkeletonGeneration:
    """骨格ドラフト生成テスト。"""

    # PURPOSE: Verify skeleton contains angle info behaves correctly
    def test_skeleton_contains_angle_info(self):
        """Verify skeleton contains angle info behavior."""
        task = CompletedTask(title="テスト追加", tests_added=5, tests_passed=5)
        angle = AngleScore(
            angle_key="sodatsu", label="育つ", axiom="Function", score=0.5
        )
        skeleton = _generate_skeleton(task, angle)
        assert "育つ" in skeleton
        assert "Function" in skeleton
        assert "Before" in skeleton
        assert "After" in skeleton

    # PURPOSE: Verify skeleton includes test stats behaves correctly
    def test_skeleton_includes_test_stats(self):
        """Verify skeleton includes test stats behavior."""
        task = CompletedTask(title="test", tests_added=10, tests_passed=10)
        angle = AngleScore(
            angle_key="sodatsu", label="育つ", axiom="Function", score=0.5
        )
        skeleton = _generate_skeleton(task, angle)
        assert "10 追加" in skeleton
        assert "10 passed" in skeleton

    # PURPOSE: Verify skeleton includes files behaves correctly
    def test_skeleton_includes_files(self):
        """Verify skeleton includes files behavior."""
        task = CompletedTask(
            title="test",
            files_changed=["doxa_promoter.py", "doxa_persistence.py"],
        )
        angle = AngleScore(
            angle_key="dekiru", label="できる", axiom="Flow", score=0.5
        )
        skeleton = _generate_skeleton(task, angle)
        assert "doxa_promoter.py" in skeleton


# =============================================================================
# Propose Pitches (Integration)
# =============================================================================


# PURPOSE: Test suite validating propose pitches correctness
class TestProposePitches:
    """統合テスト。"""

    # PURPOSE: Verify propose returns sorted behaves correctly
    def test_propose_returns_sorted(self):
        """Verify propose returns sorted behavior."""
        tasks = [
            CompletedTask(title="zzz abc"),
            CompletedTask(
                title="新規パイプライン実装 — 機能を追加",
            ),
        ]
        proposals = propose_pitches(tasks)
        assert len(proposals) == 2
        # 高スコアが先
        assert proposals[0].primary_angle.score >= proposals[1].primary_angle.score

    # PURPOSE: Verify no match gets default behaves correctly
    def test_no_match_gets_default(self):
        """Verify no match gets default behavior."""
        tasks = [CompletedTask(title="zzz xyz abc")]
        proposals = propose_pitches(tasks)
        assert len(proposals) == 1
        assert proposals[0].primary_angle.label == "わかる"

    # PURPOSE: Verify empty tasks behaves correctly
    def test_empty_tasks(self):
        """Verify empty tasks behavior."""
        assert propose_pitches([]) == []


# =============================================================================
# Format Proposals
# =============================================================================


# PURPOSE: Test suite validating format proposals correctness
class TestFormatProposals:
    """提案フォーマットテスト。"""

    # PURPOSE: Verify empty proposals behaves correctly
    def test_empty_proposals(self):
        """Verify empty proposals behavior."""
        result = format_proposals([])
        assert "完了タスクがありません" in result

    # PURPOSE: Verify format contains title behaves correctly
    def test_format_contains_title(self):
        """Verify format contains title behavior."""
        proposals = propose_pitches(
            [CompletedTask(title="新規テスト実装で検証自動化")]
        )
        result = format_proposals(proposals)
        assert "Value Pitch 自動提案" in result
        assert "提案 1" in result


# =============================================================================
# Input Parsers
# =============================================================================


# PURPOSE: Test suite validating dispatch log parser correctness
class TestDispatchLogParser:
    """Dispatch Log パーサーテスト。"""

    # PURPOSE: Verify parse workflow executions behaves correctly
    def test_parse_workflow_executions(self):
        """Verify parse workflow executions behavior."""
        log = {
            "workflow_executions": [
                {
                    "workflow": "/dia",
                    "mode": "audit",
                    "outcome": "success",
                    "notes": "MECE分析実行",
                },
                {
                    "workflow": "/bye",
                    "outcome": "in_progress",
                    "notes": "未完了",
                },
            ]
        }
        tasks = tasks_from_dispatch_log(log)
        assert len(tasks) == 1  # success のみ
        assert "/dia" in tasks[0].title

    # PURPOSE: Verify parse skill activations behaves correctly
    def test_parse_skill_activations(self):
        """Verify parse skill activations behavior."""
        log = {
            "skill_activations": [
                {
                    "skill": "K4 Sophia",
                    "outcome": "success",
                    "notes": "Web検索で根本原因を特定",
                }
            ]
        }
        tasks = tasks_from_dispatch_log(log)
        assert len(tasks) == 1
        assert "K4 Sophia" in tasks[0].title

    # PURPOSE: Verify parse exception patterns behaves correctly
    def test_parse_exception_patterns(self):
        """Verify parse exception patterns behavior."""
        log = {
            "exception_patterns": [
                {
                    "situation": "export_chats.py にバグ",
                    "action_taken": "修正した",
                    "learned": "CLIの引数は実行前にhelpで確認すべき",
                }
            ]
        }
        tasks = tasks_from_dispatch_log(log)
        assert len(tasks) == 1
        assert "学び" in tasks[0].title

    # PURPOSE: Verify empty log behaves correctly
    def test_empty_log(self):
        """Verify empty log behavior."""
        assert tasks_from_dispatch_log({}) == []


# PURPOSE: Test suite validating git stat parser correctness
class TestGitStatParser:
    """Git stat パーサーテスト。"""

    # PURPOSE: Verify basic parse behaves correctly
    def test_basic_parse(self):
        """Verify basic parse behavior."""
        tasks = tasks_from_git_stat(
            commit_messages=["feat: Doxa昇格パイプライン"],
            files_changed=["doxa_promoter.py"],
            tests_added=19,
            tests_passed=38,
        )
        assert len(tasks) == 1
        assert tasks[0].tests_added == 19
        assert "doxa_promoter.py" in tasks[0].files_changed
