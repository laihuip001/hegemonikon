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


class TestAngleClassification:
    """Benefit Angle 分類テスト。"""

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

    def test_new_feature_maps_to_dekiru(self):
        """新機能実装タスク → できる。"""
        task = CompletedTask(
            title="新規パイプライン実装 — 機能を追加して接続",
        )
        scores = _classify_angle(task)
        primary = scores[0]
        assert primary.label == "できる"

    def test_cleanup_maps_to_karui(self):
        """整理・削減タスク → 軽い。"""
        task = CompletedTask(
            title="マクロ整理 — 不要なものを削減して統合",
        )
        scores = _classify_angle(task)
        primary = scores[0]
        assert primary.label == "軽い"

    def test_bugfix_maps_to_mamoru(self):
        """バグ修正タスク → 守る。"""
        task = CompletedTask(
            title="バグ修正: 二重登録防止 guard を追加",
        )
        scores = _classify_angle(task)
        primary = scores[0]
        assert primary.label == "守る"

    def test_fep_theory_maps_to_fukai(self):
        """理論的作業 → 深い。"""
        task = CompletedTask(
            title="FEP 公理から定理を演繹。圏論の随伴関手で接続",
        )
        scores = _classify_angle(task)
        primary = scores[0]
        assert primary.label == "深い"

    def test_dashboard_maps_to_wakaru(self):
        """可視化タスク → わかる。"""
        task = CompletedTask(
            title="ダッシュボード可視化 — 因果分析を表示",
        )
        scores = _classify_angle(task)
        primary = scores[0]
        assert primary.label == "わかる"

    def test_calibration_maps_to_tashika(self):
        """計測タスク → 確か。"""
        task = CompletedTask(
            title="閾値calibrate — パラメータの根拠を数値で測定",
        )
        scores = _classify_angle(task)
        primary = scores[0]
        assert primary.label == "確か"

    def test_no_match_returns_empty(self):
        """キーワードなしタスク → 空スコアリスト。"""
        task = CompletedTask(title="zzz xyz abc")
        scores = _classify_angle(task)
        assert len(scores) == 0

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


class TestTitleGeneration:
    """タイトル生成テスト。"""

    def test_basic_title(self):
        task = CompletedTask(title="Doxa 昇格")
        angle = AngleScore(
            angle_key="dekiru", label="できる", axiom="Flow", score=0.5
        )
        title = _generate_title(task, angle)
        assert "Doxa 昇格" in title
        assert "できる" in title

    def test_long_title_truncated(self):
        task = CompletedTask(title="非常に長いタスク名" * 5)
        angle = AngleScore(
            angle_key="wakaru", label="わかる", axiom="FEP", score=0.3
        )
        title = _generate_title(task, angle)
        assert "…" in title


# =============================================================================
# Skeleton Generation
# =============================================================================


class TestSkeletonGeneration:
    """骨格ドラフト生成テスト。"""

    def test_skeleton_contains_angle_info(self):
        task = CompletedTask(title="テスト追加", tests_added=5, tests_passed=5)
        angle = AngleScore(
            angle_key="sodatsu", label="育つ", axiom="Function", score=0.5
        )
        skeleton = _generate_skeleton(task, angle)
        assert "育つ" in skeleton
        assert "Function" in skeleton
        assert "Before" in skeleton
        assert "After" in skeleton

    def test_skeleton_includes_test_stats(self):
        task = CompletedTask(title="test", tests_added=10, tests_passed=10)
        angle = AngleScore(
            angle_key="sodatsu", label="育つ", axiom="Function", score=0.5
        )
        skeleton = _generate_skeleton(task, angle)
        assert "10 追加" in skeleton
        assert "10 passed" in skeleton

    def test_skeleton_includes_files(self):
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


class TestProposePitches:
    """統合テスト。"""

    def test_propose_returns_sorted(self):
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

    def test_no_match_gets_default(self):
        tasks = [CompletedTask(title="zzz xyz abc")]
        proposals = propose_pitches(tasks)
        assert len(proposals) == 1
        assert proposals[0].primary_angle.label == "わかる"

    def test_empty_tasks(self):
        assert propose_pitches([]) == []


# =============================================================================
# Format Proposals
# =============================================================================


class TestFormatProposals:
    """提案フォーマットテスト。"""

    def test_empty_proposals(self):
        result = format_proposals([])
        assert "完了タスクがありません" in result

    def test_format_contains_title(self):
        proposals = propose_pitches(
            [CompletedTask(title="新規テスト実装で検証自動化")]
        )
        result = format_proposals(proposals)
        assert "Value Pitch 自動提案" in result
        assert "提案 1" in result


# =============================================================================
# Input Parsers
# =============================================================================


class TestDispatchLogParser:
    """Dispatch Log パーサーテスト。"""

    def test_parse_workflow_executions(self):
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

    def test_parse_skill_activations(self):
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

    def test_parse_exception_patterns(self):
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

    def test_empty_log(self):
        assert tasks_from_dispatch_log({}) == []


class TestGitStatParser:
    """Git stat パーサーテスト。"""

    def test_basic_parse(self):
        tasks = tasks_from_git_stat(
            commit_messages=["feat: Doxa昇格パイプライン"],
            files_changed=["doxa_promoter.py"],
            tests_added=19,
            tests_passed=38,
        )
        assert len(tasks) == 1
        assert tasks[0].tests_added == 19
        assert "doxa_promoter.py" in tasks[0].files_changed
