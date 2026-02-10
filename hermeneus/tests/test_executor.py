# PROOF: [L3/テスト] <- hermeneus/tests/ Hermēneus Executor テスト
"""
Hermēneus Executor Unit Tests

Phase 6: Workflow Executor のテスト
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# パッケージパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hermeneus.src.executor import ExecutionPhase, PhaseResult, ExecutionPipeline, WorkflowExecutor, BatchExecutor
from hermeneus.src.registry import WorkflowDefinition, WorkflowStage, WorkflowParser, WorkflowRegistry
from hermeneus.src.synergeia_adapter import ThreadStatus, ThreadConfig, ThreadResult, ExecutionPlan, SynergeiaAdapter, PlanBuilder


class TestWorkflowStage:
    """WorkflowStage のテスト"""
    
    def test_create_stage(self):
        """ステージ作成"""
        stage = WorkflowStage(
            name="分析",
            description="多角的分析",
            substages=["視点1", "視点2"]
        )
        assert stage.name == "分析"
        assert len(stage.substages) == 2


class TestWorkflowDefinition:
    """WorkflowDefinition のテスト"""
    
    def test_create_definition(self):
        """定義作成"""
        wf = WorkflowDefinition(
            name="noe",
            ccl="/noe+",
            description="Noēsis (深い認識)",
            stages=[],
            modes=["deep"]
        )
        assert wf.name == "noe"
        assert wf.ccl == "/noe+"
    
    def test_get_prompt_template(self):
        """プロンプトテンプレート生成"""
        wf = WorkflowDefinition(
            name="test",
            ccl="/test+",
            description="テスト",
            stages=[
                WorkflowStage(name="Stage 1", substages=["A", "B"])
            ]
        )
        template = wf.get_prompt_template()
        assert "テスト" in template
        assert "Stage 1" in template


class TestWorkflowParser:
    """WorkflowParser のテスト"""
    
    def test_parse_simple(self, tmp_path):
        """シンプルなパース"""
        content = """---
description: テストワークフロー
---

# Test

## ステージ1

説明文

- サブ1
- サブ2
"""
        path = tmp_path / "test.md"
        path.write_text(content)
        
        parser = WorkflowParser()
        wf = parser.parse(path)
        
        assert wf.name == "test"
        assert wf.description == "テストワークフロー"
        assert len(wf.stages) >= 1


class TestWorkflowRegistry:
    """WorkflowRegistry のテスト"""
    
    def test_normalize_name(self):
        """名前正規化"""
        registry = WorkflowRegistry()
        
        assert registry._normalize_name("/noe+") == "noe"
        assert registry._normalize_name("/bou-") == "bou"
        assert registry._normalize_name("ene") == "ene"
    
    def test_get_nonexistent(self):
        """存在しないワークフロー"""
        registry = WorkflowRegistry(workflows_dir=Path("/nonexistent"))
        result = registry.get("nonexistent_workflow_xyz")
        assert result is None


class TestExecutionPhase:
    """ExecutionPhase のテスト"""
    
    def test_phases(self):
        """フェーズ列挙"""
        assert ExecutionPhase.INIT.value == "init"
        assert ExecutionPhase.COMPILE.value == "compile"
        assert ExecutionPhase.EXECUTE.value == "execute"
        assert ExecutionPhase.VERIFY.value == "verify"
        assert ExecutionPhase.AUDIT.value == "audit"


class TestPhaseResult:
    """PhaseResult のテスト"""
    
    def test_create_result(self):
        """結果作成"""
        result = PhaseResult(
            phase=ExecutionPhase.COMPILE,
            success=True,
            output="LMQL code",
            duration_ms=100.5
        )
        assert result.success is True
        assert result.duration_ms == 100.5


class TestExecutionPipeline:
    """ExecutionPipeline のテスト"""
    
    def test_create_pipeline(self):
        """パイプライン作成"""
        pipeline = ExecutionPipeline(
            ccl="/noe+",
            context="テスト",
            success=True,
            output="結果"
        )
        assert pipeline.ccl == "/noe+"
        assert pipeline.success is True
    
    def test_to_dict(self):
        """辞書変換"""
        pipeline = ExecutionPipeline(
            ccl="/noe+",
            context="テスト",
            workflow_name="noe",
            success=True,
            output="結果",
            verified=True,
            confidence=0.85
        )
        d = pipeline.to_dict()
        
        assert d["ccl"] == "/noe+"
        assert d["confidence"] == 0.85


class TestWorkflowExecutor:
    """WorkflowExecutor のテスト"""
    
    def test_create_executor(self):
        """エグゼキューター作成"""
        executor = WorkflowExecutor()
        assert executor.model == "openai/gpt-4o"
        assert executor.verify_by_default is True
    
    def test_extract_workflow_name(self):
        """ワークフロー名抽出"""
        executor = WorkflowExecutor()
        
        assert executor._extract_workflow_name("/noe+") == "noe"
        assert executor._extract_workflow_name("/bou+ >> /ene+") == "bou"
        assert executor._extract_workflow_name("/dia-") == "dia"


class TestThreadStatus:
    """ThreadStatus のテスト"""
    
    def test_statuses(self):
        """ステータス列挙"""
        assert ThreadStatus.PENDING.value == "pending"
        assert ThreadStatus.COMPLETED.value == "completed"
        assert ThreadStatus.FAILED.value == "failed"


class TestThreadConfig:
    """ThreadConfig のテスト"""
    
    def test_create_config(self):
        """設定作成"""
        config = ThreadConfig(
            name="analysis",
            ccl="/noe+",
            context="分析対象",
            timeout_seconds=120
        )
        assert config.name == "analysis"
        assert config.timeout_seconds == 120


class TestThreadResult:
    """ThreadResult のテスト"""
    
    def test_create_result(self):
        """結果作成"""
        result = ThreadResult(
            thread_name="test",
            ccl="/noe+",
            status=ThreadStatus.COMPLETED,
            output="結果",
            confidence=0.9
        )
        assert result.status == ThreadStatus.COMPLETED
    
    def test_to_dict(self):
        """辞書変換"""
        result = ThreadResult(
            thread_name="test",
            ccl="/noe+",
            status=ThreadStatus.COMPLETED,
            verified=True,
            confidence=0.85
        )
        d = result.to_dict()
        
        assert d["status"] == "completed"
        assert d["confidence"] == 0.85


class TestPlanBuilder:
    """PlanBuilder のテスト"""
    
    def test_build_plan(self):
        """プラン構築"""
        plan = (
            PlanBuilder()
            .add_thread("t1", "/noe+", "ctx1")
            .add_thread("t2", "/bou+", "ctx2")
            .set_parallel(True)
            .set_concurrency(3)
            .set_timeout(300)
            .build()
        )
        
        assert len(plan.threads) == 2
        assert plan.parallel is True
        assert plan.max_concurrent == 3
        assert plan.total_timeout_seconds == 300


class TestSynergeiaAdapter:
    """SynergeiaAdapter のテスト"""
    
    def test_create_adapter(self):
        """アダプター作成"""
        adapter = SynergeiaAdapter()
        assert adapter._executor is None  # 遅延初期化
    
    def test_generate_summary(self):
        """サマリー生成"""
        adapter = SynergeiaAdapter()
        results = [
            ThreadResult("t1", "/noe+", ThreadStatus.COMPLETED, confidence=0.9),
            ThreadResult("t2", "/bou+", ThreadStatus.FAILED, error="test error"),
        ]
        
        summary = adapter._generate_summary(results)
        assert "成功: 1" in summary
        assert "失敗: 1" in summary


# =============================================================================
# Run
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
