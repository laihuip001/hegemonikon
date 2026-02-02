# Synteleia Implementation: The 6-Agent Ensembles

Synteleia is implemented as a multi-agent orchestration system. The core implementation resides in the `mekhane/synteleia` package, where cognitive ensembles are executed across layered subdirectories.

## 0. Theoretical Role: Audit as Meta-Cognition

In the Synteleia paradigm, "Audit" is the **Meta-Cognitive Layer** in action. By running specialized agents concurrently, the system builds a "model of its own cognitive output" and evaluates it for consistency, intent, and structure. This mirrors the human prefrontal cortex's self-monitoring functions, mapped to the 6-categorical FEP basis.

## 1. 6-Axis Agent Matrix

The following 8 agents are implemented in `mekhane/synteleia/` (Dendron PROOF coverage 100%):

| Axis | Agent Class | Focus Area | Key Detections |
|------|-------------|------------|----------------|
| **O (Ousia)** | `OusiaAgent` | Essence Recognition | Vague references ("it", "that"), missing definitions. |
| **H (Hormē)** | `HormeAgent` | Motivation Evaluation | Unclear purpose ("just because", "maybe"), missing goals in plans. |
| **A (Akribeia)**| `OperatorAgent` | Symbolic Precision | Incorrect CCL operators, redundant code patterns. |
| | `LogicAgent` | Rational Consistency | Logical contradictions, infinite loops, dead code. |
| | `CompletenessAgent`| Judgment Suspension | Missing elements, `TODO` markers, empty blocks. |
| **S (Schema)** | `SchemaAgent` | Structure Evaluation | Header jumps, excessive empty lines, oversized functions. |
| **P (Perigraphē)**| `PerigrapheAgent` | Boundary Mapping | Scope creep ("and also", "while at it"), missing boundaries. |
| **K (Kairos)** | `KairosAgent` | Timing Evaluation | Procrastination ("later", "eventually"), premature optimization. |

## 1.1 Discovery & Integration

The `synteleia` package is located in `mekhane/synteleia/`. For external systems (like Hermēneus or Synergeia) to utilize the Orchestrator for code-base ingestion, the root `hegemonikon` or `mekhane` directory must be present in the `PYTHONPATH`.

Failure to provide the module results in "Airp" (simulated) analysis where the LLM guesses the audit results instead of reading the AST.

## 2. Technical Infrastructure (`mekhane/synteleia/`)

### Core Architecture

- **`base.py`**: Foundation classes (`AuditAgent`, `AuditTarget`, `AuditResult`).
- **`orchestrator.py`**: The `SynteleiaOrchestrator` manages the lifecycle and product operators.
- **`poiesis/`**: Subpackage for the Generative layer (O, S, H).
- **`dokimasia/`**: Subpackage for the Evaluative layer (P, K, A).

### Orchestration Modes

- **Inner Product (`·`) Logic**: Concurrent execution of layers with linear result merging. Enabled via `@syn·`.
- **Outer Product (`×`) Logic**: 3x3 Verification Matrix where the output of each Poiēsis agent (O, S, H) is scrutinized by each Dokimasia agent (P, K, A). Enabled via `@syn×`.
- Parallel execution via `concurrent.futures.ThreadPoolExecutor`.
- Result aggregation and severity weighting.

### Integration Flow

1. **Target Identification**: Input (Code, Plan, or Text) is wrapped in an `AuditTarget`.
   - **Correct API**: `AuditTarget(content=text, target_type=AuditTargetType.CODE, source="path/to/file")`
   - *Note: Historically, 'name' was used, but the v0.7.6 standard requires 'source' for better traceability.*
2. **Agent Dispatch**: The Orchestrator triggers the relevant ensemble (e.g., all 6 agents).
3. **Consensus & Integration**: Agents produce `AgentResult` objects. The Orchestrator synthesizes these into a single report, identifying critical risks.

## 3. Implementation Details

### A-Axis Specialists

The A-Axis is the most mature, with three distinct sub-agents ensuring mathematical and logical rigor.

- **`LogicAgent`**: Uses AST analysis and regex to detect `x != x` or `if True:` patterns.
- **`CompletenessAgent`**: Implements "Judgment Suspension" by flagging incomplete thoughts or placeholders.

### O/H/S/P/K Skeleton Implementations (Phase 2)

The other axes use regex-based pattern matching (heuristic-driven) to identify qualitative cognitive failures:

- **`OusiaAgent`**: Identifies technical terms without definitions and vague pronoun usage.
- **`SchemaAgent`**: Validates Markdown hierarchy and structural hygiene (blank lines, line lengths).
- **`KairosAgent`**: Specifically looks for temporal ambiguity in plans.
- **`PerigrapheAgent`**: Detects tokens of scope creep, ensuring focus.
- **`HormeAgent`**: Validates that every plan has an explicit motive keyword (`Purpose:`, `Why:`).

### Verification

As of 2026-02-01, the entire `mekhane/synteleia/` package achieved **100% Dendron PROOF coverage** (L1:9/L2:4), confirming its system-wide readiness.

## 4. The "Anti-Airp" (Anti-Shallow) Protocol

As of v0.7.6, Synteleia is utilized as a **Truth Layer** to prevent "Airp" (表面的なエアプ分析)—a failure mode where LLMs generate plausible-sounding but empty content due to lack of real data.

- **Impact**: This forces the evaluator agent to ground its findings in the actual AST and implementation patterns of the target directory, effectively banning \"shallow business-book style\" summaries.
- **Strategic Outcome**: Grounded audits achieve **Semantic Orthogonality**, where multiple independent axes (O/H/A/S/P/K) prune the LLM's hallucination space, forcing it into high-fidelity technical adherence.
- **Economic Viability**: Benchmarks confirm that the **"Context over Cost"** approach is highly efficient, with high-fidelity sessions costing as little as $0.02 USD while providing professional-grade structural fact-checking.

## 5. Future Directions: Phase 3+

- **`@S` Macro**: Direct invocation from within CCL expressions.
- **LLM-Based Agents**: Moving beyond regex to deep semantic evaluation for each axis.
- **Cross-Agent Debate**: Allowing agents to challenge each other's findings before final reporting.
- **Supreme Arbiter Layer**: Implementation of a conflict resolution engine to handle contradictory findings between agents (e.g., speed vs. security).
- **Optimizer Feedback Loop**: Direct integration with the `CCLOptimizer` to bootstrap few-shot examples from successful audits.
