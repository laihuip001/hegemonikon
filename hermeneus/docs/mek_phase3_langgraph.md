# [CCL]/mek+ Hermēneus Phase 3 — LangGraph 統合

---
sel:
  workflow: /mek+
  scope: P3=langgraph_integration
  output_format: CCL Skill Definition + Implementation Plan
  quality_gate: 
    - ステートフル実行
    - Checkpointer 永続化
    - HITL (Human-in-the-Loop)
---

## CCL シグネチャ

```ccl
/mek+ "Hermēneus Phase 3"
  [target: LangGraph Orchestration]
  {
    /s1 "StateGraph"      -- ステートマシン定義
    /s2 "Checkpointer"    -- 状態永続化
    /s3 "HITL"            -- Human-in-the-Loop
    /s4 "Streaming"       -- リアルタイム出力
  }
  >> オーケストレーション完成 ✅
```

---

## Phase 3 概要

| 属性 | 値 |
|:-----|:---|
| **目標** | CCL ワークフローを状態遷移グラフとして実行 |
| **成果物** | `hermeneus/src/graph.py`, `hermeneus/src/checkpointer.py` |
| **依存** | `pip install langgraph` |
| **検証** | 状態永続化 + HITL 動作確認 |

---

## LangGraph 概念マッピング

```ccl
# CCL → LangGraph 変換規則
let ccl_to_langgraph = {
  "/wf"       → Node(wf_executor)
  "_" (seq)   → Edge(step_n → step_n+1)
  "*" (fusion)→ ParallelNode([left, right])
  "~" (osc)   → CycleEdge(left ↔ right)
  ">>" (conv) → ConditionalEdge(check_convergence)
  "I:" (if)   → BranchPoint
  "W:" (while)→ LoopEdge
}
```

---

## 実装タスク CCL

```ccl
# Phase 3 タスクリスト
let phase_3_tasks = [
  /s1+ "StateGraph Definition" {
    CCLState dataclass 定義
    ワークフローをノードに変換
    演算子をエッジに変換
  }
  
  /s2+ "Checkpointer Implementation" {
    SQLite Checkpointer
    状態のシリアライズ/デシリアライズ
    Thread ID 管理
  }
  
  /s3+ "Human-in-the-Loop" {
    Interrupt Before/After
    ユーザー承認ポイント
    状態修正インターフェース
  }
  
  /s4+ "Streaming Output" {
    リアルタイムトークン出力
    進捗コールバック
    WebSocket 対応 (オプション)
  }
]

F:[phase_3_tasks]{/ene+} >> 全タスク完了
```

---

## コンポーネント設計

### CCLStateGraph

```ccl
/mek "CCLStateGraph"
  [input: CCL AST]
  [output: LangGraph StateGraph]
  {
    class CCLState(TypedDict):
      context: str
      results: List[str]
      current_step: int
      confidence: float
      iteration: int
      
    def build_graph(ast: ASTNode) -> StateGraph:
      # AST を走査してグラフを構築
      graph = StateGraph(CCLState)
      
      for node in ast:
        if Workflow:
          graph.add_node(node.id, execute_workflow)
        elif Sequence:
          for step in steps:
            graph.add_edge(prev, step)
        elif Convergence:
          graph.add_conditional_edges(...)
      
      return graph.compile()
  }
```

### CCLCheckpointer

```ccl
/mek "CCLCheckpointer"
  [input: Thread ID, State]
  [output: Persistent State]
  {
    class CCLCheckpointer(BaseCheckpointSaver):
      # SQLite ベース
      path: Path = ~/.hermeneus/checkpoints/
      
      def put(thread_id, state):
        # 状態を保存
        
      def get(thread_id):
        # 状態を復元
        
      def list(thread_id):
        # 履歴を取得
  }
```

### HITLController

```ccl
/mek "HITLController"
  [input: Graph, Interrupt Points]
  [output: Controlled Execution]
  {
    class HITLController:
      def interrupt_before(nodes: List[str]):
        # 指定ノードの前で停止
        
      def resume(thread_id, user_input):
        # ユーザー入力で再開
        
      def rollback(thread_id, checkpoint_id):
        # 過去の状態に戻る
  }
```

---

## 実装ファイル

| ファイル | 役割 |
|:---------|:-----|
| `src/graph.py` | [NEW] CCL → StateGraph 変換 |
| `src/checkpointer.py` | [NEW] 状態永続化 |
| `src/hitl.py` | [NEW] HITL コントローラー |
| `src/__init__.py` | [MODIFY] v0.3.0 API 更新 |
| `tests/test_graph.py` | [NEW] グラフテスト |

---

## 依存関係

```bash
# 必須
pip install langgraph>=0.2.0

# 推奨
pip install langgraph-checkpoint-sqlite  # 永続化
pip install langchain-core               # 基盤
```

---

## 使用例 (目標)

```python
from hermeneus.src import build_graph, execute_graph

# グラフ構築
graph = build_graph("/s+_/ene >> V[] < 0.3")

# 実行 (状態永続化あり)
result = execute_graph(
    graph,
    context="プロジェクト設計を分析",
    thread_id="session-001",
    checkpoint_path="~/.hermeneus/checkpoints/"
)

# HITL: 承認待ち状態から再開
result = resume_graph(
    thread_id="session-001",
    user_input="承認します",
    command="proceed"  # or "rollback", "modify"
)
```

---

## ユースケース CCL

### 1. 複雑なワークフロー実行

```ccl
# 分析→計画→実行 パイプライン
/noe+_/bou_/ene >> V[] < 0.2

# LangGraph 変換
StateGraph:
  noe → bou → ene → check_convergence
                    ↓ (not converged)
                    noe (loop back)
```

### 2. HITL 付き実行

```ccl
# 高リスク操作は承認必須
/s+[HITL:before]_/ene![HITL:after]

# LangGraph 変換
StateGraph:
  s → [INTERRUPT] → ene → [INTERRUPT]
      ↑ user approval    ↑ user review
```

### 3. 状態復元

```ccl
# 中断からの再開
/resume(thread_id="session-001")

# LangGraph 変換
checkpointer.get("session-001")
→ 最後の状態から再開
```

---

## リスク分析 CCL

```ccl
/pre "Phase 3 Risks"
  {
    R1: LangGraph API 変更    -- バージョン固定 + 抽象化レイヤー
    R2: 状態シリアライズ失敗  -- pickle → JSON 移行検討
    R3: HITL タイムアウト     -- 状態永続化で対処
    R4: グラフサイクル検出    -- DAG 検証ロジック追加
  }
  >> リスク緩和策実装
```

---

## アーキテクチャ図

```
                    ┌─────────────────────────────────────┐
                    │           CCL Input                 │
                    │    "/noe+_/bou >> V[] < 0.3"        │
                    └────────────────┬────────────────────┘
                                     │
                    ┌────────────────▼────────────────────┐
                    │     Phase 1: Parser (AST)           │
                    └────────────────┬────────────────────┘
                                     │
                    ┌────────────────▼────────────────────┐
                    │     Phase 3: Graph Builder          │
                    │     AST → StateGraph                │
                    └────────────────┬────────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         │                           │                           │
         ▼                           ▼                           ▼
   ┌───────────┐             ┌────────────┐             ┌─────────────┐
   │ Node: noe │ ──────────► │ Node: bou  │ ──────────► │ Node: check │
   └───────────┘             └────────────┘             └──────┬──────┘
         ▲                                                     │
         │                                              ▼ < 0.3?
         └──────────────────── NO ─────────────────────────────┘
                                                        │
                                                       YES
                                                        │
                    ┌───────────────────────────────────▼─────┐
                    │              END (Converged)            │
                    └─────────────────────────────────────────┘
                                     │
                    ┌────────────────▼────────────────────┐
                    │        Checkpointer (SQLite)        │
                    │     ~/.hermeneus/checkpoints/       │
                    └─────────────────────────────────────┘
```

---

## 次ステップ

```ccl
# Phase 3 完了後 → Phase 4 (Formal Verification)
/mek+ "Verification Layer"
  {
    Multi-Agent Debate
    Constrained Decoding 強化
    計算検証 (LeanDojo?)
  }
  _/ene+
```

---

*Generated: 2026-02-01 | Origin: /mek+ Hermēneus Phase 3*
