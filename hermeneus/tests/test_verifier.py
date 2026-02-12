# PROOF: [L3/テスト] <- hermeneus/tests/ Hermēneus 検証テスト
"""
Hermēneus Verifier Unit Tests

Phase 4: Formal Verification のテスト
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# パッケージパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hermeneus.src.audit import AuditRecord, AuditStats, AuditStore, AuditReporter
from hermeneus.src.verifier import AgentRole, VerdictType, DebateArgument, Verdict, DebateRound, ConsensusResult, DebateAgent, DebateEngine


class TestAgentRole:
    """AgentRole のテスト"""
    
    # PURPOSE: 役割の列挙
    def test_roles(self):
        """役割の列挙"""
        assert AgentRole.PROPOSER.value == "proposer"
        assert AgentRole.CRITIC.value == "critic"
        assert AgentRole.ARBITER.value == "arbiter"


class TestVerdictType:
    """VerdictType のテスト"""
    
    # PURPOSE: 判定タイプ
    def test_verdict_types(self):
        """判定タイプ"""
        assert VerdictType.ACCEPT.value == "accept"
        assert VerdictType.REJECT.value == "reject"
        assert VerdictType.UNCERTAIN.value == "uncertain"


class TestDebateArgument:
    """DebateArgument のテスト"""
    
    # PURPOSE: 引数作成
    def test_create_argument(self):
        """引数作成"""
        arg = DebateArgument(
            agent_role=AgentRole.PROPOSER,
            content="この主張は妥当です。",
            confidence=0.8
        )
        assert arg.agent_role == AgentRole.PROPOSER
        assert arg.confidence == 0.8


class TestDebateAgent:
    """DebateAgent のテスト"""
    
    # PURPOSE: Proposer 作成
    def test_create_proposer(self):
        """Proposer 作成"""
        agent = DebateAgent(AgentRole.PROPOSER)
        assert agent.role == AgentRole.PROPOSER
    
    # PURPOSE: Critic 作成
    def test_create_critic(self):
        """Critic 作成"""
        agent = DebateAgent(AgentRole.CRITIC)
        assert agent.role == AgentRole.CRITIC
    
    # PURPOSE: 高確信度推定
    def test_estimate_confidence_high(self):
        """高確信度推定"""
        agent = DebateAgent(AgentRole.PROPOSER)
        text = "これは確実に正しい。明確にそうだ。definitely correct。"
        confidence = agent._estimate_confidence(text)
        assert confidence > 0.7
    
    # PURPOSE: 低確信度推定
    def test_estimate_confidence_low(self):
        """低確信度推定"""
        agent = DebateAgent(AgentRole.PROPOSER)
        text = "おそらくそうかもしれない。maybe, perhaps。"
        confidence = agent._estimate_confidence(text)
        assert confidence < 0.6
    
    # PURPOSE: 判定パース: ACCEPT
    def test_parse_verdict_accept(self):
        """判定パース: ACCEPT"""
        agent = DebateAgent(AgentRole.ARBITER)
        text = "判定: ACCEPT\n確信度: 85%\n理由: 論拠が十分。"
        verdict_type, confidence, reasoning = agent._parse_verdict(text)
        
        assert verdict_type == VerdictType.ACCEPT
        assert confidence == 0.85
        assert "論拠" in reasoning
    
    # PURPOSE: 判定パース: REJECT
    def test_parse_verdict_reject(self):
        """判定パース: REJECT"""
        agent = DebateAgent(AgentRole.ARBITER)
        text = "判定: REJECT\n確信度: 70%\n理由: 証拠不足。"
        verdict_type, confidence, reasoning = agent._parse_verdict(text)
        
        assert verdict_type == VerdictType.REJECT
        assert confidence == 0.7


class TestDebateEngine:
    """DebateEngine のテスト"""
    
    # PURPOSE: エンジン作成
    def test_create_engine(self):
        """エンジン作成"""
        engine = DebateEngine()
        assert engine.proposer.role == AgentRole.PROPOSER
        assert len(engine.critics) == 2
        assert engine.arbiter.role == AgentRole.ARBITER
    
    # PURPOSE: 合意構築
    def test_build_consensus(self):
        """合意構築"""
        engine = DebateEngine()
        
        # モックラウンド
        rounds = [
            DebateRound(
                round_number=1,
                proposition=DebateArgument(
                    AgentRole.PROPOSER,
                    "支持論拠",
                    0.8
                ),
                critiques=[
                    DebateArgument(AgentRole.CRITIC, "批判1", 0.6),
                    DebateArgument(AgentRole.CRITIC, "批判2", 0.5)
                ]
            )
        ]
        
        verdict = Verdict(
            type=VerdictType.ACCEPT,
            reasoning="論拠が勝る",
            confidence=0.75
        )
        
        result = engine._build_consensus("テスト主張", rounds, verdict)
        
        assert result.accepted is True
        assert result.confidence == 0.75
        assert len(result.rounds) == 1


class TestAuditRecord:
    """AuditRecord のテスト"""
    
    # PURPOSE: レコード作成
    def test_create_record(self):
        """レコード作成"""
        record = AuditRecord(
            record_id="audit_001",
            ccl_expression="/noe+",
            execution_result="分析結果",
            debate_summary="ラウンド数: 3",
            consensus_accepted=True,
            confidence=0.85,
            dissent_reasons=[]
        )
        assert record.record_id == "audit_001"
        assert record.consensus_accepted is True


class TestAuditStore:
    """AuditStore のテスト"""
    
    # PURPOSE: 一時ストア
    @pytest.fixture
    def temp_store(self, tmp_path):
        """一時ストア"""
        db_path = tmp_path / "test_audit.db"
        return AuditStore(db_path)
    
    # PURPOSE: 記録と取得
    def test_record_and_get(self, temp_store):
        """記録と取得"""
        record = AuditRecord(
            record_id="",
            ccl_expression="/s+",
            execution_result="成功",
            debate_summary="テスト",
            consensus_accepted=True,
            confidence=0.9,
            dissent_reasons=["反対意見1"]
        )
        
        record_id = temp_store.record(record)
        assert record_id is not None
        
        retrieved = temp_store.get(record_id)
        assert retrieved is not None
        assert retrieved.ccl_expression == "/s+"
        assert retrieved.confidence == 0.9
    
    # PURPOSE: クエリ
    def test_query(self, temp_store):
        """クエリ"""
        # 複数レコードを挿入
        for i in range(5):
            temp_store.record(AuditRecord(
                record_id="",
                ccl_expression=f"/wf{i}+",
                execution_result=f"結果{i}",
                debate_summary="",
                consensus_accepted=i % 2 == 0,
                confidence=0.5 + i * 0.1,
                dissent_reasons=[]
            ))
        
        # 全件クエリ
        all_records = temp_store.query()
        assert len(all_records) == 5
        
        # 確信度フィルタ
        high_conf = temp_store.query(min_confidence=0.7)
        assert len(high_conf) == 3
    
    # PURPOSE: 統計取得
    def test_get_stats(self, temp_store):
        """統計取得"""
        for i in range(4):
            temp_store.record(AuditRecord(
                record_id="",
                ccl_expression="/test+",
                execution_result="",
                debate_summary="",
                consensus_accepted=i < 3,  # 3件受理、1件拒否
                confidence=0.8,
                dissent_reasons=[]
            ))
        
        stats = temp_store.get_stats()
        assert stats.total_records == 4
        assert stats.accepted_count == 3
        assert stats.rejected_count == 1


class TestAuditReporter:
    """AuditReporter のテスト"""
    
    # PURPOSE: 期間パース
    def test_parse_period(self, tmp_path):
        """期間パース"""
        store = AuditStore(tmp_path / "test.db")
        reporter = AuditReporter(store)
        
        now = datetime.now()
        
        since_7d = reporter._parse_period("last_7_days")
        assert (now - since_7d).days <= 7
        
        since_30d = reporter._parse_period("last_30_days")
        assert (now - since_30d).days <= 30


# =============================================================================
# Run
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
