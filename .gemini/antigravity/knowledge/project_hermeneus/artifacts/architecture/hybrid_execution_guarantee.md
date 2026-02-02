# Architecture: Hybrid Execution Guarantee

## 1. The Core Paradox

LLMs are **prediction engines**, not **execution engines**. Even with a temperature of 0, non-determinism (due to float precision, caching, or distributed sampling) makes a 100% execution guarantee impossible for pure LLM prompts.

## 2. The 4-Layer Hybrid Model

To achieve a **>96% reliability score**, Hermēneus implements a 4-layer defense model that encapsulates the LLM within deterministic structures:

```
┌─────────────────────────────────────────┐
│ Layer 4: Verification (Multi-Agent/SMT) │ ← Phase 4b/5 (Lean4/Verified)
└────────────────────┬────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│ Layer 3: Execution (LangGraph/State)    │ ← Phase 3/6 (Orchestration)
└────────────────────┬────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│ Layer 2: Control (DSL/LMQL/GCD)         │ ← Phase 1/2 (Parser/Translator)
└────────────────────┬────────────────────┘
                     ↓
┌─────────────────────────────────────────┐
│ Layer 1: Optimization (DSPy/Auto-Refine)│ ← Phase 4 (Teleprompter)
└─────────────────────────────────────────┘
```

### 2.1 Layer Details

- **Symbolic Layer (DSL)**: Translating vague human intent into a structured AST.
- **Semantic Layer (Control)**: Using LMQL constraints to mask invalid tokens *during* sampling, ensuring type safety and structural compliance.
- **Structural Layer (Execution)**: Mapping the AST to a Directed Acyclic Graph (DAG) or State Machine (LangGraph). This allows for cycles, retries, and state persistence.
- **Verificational Layer (Auditing)**: Using multi-agent debate or formal verification (Z3/SMT) to confirm the output meets the original CCL specification.

## 3. Key Design Decisions

1. **Separation of Concerns**: The LLM *only* generates the "thought" or "content", while the compiler handles the "looping" and "branching".
2. **Grammar-Constrained Decoding (GCD)**: Forcing output to adhere to Pydantic schemas or regex patterns to eliminate "Format Induced Hallucinations".
3. **Recoverability over Autonomy**: Prioritizing the ability to save state and resume (Checkpointing) over unattended execution.

---
*Origin: Research Paper Ingestion & Perplexity Investigation (2026-01-31)*
