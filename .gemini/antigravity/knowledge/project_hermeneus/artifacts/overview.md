# Hermēneus (Ἑρμηνεύς) — CCL Execution Guarantee Compiler

## 1. Vision

**Hermēneus** is the bridge between human-level cognitive algebra (CCL) and machine-level deterministic execution. While LLMs excel at understanding intent, they lack the reliability for long-running, complex workflows. Hermēneus provides a structured compiler that translates CCL into **LMQL** (Language Models Query Language) and **LangGraph**, ensuring a **>96% execution guarantee**.

## 2. 4-Layer Hybrid Architecture

To overcome the limitations of pure LLM execution, Hermēneus uses four distinct layers:

| Layer | Technology | Role |
|:---|:---|:---|
| **L1: Optimization** | DSPy Teleprompter | Continuous prompt optimization and refinement. |
| **L2: Control** | LMQL | Constrained decoding and structured output enforcement. |
| **L3: Execution** | LangGraph | State management, cycles, and multi-step orchestration. |
| **L4: Verification** | Multi-Agent Debate | Formal verification and peer-review of execution results. |

## 3. Directory Structure

```
hermeneus/
├── docs/               # Component specifications and architecture docs
├── src/                # Core implementation
│   ├── ast.py          # Abstract Syntax Tree definitions
│   ├── expander.py     # Macro and shorthand expansion
│   ├── parser.py       # Formal CCL parser (CPL v2.0 compliant)
│   ├── translator.py   # AST-to-LMQL translator
│   ├── runtime.py      # [Phase 2] Execution runtime
│   ├── constraints.py  # [Phase 2] GCD Logic (Outlines)
│   ├── graph.py        # [Phase 3] LangGraph Orchestration
│   ├── checkpointer.py # [Phase 3] State Persistence
│   ├── hitl.py         # [Phase 3] Human-in-the-Loop
│   ├── verifier.py     # [Phase 4] Multi-Agent Debate
│   ├── audit.py        # [Phase 4] Audit Trail Persistence
│   ├── optimizer.py    # [Phase 4] DSPy Optimization
│   ├── prover.py       # [Phase 4b] Formal Prover Interface
│   ├── cli.py          # [Phase 5] CLI & Production Toolkit
│   ├── registry.py     # [Phase 6] Workflow Registry
│   ├── executor.py     # [Phase 6] Workflow Executor
│   ├── synergeia_adapter.py # [Phase 6] Synergeia Adapter
│   └── mcp_server.py   # [Phase 7] MCP Server
└── tests/              # Pytest suite (verified 125/125 pass)
```

## 4. Operational Progress

Hermēneus is developed following a 4-phase roadmap:

- **Phase 1 (Complete)**: Expander + Parser + AST + Translator logic.
- **Phase 2 (Complete)**: LMQL Runtime Integration & Constrained Decoding.
- **Phase 3 (Complete)**: LangGraph Orchestration & Checkpointing.
- **Phase 4 (Complete)**: Formal Verification, Audit Trail & DSPy Optimization.
- **Phase 4b (Complete)**: Formal Prover Interface (Mypy, Schema, Lean4).
- **Phase 5 (Complete)**: CLI Toolkit & Production Packaging.
- **Phase 6 (Complete)**: Workflow Executor & Full Synergeia Integration.
- **Phase 7 (Complete)**: MCP Server (AI Self-Integration) & Gemini 3 Pro Preview Upgrade.

---
*Updated: 2026-02-01 | Project Hermeneus Overview v0.8.0*
