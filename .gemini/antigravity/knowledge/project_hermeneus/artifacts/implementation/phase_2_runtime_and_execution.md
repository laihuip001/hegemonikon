# Hermēneus Phase 2: Runtime and Execution Implementation

## 1. Goal
Transition the Hermēneus project from a static compiler into a functional execution engine capable of running compiled LMQL code with strict structural and semantic guarantees.

## 2. Core Components

### 2.1 LMQL Executor (`runtime.py`)
- **LMQLExecutor**: Manages the loading and execution of `@lmql.query` functions.
- **API Fallback**: Implements a robust fallback to vanilla OpenAI/LLM APIs by extracting core prompts from compiled LMQL code using regular expressions if the `lmql` library is not available in the environment.
- **Async Interface**: Provides `execute_async()` for seamless integration with concurrent Synergeia workflows.

### 2.2 Convergence Management (`runtime.py`)
- **ConvergenceExecutor**: Orchestrates the `>>` (Convergence) operator logic.
- **Heuristic Uncertainty Estimation**: Implements `_estimate_uncertainty()` to detect linguistic markers of doubt ("perhaps", "unclear", "?") vs. certainty ("definitely", "conclusion", "therefore"), allowing the loop to terminate only when confidence meets the threshold (default `V[] < 0.5`).
- **Iterative Refinement**: Automatically augments the context with previous attempts to drive probabilistic outputs toward deterministic alignment.

### 2.3 Constrained Decoding (`constraints.py`)
- **SchemaGenerator**: A utility that dynamically converts Python `dataclasses` into formal JSON Schema for structured output enforcement.
- **ConstrainedDecoder**:
    - Leverages the **Outlines** library for Grammar-Constrained Decoding (GCD) where supported.
    - **Schema-Injection Fallback**: For environments without Outlines, it automatically injects the JSON Schema into the prompt instructions and employs recursive regex-based parsing to ensure the output conforms to the required data structure.

## 3. High-Level API
The `execute_ccl()` entry point consolidates the entire pipeline:
1. `expand_ccl()`
2. `parse_ccl()`
3. `translate_to_lmql()`
4. `LMQLExecutor.execute()`

---
*Consolidated: 2026-02-01 | Phase 2 Implementation Detail*
