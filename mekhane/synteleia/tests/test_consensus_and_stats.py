# PROOF: [L3/テスト] <- mekhane/synteleia/tests/ ConsensusAgent テスト
"""
ConsensusAgent テストスイート

F7: L3 マルチモデルコンセンサス監査のユニットテスト
"""

import json
from unittest.mock import MagicMock

import pytest

from mekhane.synteleia.dokimasia.consensus_agent import ConsensusAgent
from mekhane.synteleia.base import AuditTarget, AuditTargetType


class TestConsensusAgent:
    """ConsensusAgent のユニットテスト。"""

    def test_no_backends(self):
        """バックエンドなしの場合、passed=True, confidence=0.0。"""
        agent = ConsensusAgent(backends=[])
        target = AuditTarget(
            content="test code",
            target_type=AuditTargetType.CODE,
        )
        result = agent.audit(target)
        assert result.passed is True
        assert result.confidence == 0.0
        assert result.metadata["reason"] == "No backends available"

    def test_no_available_backends(self):
        """バックエンドが接続不可の場合。"""
        backend = MagicMock()
        backend.is_available.return_value = False
        agent = ConsensusAgent(backends=[backend])
        target = AuditTarget(content="test", target_type=AuditTargetType.CODE)
        result = agent.audit(target)
        assert result.passed is True
        assert result.confidence == 0.0
        assert result.metadata["reason"] == "No backends reachable"

    def test_consensus_all_agree(self):
        """全モデルが同じ issue を検出 → 高確信度。"""
        issue_json = json.dumps({
            "issues": [{"code": "SEC-001", "message": "eval detected", "severity": "critical"}],
            "summary": "security issue",
            "confidence": 0.9,
        })
        backends = []
        for _ in range(3):
            b = MagicMock()
            b.is_available.return_value = True
            b.query.return_value = issue_json
            backends.append(b)

        agent = ConsensusAgent(backends=backends)
        target = AuditTarget(content="eval(x)", target_type=AuditTargetType.CODE)
        result = agent.audit(target)

        assert result.passed is False  # CRITICAL detected
        assert result.confidence == 1.0  # 3/3 agree
        assert len(result.issues) == 1
        assert result.issues[0].code == "SEC-001"

    def test_consensus_no_issues(self):
        """全モデルが問題なしと判断。"""
        no_issue_json = json.dumps({
            "issues": [],
            "summary": "clean code",
            "confidence": 1.0,
        })
        backends = []
        for _ in range(3):
            b = MagicMock()
            b.is_available.return_value = True
            b.query.return_value = no_issue_json
            backends.append(b)

        agent = ConsensusAgent(backends=backends)
        target = AuditTarget(content="print('hello')", target_type=AuditTargetType.CODE)
        result = agent.audit(target)

        assert result.passed is True
        assert result.confidence == 1.0
        assert len(result.issues) == 0

    def test_consensus_partial_agreement(self):
        """2/3 のモデルが検出 → 過半数で採用。"""
        issue_json = json.dumps({
            "issues": [{"code": "LOG-001", "message": "logging issue", "severity": "medium"}],
            "summary": "minor",
            "confidence": 0.7,
        })
        clean_json = json.dumps({
            "issues": [],
            "summary": "clean",
            "confidence": 1.0,
        })

        b1 = MagicMock()
        b1.is_available.return_value = True
        b1.query.return_value = issue_json

        b2 = MagicMock()
        b2.is_available.return_value = True
        b2.query.return_value = issue_json

        b3 = MagicMock()
        b3.is_available.return_value = True
        b3.query.return_value = clean_json

        agent = ConsensusAgent(backends=[b1, b2, b3])
        target = AuditTarget(content="log(x)", target_type=AuditTargetType.CODE)
        result = agent.audit(target)

        assert result.passed is True  # MEDIUM doesn't cause failure
        assert len(result.issues) == 1
        assert result.issues[0].code == "LOG-001"

    def test_backend_failure_graceful(self):
        """1つのバックエンドがエラーの場合も残りで処理。"""
        issue_json = json.dumps({
            "issues": [{"code": "T-001", "message": "test", "severity": "low"}],
            "summary": "test",
            "confidence": 0.8,
        })
        b1 = MagicMock()
        b1.is_available.return_value = True
        b1.query.return_value = issue_json

        b2 = MagicMock()
        b2.is_available.return_value = True
        b2.query.side_effect = RuntimeError("API error")

        agent = ConsensusAgent(backends=[b1, b2])
        target = AuditTarget(content="test", target_type=AuditTargetType.CODE)
        result = agent.audit(target)

        # 1 backend succeeded
        assert result.passed is True
        assert result.metadata["n_backends"] == 1


class TestOrchestratorWithL3:
    """Orchestrator.with_l3 のテスト。"""

    def test_with_l3_creates_orchestrator(self):
        """with_l3 が ConsensusAgent を含むオーケストレータを生成。"""
        from mekhane.synteleia.orchestrator import SynteleiaOrchestrator
        orch = SynteleiaOrchestrator.with_l3()
        agent_names = [a.name for a in orch.dokimasia_agents]
        assert "ConsensusAgent" in agent_names


class TestPatternStats:
    """F5: パターン統計テスト。"""

    def test_record_and_get(self):
        """record_hit でヒット数が増加し、get_stats で取得可能。"""
        from mekhane.synteleia.pattern_loader import (
            record_hit, get_stats, reset_stats,
        )
        reset_stats()
        record_hit("O-001")
        record_hit("O-001")
        record_hit("S-001")

        stats = get_stats()
        assert stats["O-001"] == 2
        assert stats["S-001"] == 1
        # ソート順: ヒット数降順
        keys = list(stats.keys())
        assert keys[0] == "O-001"

        reset_stats()
        assert get_stats() == {}


class TestMergedPatterns:
    """F4: 3層マージのテスト。"""

    def test_no_custom_dir(self, tmp_path):
        """カスタムディレクトリが存在しない場合、プロジェクト YAML のみ使用。"""
        from mekhane.synteleia.pattern_loader import load_merged_patterns, _cache
        _cache.clear()

        # YAML を tmp に作成
        import yaml
        yaml_path = tmp_path / "patterns.yaml"
        yaml_path.write_text(yaml.dump({
            "ousia": {"vague_patterns": [["V-001", "test"]]}
        }))

        result = load_merged_patterns(
            yaml_path, "ousia",
            custom_dir=tmp_path / "nonexistent",
        )
        assert "vague_patterns" in result
        _cache.clear()

    def test_custom_overrides(self, tmp_path):
        """カスタムパターンがプロジェクトパターンを上書き。"""
        from mekhane.synteleia.pattern_loader import load_merged_patterns, _cache
        _cache.clear()

        import yaml

        # プロジェクト YAML
        project_dir = tmp_path / "project"
        project_dir.mkdir()
        project_yaml = project_dir / "patterns.yaml"
        project_yaml.write_text(yaml.dump({
            "ousia": {"key_a": "project", "key_b": "project"}
        }))

        # カスタム YAML
        custom_dir = tmp_path / "custom"
        custom_dir.mkdir()
        custom_yaml = custom_dir / "patterns.yaml"
        custom_yaml.write_text(yaml.dump({
            "ousia": {"key_a": "custom"}
        }))

        result = load_merged_patterns(project_yaml, "ousia", custom_dir=custom_dir)
        assert result["key_a"] == "custom"  # カスタムが優先
        assert result["key_b"] == "project"  # プロジェクトのみのキーは残る
        _cache.clear()
