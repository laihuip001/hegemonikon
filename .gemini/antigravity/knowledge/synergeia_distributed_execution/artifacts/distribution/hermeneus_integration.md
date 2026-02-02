# Distribution: Hermēneus Integration

On 2026-02-01, Synergeia's distributed execution capability was significantly enhanced through deep integration with the **Hermēneus CCL Compiler**.

## 1. Context

Previously, Synergeia coordinated tasks by mapping CCL IDs to specific model threads and sending raw prompt templates. While effective, this lacked a formal verification layer and had lower reliability for complex control structures.

## 2. The Integration: `execute_hermeneus`

A new core capability was added to the `coordinator.py` system:

- **Automatic Compilation**: The coordinator now detects if Hermēneus is available and routes CCL expressions through its compiler.
- **LMQL Transition**: CCL is translated into LMQL (Language Model Query Language) code.
- **Real-World Execution (`execute_ccl`)**: The coordinator now utilizes `hermeneus_execute` (aliased `execute_ccl` from Hermēneus) to perform the actual LLM call.
- **Results Handling**: The `llm_output` from Hermēneus is captured and returned in the coordinator's JSON result, enabling high-fidelity responses within a distributed pipeline.
- **Auto-Path Resolution**: The coordinator automatically injects the `HEGEMONIKON_ROOT` into `sys.path`, resolving potential import errors between Synergeia and the Hermēneus package.

## 3. Updated Thread Registry

The `THREAD_REGISTRY` now includes a high-priority `hermeneus` entry for universal compilation:

| Thread | Role | Priority |
| :--- | :--- | :--- |
| **Hermēneus** | Structure/Validation (LMQL) | 0 (Highest) |
| **Perplexity** | Research/Gnōsis | 5 |
| **Claude** | Schema/Logic | 5 |
| **Antigravity** | Manual/Core Bias | 10 |

## 4. Execution Flow

1. **Input**: User provides a CCL expression (e.g., `/noe+ || /sop-`).
2. **Coordination**: `parse_ccl` identifies parallel segments.
3. **Hermēneus Bridge**: `execute_ccl` invokes `execute_hermeneus`.
4. **Macro Injection**: The coordinator passes the `STANDARD_MACROS` (dynamically loaded from `ccl/macros/`) to the compiler.
5. **Compilation**: Hermēneus performs expansion using the injected macros, then parsing and translation to LMQL.
6. **Output**: The coordinator receives a structured `ExecutionResult` containing the expansion log, AST type, and generated code.

## 5. Impact

This integration completes the "Cognitive Enclosure" envisioned in the 4-layer hybrid architecture, where LLM variability is constrained by compiler-verified logic.

## 6. Phase 7: AI Self-Integrated Loop

With the introduction of the **Hermēneus MCP Server**, the "Hermēneus Bridge" becomes the primary interface for the AI assistant itself. Instead of the coordinator alone using Hermēneus, the AI can now proactively:

1. **Validate Intent**: Call `hermeneus_compile` to see how its plan translates to CCL.
2. **Execute & Verify**: Call `hermeneus_execute` to run workflows with a guaranteed audit trail.

## 7. Recursive Self-Evaluation Patterns

To solve the "Shallow Analysis" problem, the coordinator supports recursive self-evaluation patterns using the **Synteleia Macro Integration**:

- **Command**: `python synergeia/coordinator.py "@syn·[hermeneus/src]" "Evaluate architecture"`
- **Logic**:
    1. Synergeia routes the request through the Hermēneus Bridge.
    2. Hermēneus expands the `@syn` macro, which triggers the **Synteleia Layer**.
    3. Synteleia performs **directory ingestion**, reading the actual source code.
    4. The resulting high-fidelity context is passed to the LLM (Gemini/Claude) for a "Grounded Audit" rather than a surface guess.

### 7.1 Detecting Simulated (Airp) Output

If the audit report starts with "Actual source code is not included, providing simulation..." or similar caveats, it indicates a bridge failure (usually a missing module path).

**Technical Resolution**:
The `PYTHONPATH` must include both the `HEGEMONIKON_ROOT` and the `mekhane` directory to allow `from synteleia import ...` to function. The Coordinator enforces this dynamically:

```python
sys.path.insert(0, str(HEGEMONIKON_ROOT))
sys.path.insert(0, str(HEGEMONIKON_ROOT / "mekhane"))
```

---
*Reference: synergeia/coordinator.py (2026-02-01 Phase 7 Update)*
