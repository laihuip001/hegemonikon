# Hermēneus (Ἑρμηνεύς) — CCL Execution Guarantee Compiler

## 1. Vision

**Hermēneus** is the bridge between human-level cognitive algebra (CCL) and machine-level deterministic execution. While LLMs excel at understanding intent, they lack the reliability for long-running, complex workflows. Hermēneus provides a structured compiler that translates CCL into **LMQL** (Language Models Query Language) and **LangGraph**, ensuring a **>96% execution guarantee**.

### Model Theory: CCL Syntax-Semantics Mapping

From the perspective of Mathematical Logic:

- **Syntax**: The CCL expression (e.g., `/noe+*dia`).
- **Semantics (Model)**: The execution of the specific derivatives and workflows within **Hermēneus**.
- **Satisfaction**: A judgment or action "satisfies" the CCL intent if the model produced by Hermēneus remains consistent with the structural constraints of the syntax.

## 2. 4-Layer Hybrid Architecture

To overcome the limitations of pure LLM execution, Hermēneus uses four distinct layers:

| Layer | Technology | Role |
| :--- | :--- | :--- |
| **L1: Optimization** | DSPy Teleprompter | Continuous prompt optimization and refinement. |
| **L2: Control** | LMQL | Constrained decoding and structured output enforcement. |
| **L3: Execution** | LangGraph | State management, cycles, and multi-step orchestration. |
| **L4: Verification** | Multi-Agent Debate | Formal verification and peer-review of execution results (Synteleia). |

## 3. Core Principles & Insights

### Context Density over API Cost
>
> **"Naked API calls are trash. Context is everything."**

- **Axiom**: The value of an AI response is determined not by the model's inherent intelligence or the cost of the token, but by the **density and relevance of the context** provided in the prompt.
- **Application**: Hermeneus implements a "Synteleia Monitor" that automatically enriches the LLM context with audit results, issue details, and specific project constraints before execution.
- **Result**: Drastic reduction in "hallucinated" or generic ("airplay") outputs; the AI's suggestions become highly specific and actionable ("Doxa").

### The Immune Layer (Synteleia)

- **Concept**: Synteleia acts as the system's "immune system," auditing code and logic before it is committed or executed.
- **Integration**: Audit results are piped directly into Hermeneus's prompt controller to ensure the LLM is aware of existing weaknesses or technical debt.

### Lightweight Hierarchies (Thin Categories)

- **Strategy**: For complex derivative priority and task dependencies, Hermēneus utilizes **Thin Categories** (Lattices). This mathematical simplification allows for high structural reliability and deterministic resolving of hierarchical cognitive constraints without the full overhead of general Category Theory.

```text
hermeneus/
├── docs/               # Component specifications and architecture docs
├── src/                # Core implementation
│   ├── ast.py          # Abstract Syntax Tree definitions
│   ├── parser.py       # Formal CCL parser (CPL v2.0 compliant)
│   ├── translator.py   # AST-to-LMQL translator
│   ├── runtime.py      # Execution runtime
│   ├── graph.py        # LangGraph Orchestration
│   ├── verifier.py     # Multi-Agent Debate
│   ├── optimizer.py    # DSPy Optimization
│   ├── prover.py       # Formal Prover Interface (Mypy, Lean4)
│   ├── cli.py          # CLI & Production Toolkit
│   └── mcp_server.py   # MCP Server
└── tests/              # Pytest suite
```

## 5. Operational Progress (v0.8.0)

- **Phase 1-3 (Complete)**: Translation, LMQL Integration, and LangGraph Orchestration.
- **Phase 4-5 (Complete)**: Formal Verification, DSPy Optimization, and CLI Toolkit.
- **Phase 6-7 (Complete)**: Synergeia Integration, MCP Server, and Gemini 3 Pro Preview Upgrade.
- **Phase 8 (InProgress)**: Dendron L2 Purpose compliance (Teleological Verification).

## 6. L2 Purpose Audit Baseline (Cell P20)

As part of the **Project Dendron** recursive self-improvement audit (2026-02-06), Hermēneus currently has the following compliance status:

- **Total Functions/Classes**: 237
- **Current Coverage**: 0% (Missing `# PURPOSE:`)
- **Key Targets**: `prover.py` (27), `synergeia_adapter.py` (20), `hitl.py` (19).

**Strategic Goal**: Reaching 100% L2 compliance for the `src/` core by next cycle.

---
Updated: 2026-02-06 | Project Hermeneus Overview v0.9.0 (Dendron Integration)
