# Hermēneus Phase 3: Orchestration and Human-in-the-Loop Implementation

## 1. Goal
Transition the Hermēneus project from a linear compiler/executor into a stateful orchestrator capable of managing complex, long-running workflows with persistence and human oversight.

## 2. Core Components

### 2.1 Graph Translation (`graph.py`)
- **CCLGraphBuilder**: Translates the parsed CCL AST into a directed graph.
    - **LangGraph Mapping**: Maps `Sequence`, `ConvergenceLoop`, and `IfCondition` nodes to `StateGraph` nodes and edges.
    - **CCLState**: Defines a unified state schema (Context, Results, Confidence, Uncertainty) carried across graph nodes.
- **CompiledGraph**: A wrapper that abstracts whether the underlying execution engine is LangGraph or the internal lightweight fallback.

### 2.2 Persistence Layer (`checkpointer.py`)
- **CCLCheckpointer**: A SQLite-based persistence engine.
    - **Snapshot Persistence**: Automatically serializes the `CCLState` at each node transition.
    - **Time-Travel Debugging**: Allows for the listing and retrieval of previous checkpoints by `thread_id`, enabling rollbacks and session resumption.
- **MemoryCheckpointer**: A volatile in-memory implementation used for transient execution and unit testing.

### 2.3 Human-in-the-Loop (`hitl.py`)
- **HITLController**: Manages execution interrupts.
    - **Interrupt Points**: Nodes can be tagged with `BEFORE` or `AFTER` interrupts, triggering a pause in execution.
    - **Response Handlers**: Standardized protocol for human feedback, supporting `proceed`, `rollback`, `abort`, and `modify`.
    - **State Modification**: Allows the human operator to manually inject or correct data in the `CCLState` before resuming execution.

## 3. Orchestration API
The `build_graph()` entry point facilitates the higher-level orchestration:
1. `expand_ccl()`
2. `parse_ccl()`
3. `CCLGraphBuilder.build(ast)`
4. `CompiledGraph.invoke(initial_state)`

---
*Consolidated: 2026-02-01 | Phase 3 Implementation Detail*
