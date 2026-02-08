# PROOF: [L2/インフラ] <- hermeneus/src/ Hermēneus パッケージ
"""
Hermēneus — CCL 実行保証コンパイラ

CCL (Cognitive Control Language) を LMQL に翻訳し、
ハイブリッドアーキテクチャによる実行保証 (>96%) を実現する。

Usage:
    from hermeneus.src import compile_ccl
    lmql_code = compile_ccl("/noe+ >> V[] < 0.3")

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

from .ast import (
    OpType, Workflow, Condition, MacroRef,
    ConvergenceLoop, Sequence, Fusion, Oscillation, ColimitExpansion,
    ForLoop, IfCondition, WhileLoop, Lambda, Program,
    ASTNode
)
from .expander import Expander, ExpansionResult, expand_ccl
from .parser import CCLParser, parse_ccl
from .translator import LMQLTranslator, translate_to_lmql
from .runtime import (
    ExecutionStatus, ExecutionResult, ExecutionConfig,
    LMQLExecutor, ConvergenceExecutor, execute_ccl
)
from .constraints import (
    CCLOutputSchema, ConvergenceOutputSchema, SequenceOutputSchema,
    SchemaGenerator, ConstrainedDecoder,
    generate_constrained, generate_json
)
from .graph import (
    CCLState, NodeType, GraphNode, GraphEdge,
    CCLGraphBuilder, CompiledGraph,
    build_graph, execute_graph
)
from .checkpointer import (
    Checkpoint, CheckpointWrite,
    CCLCheckpointer, MemoryCheckpointer,
    save_state, load_state, list_checkpoints
)
from .hitl import (
    InterruptType, HITLCommand, InterruptPoint,
    HITLRequest, HITLResponse, HITLController,
    requires_approval, create_hitl_controller
)
from .optimizer import (
    OptimizerType, OptimizationConfig, OptimizationResult,
    CCLExample, CCLOptimizer, MockOptimizer,
    is_dspy_available, optimize_ccl, get_optimizer
)
from .verifier import (
    AgentRole, VerdictType, DebateArgument, Verdict,
    DebateRound, ConsensusResult, DebateAgent, DebateEngine,
    verify_execution, verify_execution_async, quick_verify
)
from .audit import (
    AuditRecord, AuditStats, AuditStore, AuditReporter,
    record_verification, query_audits, get_audit_report
)
from .prover import (
    ProofType, ProofStatus, ProofResult,
    ProverInterface, MypyProver, SchemaProver, Lean4Prover,
    ProofCache, verify_code, verify_schema, get_prover
)
from .registry import (
    WorkflowDefinition, WorkflowStage, WorkflowParser,
    WorkflowRegistry, get_workflow, list_workflows
)
from .executor import (
    ExecutionPhase, PhaseResult, ExecutionPipeline,
    WorkflowExecutor, BatchExecutor,
    run_workflow, run_workflow_sync, get_executor
)
from .synergeia_adapter import (
    ThreadStatus, ThreadConfig, ThreadResult, ExecutionPlan,
    SynergeiaAdapter, PlanBuilder,
    execute_synergeia_thread, create_plan, get_adapter
)

# MCP Server は Optional import (MCP SDK が必要)
try:
    from .mcp_server import MCP_AVAILABLE, run_server as run_mcp_server
except ImportError:
    MCP_AVAILABLE = False
    run_mcp_server = None


__version__ = "0.7.0"  # Phase 7
__all__ = [
    # AST Nodes
    "OpType", "Workflow", "Condition", "MacroRef",
    "ConvergenceLoop", "Sequence", "Fusion", "Oscillation", "ColimitExpansion",
    "ForLoop", "IfCondition", "WhileLoop", "Lambda", "Program",
    "ASTNode",
    # Expander
    "Expander", "ExpansionResult", "expand_ccl",
    # Parser
    "CCLParser", "parse_ccl",
    # Translator
    "LMQLTranslator", "translate_to_lmql",
    # Runtime (Phase 2)
    "ExecutionStatus", "ExecutionResult", "ExecutionConfig",
    "LMQLExecutor", "ConvergenceExecutor", "execute_ccl",
    # Constraints (Phase 2)
    "CCLOutputSchema", "ConvergenceOutputSchema", "SequenceOutputSchema",
    "SchemaGenerator", "ConstrainedDecoder",
    "generate_constrained", "generate_json",
    # Graph (Phase 3)
    "CCLState", "NodeType", "GraphNode", "GraphEdge",
    "CCLGraphBuilder", "CompiledGraph",
    "build_graph", "execute_graph",
    # Checkpointer (Phase 3)
    "Checkpoint", "CheckpointWrite",
    "CCLCheckpointer", "MemoryCheckpointer",
    "save_state", "load_state", "list_checkpoints",
    # HITL (Phase 3)
    "InterruptType", "HITLCommand", "InterruptPoint",
    "HITLRequest", "HITLResponse", "HITLController",
    "requires_approval", "create_hitl_controller",
    # Optimizer (Phase 4)
    "OptimizerType", "OptimizationConfig", "OptimizationResult",
    "CCLExample", "CCLOptimizer", "MockOptimizer",
    "is_dspy_available", "optimize_ccl", "get_optimizer",
    # Verifier (Phase 4)
    "AgentRole", "VerdictType", "DebateArgument", "Verdict",
    "DebateRound", "ConsensusResult", "DebateAgent", "DebateEngine",
    "verify_execution", "verify_execution_async", "quick_verify",
    # Audit (Phase 4)
    "AuditRecord", "AuditStats", "AuditStore", "AuditReporter",
    "record_verification", "query_audits", "get_audit_report",
    # Prover (Phase 4b)
    "ProofType", "ProofStatus", "ProofResult",
    "ProverInterface", "MypyProver", "SchemaProver", "Lean4Prover",
    "ProofCache", "verify_code", "verify_schema", "get_prover",
    # Registry (Phase 6)
    "WorkflowDefinition", "WorkflowStage", "WorkflowParser",
    "WorkflowRegistry", "get_workflow", "list_workflows",
    # Executor (Phase 6)
    "ExecutionPhase", "PhaseResult", "ExecutionPipeline",
    "WorkflowExecutor", "BatchExecutor",
    "run_workflow", "run_workflow_sync", "get_executor",
    # Synergeia Adapter (Phase 6)
    "ThreadStatus", "ThreadConfig", "ThreadResult", "ExecutionPlan",
    "SynergeiaAdapter", "PlanBuilder",
    "execute_synergeia_thread", "create_plan", "get_adapter",
    # Main API
    "compile_ccl",
]


def compile_ccl(
    ccl: str,
    macros: dict = None,
    model: str = "openai/gpt-4o"
) -> str:
    """CCL 式を LMQL プログラムにコンパイル
    
    Args:
        ccl: CCL 式 (例: "/noe+ >> V[] < 0.3")
        macros: マクロ定義 (例: {"think": "/noe+"})
        model: 使用する LLM モデル
        
    Returns:
        LMQL プログラムコード
        
    Example:
        >>> lmql_code = compile_ccl("/noe+")
        >>> print(lmql_code)
    """
    # Step 1: 展開
    expander = Expander(macro_registry=macros or {})
    expansion = expander.expand(ccl)
    
    # Step 2: パース
    parser = CCLParser()
    ast = parser.parse(expansion.expanded)
    
    # Step 3: 翻訳
    translator = LMQLTranslator(model=model)
    lmql_code = translator.translate(ast)
    
    return lmql_code


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """CLI エントリーポイント"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m hermeneus.src <ccl_expression>")
        print("Example: python -m hermeneus.src '/noe+ >> V[] < 0.3'")
        sys.exit(1)
    
    ccl = sys.argv[1]
    
    print(f"CCL: {ccl}")
    print("=" * 60)
    
    try:
        lmql_code = compile_ccl(ccl)
        print(lmql_code)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
