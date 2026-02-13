# PROOF: [L2/インフラ] <- hermeneus/src/ CCL → LangGraph グラフ変換
"""
Hermēneus Graph — CCL AST を LangGraph StateGraph に変換

CCL ワークフローをステートマシンとして実行し、
状態永続化と HITL を可能にする。

Origin: 2026-01-31 CCL Execution Guarantee Architecture
"""

from typing import Any, Dict, List, Optional, Callable, TypedDict, Annotated
from dataclasses import dataclass, field
from enum import Enum
import operator


# =============================================================================
# State Definition
# =============================================================================

# PURPOSE: [L2-auto] CCL 実行状態
class CCLState(TypedDict, total=False):
    """CCL 実行状態"""
    context: str                             # 入力コンテキスト
    results: Annotated[List[str], operator.add]  # 累積結果
    current_step: int                        # 現在のステップ
    current_node: str                        # 現在のノード ID
    confidence: float                        # 確信度 (0.0-1.0)
    uncertainty: float                       # 不確実性 (V[])
    iteration: int                           # 反復回数
    max_iterations: int                      # 最大反復
    converged: bool                          # 収束フラグ
    error: Optional[str]                     # エラーメッセージ
    metadata: Dict[str, Any]                 # メタデータ


# PURPOSE: [L2-auto] ノードタイプ
class NodeType(Enum):
    """ノードタイプ"""
    WORKFLOW = "workflow"
    FUSION = "fusion"
    CONVERGENCE_CHECK = "convergence_check"
    BRANCH = "branch"
    LOOP = "loop"
    END = "end"


@dataclass
# PURPOSE: [L2-auto] グラフノード
class GraphNode:
    """グラフノード"""
    id: str
    type: NodeType
    workflow_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
# PURPOSE: [L2-auto] グラフエッジ
class GraphEdge:
    """グラフエッジ"""
    source: str
    target: str
    condition: Optional[Callable[[CCLState], bool]] = None
    label: str = ""


# =============================================================================
# Graph Builder
# =============================================================================

# PURPOSE: [L2-auto] CCL AST → LangGraph StateGraph 変換器
class CCLGraphBuilder:
    """CCL AST → LangGraph StateGraph 変換器
    
    LangGraph がインストールされていない場合は、
    シンプルなステートマシン実装を使用。
    """
    
    # PURPOSE: Initialize instance
    def __init__(self):
        self._langgraph_available = self._check_langgraph()
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self._node_counter = 0
    
    # PURPOSE: LangGraph がインストールされているか確認
    def _check_langgraph(self) -> bool:
        """LangGraph がインストールされているか確認"""
        try:
            from langgraph.graph import StateGraph  # noqa: F401
            return True
        except ImportError:
            return False
    
    # PURPOSE: AST からグラフを構築
    def build(self, ast: Any) -> "CompiledGraph":
        """AST からグラフを構築"""
        # 遅延インポート
        from .ccl_ast import (
            Workflow, Sequence, ConvergenceLoop, Fusion, Oscillation,
            ForLoop, IfCondition, WhileLoop
        )
        
        # AST タイプに応じて構築
        entry_node = self._build_node(ast)
        
        if self._langgraph_available:
            return self._compile_with_langgraph(entry_node)
        else:
            return self._compile_fallback(entry_node)
    
    # PURPOSE: 新しいノード ID を生成
    def _new_node_id(self, prefix: str = "node") -> str:
        """新しいノード ID を生成"""
        self._node_counter += 1
        return f"{prefix}_{self._node_counter}"
    
    # PURPOSE: AST ノードからグラフノードを構築
    def _build_node(self, ast: Any) -> str:
        """AST ノードからグラフノードを構築"""
        from .ccl_ast import (
            Workflow, Sequence, ConvergenceLoop, Fusion, Oscillation,
            ForLoop, IfCondition, WhileLoop
        )
        
        if isinstance(ast, Workflow):
            return self._build_workflow(ast)
        elif isinstance(ast, Sequence):
            return self._build_sequence(ast)
        elif isinstance(ast, ConvergenceLoop):
            return self._build_convergence(ast)
        elif isinstance(ast, Fusion):
            return self._build_fusion(ast)
        elif isinstance(ast, Oscillation):
            return self._build_oscillation(ast)
        elif isinstance(ast, ForLoop):
            return self._build_for_loop(ast)
        elif isinstance(ast, IfCondition):
            return self._build_if_condition(ast)
        elif isinstance(ast, WhileLoop):
            return self._build_while_loop(ast)
        else:
            raise ValueError(f"Unknown AST type: {type(ast)}")
    
    # PURPOSE: Workflow ノードを構築
    def _build_workflow(self, wf: Any) -> str:
        """Workflow ノードを構築"""
        node_id = self._new_node_id(f"wf_{wf.id}")
        self.nodes[node_id] = GraphNode(
            id=node_id,
            type=NodeType.WORKFLOW,
            workflow_id=wf.id,
            metadata={"operators": [op.name for op in wf.operators]}
        )
        return node_id
    
    # PURPOSE: Sequence を直列エッジで構築
    def _build_sequence(self, seq: Any) -> str:
        """Sequence を直列エッジで構築"""
        if not seq.steps:
            return self._new_node_id("empty")
        
        # 各ステップをノードに変換
        step_ids = [self._build_node(step) for step in seq.steps]
        
        # エッジを作成
        for i in range(len(step_ids) - 1):
            self.edges.append(GraphEdge(
                source=step_ids[i],
                target=step_ids[i + 1],
                label="next"
            ))
        
        # 最初のノード ID を返す (エントリーポイント)
        return step_ids[0]
    
    # PURPOSE: ConvergenceLoop を条件付きサイクルで構築
    def _build_convergence(self, conv: Any) -> str:
        """ConvergenceLoop を条件付きサイクルで構築"""
        # 本体ノード
        body_id = self._build_node(conv.body)
        
        # 収束チェックノード
        check_id = self._new_node_id("convergence_check")
        self.nodes[check_id] = GraphNode(
            id=check_id,
            type=NodeType.CONVERGENCE_CHECK,
            metadata={
                "var": conv.condition.var,
                "op": conv.condition.op,
                "value": conv.condition.value
            }
        )
        
        # 終了ノード
        end_id = self._new_node_id("end")
        self.nodes[end_id] = GraphNode(id=end_id, type=NodeType.END)
        
        # エッジ: body → check
        self.edges.append(GraphEdge(source=body_id, target=check_id))
        
        # 条件付きエッジ: check → end (収束) or check → body (継続)
        # PURPOSE: Check converged
        def check_converged(state: CCLState) -> bool:
            uncertainty = state.get("uncertainty", 1.0)
            op = conv.condition.op
            value = conv.condition.value
            
            if op == "<":
                return uncertainty < value
            elif op == "<=":
                return uncertainty <= value
            elif op == ">":
                return uncertainty > value
            elif op == ">=":
                return uncertainty >= value
            return False
        
        self.edges.append(GraphEdge(
            source=check_id,
            target=end_id,
            condition=check_converged,
            label="converged"
        ))
        
        # ループバック (収束していない場合)
        self.edges.append(GraphEdge(
            source=check_id,
            target=body_id,
            condition=lambda s: not check_converged(s),
            label="continue"
        ))
        
        return body_id
    
    # PURPOSE: Fusion を並列ノードで構築
    def _build_fusion(self, fusion: Any) -> str:
        """Fusion を並列ノードで構築"""
        node_id = self._new_node_id("fusion")
        
        left_id = self._build_node(fusion.left)
        right_id = self._build_node(fusion.right)
        
        self.nodes[node_id] = GraphNode(
            id=node_id,
            type=NodeType.FUSION,
            children=[left_id, right_id]
        )
        
        return node_id
    
    # PURPOSE: Oscillation を双方向サイクルで構築
    def _build_oscillation(self, osc: Any) -> str:
        """Oscillation を双方向サイクルで構築"""
        left_id = self._build_node(osc.left)
        right_id = self._build_node(osc.right)
        
        # 双方向エッジ
        self.edges.append(GraphEdge(source=left_id, target=right_id, label="oscillate"))
        self.edges.append(GraphEdge(source=right_id, target=left_id, label="oscillate"))
        
        return left_id
    
    # PURPOSE: ForLoop を反復構造で構築
    def _build_for_loop(self, for_loop: Any) -> str:
        """ForLoop を反復構造で構築"""
        body_id = self._build_node(for_loop.body)
        
        node_id = self._new_node_id("for")
        self.nodes[node_id] = GraphNode(
            id=node_id,
            type=NodeType.LOOP,
            children=[body_id],
            metadata={"iterations": for_loop.iterations}
        )
        
        return node_id
    
    # PURPOSE: IfCondition を分岐で構築
    def _build_if_condition(self, if_cond: Any) -> str:
        """IfCondition を分岐で構築"""
        then_id = self._build_node(if_cond.then_branch)
        else_id = self._build_node(if_cond.else_branch) if if_cond.else_branch else None
        
        node_id = self._new_node_id("branch")
        children = [then_id]
        if else_id:
            children.append(else_id)
        
        self.nodes[node_id] = GraphNode(
            id=node_id,
            type=NodeType.BRANCH,
            children=children,
            metadata={
                "condition": {
                    "var": if_cond.condition.var,
                    "op": if_cond.condition.op,
                    "value": if_cond.condition.value
                }
            }
        )
        
        return node_id
    
    # PURPOSE: WhileLoop を条件付きループで構築
    def _build_while_loop(self, while_loop: Any) -> str:
        """WhileLoop を条件付きループで構築"""
        body_id = self._build_node(while_loop.body)
        
        node_id = self._new_node_id("while")
        self.nodes[node_id] = GraphNode(
            id=node_id,
            type=NodeType.LOOP,
            children=[body_id],
            metadata={
                "condition": {
                    "var": while_loop.condition.var,
                    "op": while_loop.condition.op,
                    "value": while_loop.condition.value
                }
            }
        )
        
        return node_id
    
    # PURPOSE: LangGraph を使用してコンパイル
    def _compile_with_langgraph(self, entry_node: str) -> "CompiledGraph":
        """LangGraph を使用してコンパイル"""
        from langgraph.graph import StateGraph, END
        
        graph = StateGraph(CCLState)
        
        # ノードを追加
        for node_id, node in self.nodes.items():
            if node.type == NodeType.WORKFLOW:
                graph.add_node(node_id, self._create_workflow_executor(node))
            elif node.type == NodeType.CONVERGENCE_CHECK:
                graph.add_node(node_id, self._create_convergence_checker(node))
            elif node.type == NodeType.END:
                # END は特別なノード
                pass
            else:
                graph.add_node(node_id, self._create_generic_executor(node))
        
        # エッジを追加
        for edge in self.edges:
            if edge.target in self.nodes and self.nodes[edge.target].type == NodeType.END:
                target = END
            else:
                target = edge.target
            
            if edge.condition:
                # 条件付きエッジ
                graph.add_conditional_edges(
                    edge.source,
                    lambda s, e=edge: "converged" if e.condition(s) else "continue",
                    {"converged": END, "continue": edge.target}
                )
            else:
                graph.add_edge(edge.source, target)
        
        # エントリーポイント設定
        graph.set_entry_point(entry_node)
        
        return CompiledGraph(graph.compile(), entry_node, self.nodes, self.edges)
    
    # PURPOSE: フォールバック: シンプルなステートマシン
    def _compile_fallback(self, entry_node: str) -> "CompiledGraph":
        """フォールバック: シンプルなステートマシン"""
        return CompiledGraph(None, entry_node, self.nodes, self.edges)
    
    # PURPOSE: ワークフロー実行関数を作成
    def _create_workflow_executor(self, node: GraphNode) -> Callable:
        """ワークフロー実行関数を作成"""
        # PURPOSE: Execute
        def execute(state: CCLState) -> CCLState:
            from .runtime import execute_ccl
            
            wf_id = node.workflow_id
            context = state.get("context", "")
            
            # ワークフローを実行
            result = execute_ccl(f"/{wf_id}", context)
            
            return {
                "results": [result.output],
                "current_node": node.id,
                "confidence": result.confidence,
                "uncertainty": 1.0 - result.confidence
            }
        return execute
    
    # PURPOSE: 収束チェック関数を作成
    def _create_convergence_checker(self, node: GraphNode) -> Callable:
        """収束チェック関数を作成"""
        # PURPOSE: Check
        def check(state: CCLState) -> CCLState:
            uncertainty = state.get("uncertainty", 1.0)
            iteration = state.get("iteration", 0)
            max_iter = state.get("max_iterations", 5)
            
            op = node.metadata["op"]
            value = node.metadata["value"]
            
            converged = False
            if op == "<":
                converged = uncertainty < value
            elif op == ">":
                converged = uncertainty > value
            
            return {
                "iteration": iteration + 1,
                "converged": converged or iteration >= max_iter
            }
        return check
    
    # PURPOSE: 汎用実行関数を作成
    def _create_generic_executor(self, node: GraphNode) -> Callable:
        """汎用実行関数を作成"""
        # PURPOSE: Execute
        def execute(state: CCLState) -> CCLState:
            return {"current_node": node.id}
        return execute


# =============================================================================
# Compiled Graph
# =============================================================================

@dataclass
# PURPOSE: [L2-auto] コンパイル済みグラフ
class CompiledGraph:
    """コンパイル済みグラフ"""
    langgraph: Any  # LangGraph StateGraph (なければ None)
    entry_node: str
    nodes: Dict[str, GraphNode]
    edges: List[GraphEdge]
    
    # PURPOSE: グラフを実行
    def invoke(
        self,
        context: str,
        config: Optional[Dict[str, Any]] = None
    ) -> CCLState:
        """グラフを実行"""
        initial_state: CCLState = {
            "context": context,
            "results": [],
            "current_step": 0,
            "current_node": self.entry_node,
            "confidence": 0.0,
            "uncertainty": 1.0,
            "iteration": 0,
            "max_iterations": 5,
            "converged": False,
            "error": None,
            "metadata": {}
        }
        
        if self.langgraph:
            return self.langgraph.invoke(initial_state, config)
        else:
            return self._fallback_execute(initial_state)
    
    # PURPOSE: フォールバック実行
    def _fallback_execute(self, state: CCLState) -> CCLState:
        """フォールバック実行"""
        from .runtime import execute_ccl
        
        current = self.entry_node
        visited = set()
        
        while current and current not in visited:
            visited.add(current)
            
            if current not in self.nodes:
                break
            
            node = self.nodes[current]
            
            # ノード実行
            if node.type == NodeType.WORKFLOW:
                result = execute_ccl(f"/{node.workflow_id}", state["context"])
                state["results"].append(result.output)
                state["confidence"] = result.confidence
                state["uncertainty"] = 1.0 - result.confidence
            
            elif node.type == NodeType.END:
                break
            
            # 次のノードを探す
            next_node = None
            for edge in self.edges:
                if edge.source == current:
                    if edge.condition is None or edge.condition(state):
                        next_node = edge.target
                        break
            
            current = next_node
            state["current_node"] = current or "end"
            state["iteration"] += 1
            
            if state["iteration"] > state["max_iterations"]:
                break
        
        state["converged"] = state["uncertainty"] < 0.3
        return state


# =============================================================================
# Convenience Functions
# =============================================================================

# PURPOSE: CCL 式からグラフを構築
def build_graph(ccl: str, macros: Optional[Dict[str, str]] = None) -> CompiledGraph:
    """CCL 式からグラフを構築
    
    Args:
        ccl: CCL 式
        macros: マクロ定義
        
    Returns:
        CompiledGraph
        
    Example:
        >>> graph = build_graph("/noe+_/bou >> V[] < 0.3")
        >>> result = graph.invoke("プロジェクトを分析")
    """
    from .parser import parse_ccl
    from .expander import expand_ccl
    
    # 展開
    expansion = expand_ccl(ccl, macros)
    expanded = expansion.expanded if hasattr(expansion, 'expanded') else expansion
    
    # パース
    ast = parse_ccl(expanded)
    
    # グラフ構築
    builder = CCLGraphBuilder()
    return builder.build(ast)


# PURPOSE: グラフを実行
def execute_graph(
    graph: CompiledGraph,
    context: str,
    thread_id: Optional[str] = None,
    **kwargs
) -> CCLState:
    """グラフを実行
    
    Args:
        graph: コンパイル済みグラフ
        context: 入力コンテキスト
        thread_id: スレッド ID (状態永続化用)
        **kwargs: 追加設定
        
    Returns:
        最終状態
    """
    config = {}
    if thread_id:
        config["configurable"] = {"thread_id": thread_id}
    
    return graph.invoke(context, config)
