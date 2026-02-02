# PROOF: [L2/インフラ] Hermēneus グラフテスト
"""
Hermēneus Graph Unit Tests

Phase 3: LangGraph 統合のテスト
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# パッケージパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hermeneus.src import (
    parse_ccl, compile_ccl,
    # Graph
    CCLState, NodeType, GraphNode, GraphEdge,
    CCLGraphBuilder, CompiledGraph, build_graph,
    # Checkpointer
    Checkpoint, CheckpointWrite,
    MemoryCheckpointer, save_state, load_state,
    # HITL
    InterruptType, HITLCommand,
    HITLController, HITLRequest, HITLResponse,
)


class TestCCLState:
    """CCLState のテスト"""
    
    def test_state_creation(self):
        """状態作成"""
        state: CCLState = {
            "context": "test",
            "results": [],
            "confidence": 0.5,
            "uncertainty": 0.5,
        }
        assert state["context"] == "test"
        assert state["confidence"] == 0.5


class TestGraphNode:
    """GraphNode のテスト"""
    
    def test_workflow_node(self):
        """ワークフローノード"""
        node = GraphNode(
            id="wf_noe_1",
            type=NodeType.WORKFLOW,
            workflow_id="noe"
        )
        assert node.type == NodeType.WORKFLOW
        assert node.workflow_id == "noe"
    
    def test_convergence_check_node(self):
        """収束チェックノード"""
        node = GraphNode(
            id="conv_1",
            type=NodeType.CONVERGENCE_CHECK,
            metadata={"var": "V[]", "op": "<", "value": 0.3}
        )
        assert node.type == NodeType.CONVERGENCE_CHECK
        assert node.metadata["value"] == 0.3


class TestCCLGraphBuilder:
    """CCLGraphBuilder のテスト"""
    
    def test_build_simple_workflow(self):
        """単純なワークフローからグラフ構築"""
        ast = parse_ccl("/noe+")
        builder = CCLGraphBuilder()
        graph = builder.build(ast)
        
        assert isinstance(graph, CompiledGraph)
        assert len(graph.nodes) >= 1
    
    def test_build_sequence(self):
        """シーケンスからグラフ構築"""
        ast = parse_ccl("/s+_/ene")
        builder = CCLGraphBuilder()
        graph = builder.build(ast)
        
        assert isinstance(graph, CompiledGraph)
        assert len(graph.nodes) >= 2
        assert len(graph.edges) >= 1
    
    def test_build_convergence(self):
        """収束ループからグラフ構築"""
        ast = parse_ccl("/noe+ >> V[] < 0.3")
        builder = CCLGraphBuilder()
        graph = builder.build(ast)
        
        assert isinstance(graph, CompiledGraph)
        # 収束チェックノードが存在する
        conv_nodes = [n for n in graph.nodes.values() if n.type == NodeType.CONVERGENCE_CHECK]
        assert len(conv_nodes) >= 1


class TestMemoryCheckpointer:
    """MemoryCheckpointer のテスト"""
    
    @pytest.mark.asyncio
    async def test_put_and_get(self):
        """保存と取得"""
        cp = MemoryCheckpointer()
        
        write = CheckpointWrite(
            thread_id="test-001",
            state={"context": "test", "results": []}
        )
        
        checkpoint = await cp.put(write)
        assert checkpoint.thread_id == "test-001"
        assert checkpoint.checkpoint_id is not None
        
        retrieved = await cp.get("test-001")
        assert retrieved is not None
        assert retrieved.state["context"] == "test"
    
    @pytest.mark.asyncio
    async def test_list_checkpoints(self):
        """履歴取得"""
        cp = MemoryCheckpointer()
        
        for i in range(3):
            await cp.put(CheckpointWrite(
                thread_id="test-002",
                state={"step": i}
            ))
        
        history = await cp.list("test-002")
        assert len(history) == 3
    
    @pytest.mark.asyncio
    async def test_delete(self):
        """削除"""
        cp = MemoryCheckpointer()
        
        await cp.put(CheckpointWrite(
            thread_id="test-003",
            state={"test": True}
        ))
        
        await cp.delete("test-003")
        
        retrieved = await cp.get("test-003")
        assert retrieved is None


class TestHITLController:
    """HITLController のテスト"""
    
    def test_register_interrupt(self):
        """割り込み登録"""
        controller = HITLController()
        
        controller.register_interrupt(
            "wf_noe_1",
            InterruptType.BEFORE,
            reason="高リスク操作"
        )
        
        point = controller.should_interrupt(
            "wf_noe_1",
            InterruptType.BEFORE,
            {}
        )
        
        assert point is not None
        assert point.reason == "高リスク操作"
    
    def test_should_not_interrupt_unregistered(self):
        """未登録ノードは割り込まない"""
        controller = HITLController()
        
        point = controller.should_interrupt(
            "unregistered_node",
            InterruptType.BEFORE,
            {}
        )
        
        assert point is None
    
    def test_create_and_respond(self):
        """リクエスト作成と応答"""
        controller = HITLController()
        
        controller.register_interrupt("wf_1", InterruptType.BEFORE)
        point = controller.should_interrupt("wf_1", InterruptType.BEFORE, {})
        
        request = controller.create_request(
            thread_id="test-hitl",
            point=point,
            state={"context": "test"}
        )
        
        assert request.request_id is not None
        assert len(controller.list_pending_requests()) == 1
        
        response = controller.respond(
            request.request_id,
            HITLCommand.PROCEED
        )
        
        assert response.command == HITLCommand.PROCEED
        assert len(controller.list_pending_requests()) == 0
    
    def test_apply_response_with_modifications(self):
        """状態修正の適用"""
        controller = HITLController()
        
        response = HITLResponse(
            request_id="test",
            command=HITLCommand.MODIFY,
            state_modifications={"new_key": "new_value"}
        )
        
        original_state = {"context": "original"}
        new_state = controller.apply_response(response, original_state)
        
        assert new_state["context"] == "original"
        assert new_state["new_key"] == "new_value"


class TestBuildGraph:
    """build_graph 関数のテスト"""
    
    def test_build_from_ccl_string(self):
        """CCL 文字列からグラフ構築"""
        graph = build_graph("/noe+")
        
        assert isinstance(graph, CompiledGraph)
        assert graph.entry_node is not None
    
    def test_build_complex_graph(self):
        """複雑な CCL からグラフ構築"""
        graph = build_graph("/s+_/bou_/ene")
        
        assert isinstance(graph, CompiledGraph)
        # シーケンスなのでエッジがある
        assert len(graph.edges) >= 2


# =============================================================================
# Run
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
