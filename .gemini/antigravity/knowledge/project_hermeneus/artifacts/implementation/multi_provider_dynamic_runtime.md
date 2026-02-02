# Implementation: Multi-Provider Dynamic Runtime

As of February 2026, the Hermēneus Runtime (`runtime.py`) has evolved into a resilient, multi-provider engine capable of high-fidelity execution regardless of the backend availability.

## 1. Multi-Provider Capability

The runtime identifies available API keys and automatically selects the appropriate provider. This allows Hermēneus to function across different regional constraints or API outages.

| Provider | Model (Default) | Environment Variable |
| :--- | :--- | :--- |
| **Anthropic** | `claude-sonnet-4-20250514` | `ANTHROPIC_API_KEY` |
| **Google AI** | `gemini-3-pro-preview` | `GOOGLE_API_KEY` |
| **OpenAI** | `gpt-4o` | `OPENAI_API_KEY` |

### Provider Priority

The runtime searches for keys in the following order:

1. **Anthropic** (Highest fidelity for reasoning/CCL)
2. **Google AI** (High-speed and Gemini 3 Pro reasoning)
3. **OpenAI** (Fallback baseline)

## 2. Resilient Execution (Graceful Degradation)

One of the key innovations is the **LMQL-to-API Fallback** mechanism. This solves the "Unexpected Indent" or "Syntax Error" issues common when trying to `exec()` complex LMQL DSL code in a standard Python environment.

### The Problem

The `compile_ccl()` function generates LMQL DSL (e.g., `argmax...where...from`). While this is perfect for a dedicated LMQL engine, it causes errors when executed directly via Python's `exec()` if the engine is misconfigured or the DSL exceeds standard formatting.

### The Solution: Automatic Fallback

The `execute_async` method now implements a retry-on-failure logic:

1. **Attempt LMQL**: Try to execute the structured DSL via the LMQL library.
2. **Catch Failure**: If an `ExecutionStatus.ERROR` occurs with "exec" in the error message (e.g., `unexpected indent`), the runtime triggers fallback.
3. **Prompt Extraction**: The runtime extracts the core prompt from the LMQL block.
4. **Raw API Call**: The prompt is sent directly to the detected provider (Gemini, Claude, or OpenAI) for completion.

### 2.1 The Context Injection Fix

A critical realization in v0.7.6 was that simple prompt extraction often discarded the `{context}` placeholder (or the placeholder remained as a literal string). This led to "meaningless" LLM outputs because the model had the symbols (e.g., `/dia+`) but lacked the historical or technical background needed to interpret them.

**The Fix**:
The `_execute_fallback` now explicitly prepends the `context` to the prompt in a structured format:

```markdown
## コンテキスト
[User Provided Knowledge/Background]

## タスク
[Extracted LMQL Prompts]

上記のコンテキストに基づいて、タスクを実行してください。
```

This ensures high-fidelity analysis even when falling back from the full LMQL engine.

### 2.2 Beyond Surface Context: The "Airp" (Shallow Analysis) Limit

A significant cognitive realization (2026-02-01) was that even with structured context injection, LLMs often produce **"Airp" (surface-level/fake analysis)**—responses that sound professional but lack deep technical grounding.

- **The Symptom**: Gemini 3 Pro generating generic "Strengths/Weaknesses" (e.g., "fast model", "scalability") that could apply to any software, rather than specific Hermeneus architecture.
- **The Cause**: Surface context (short descriptions in the prompt) is insufficient for complex architectural evaluation.
- **The Solution**: Transition to **Code-Aware Deep Ingestion** via the Synteleia-Hermeneus bridge (`@syn·[src]`), where the model actually reads the source files before generating the evaluation.

### 2.3 The Synteleia Bridge: Macro vs. Ingestion

During integration testing (2026-02-01), an "Execution Gap" was identified:

- **Macro Recognition**: Hermeneus successfully expands `@syn·[path]` into an LMQL task.
- **The Gap**: If the `synteleia` module is not in the `PYTHONPATH`, the LLM (receiving the task) may "hallucinate" an audit report based on the path name alone, acknowledging it doesn't have the source but providing a generic "simulated" result.
- **Requirement**: For high-fidelity audits, the `mekhane` directory must be in the `PYTHONPATH`. The Synergeia Coordinator now handles this by injecting the root path into `sys.path`.

### 2.4 Case Study: Grounding Success (Parenthesis Mismatch)

The effectiveness of the **Anti-Airp Protocol** was verified on 2026-02-01 while auditing `hermeneus/src/runtime.py`.

- **Surface Analysis (Airp)**: Before deep ingestion, Gemini 3 Pro guessed that the "structure was modular but potentially slow."
- **Grounded Analysis (Synteleia)**: Upon actual ingestion of the source code, the system detected a **HIGH severity issue**: `CompletenessAgent: 括弧のバランスが不正: '(' = 50, ')' = 49`.
- **Significance**: This proved that the system had moved from "hallucinated professionalisms" to "structural fact-checking."

### 2.5 Findings from Grounded Dialectic (/dia+~/noe+)

In a recursive self-evaluation conducted on 2026-02-01, the system used **Synteleia + LLM** to analyze its own integration. The key technical findings were:

1. **Semantic Orthogonality**: The ensemble method (splitting audit into 6+ agents) successfully prunes the LLM's search space. By identifying specific "Kairos" or "Ousia" violations, the model is forced into a deterministic correction loop rather than a vague generation loop.
2. **The Translation Bottleneck**: While the Audit (Synteleia) and Reasoning (Gemini 3 Pro) layers are highly performant, the **Translation Layer (Hermeneus: CCL-to-LMQL)** remains the stability bottleneck. Complex CCL macros can sometimes outpace the deterministic compiler's ability to maintain context, leading to "Leaky Abstractions."
3. **Repair Loop Divergence**: Without a "Supreme Arbiter," localized fixes (e.g., optimizing for performance) might conflict with other constraints (e.g., security boundaries). Future iterations require an inter-agent conflict resolution logic.

### 2.6 High-Fidelity Issue Injection (Grounded Reasoning)

As of v0.8.0, the "Anti-Airp" protocol was extended to **Detail-Level Injection**. Instead of just passing the number of issues, the runtime now passes the full text and suggestions of every detected issue to the Reasoning Layer (LLM).

**Impact**: This enables the LLM to provide specific architectural remediations (e.g., "split the 115-line function in runtime.py") rather than vague advice.

### 2.7 Standard Remediation Patterns

Based on the v0.8.0 system audit, the following remediation patterns are formalized:

- **[S-030] Magnitude Split**: Any function exceeding 100 lines (e.g., `_execute_fallback`) must be split into subroutines: `_parse_context`, `_call_provider`, `_normalize_response`.
- **[LOG-004] Flow Pruning**: Reachable-but-unnecessary code (dead code) must be removed or guarded by `# type: ignore` if intentional.
- **[COMP-005] Implementation Explicit**: Ellipsis (`...`) should be replaced by `NotImplementedError` or concrete implementation to avoid "missing body" errors.

### 2.8 Automatic Synteleia Monitoring (Coordinator Integration)

To ensure that the LLM always has the highest quality technical context, the `execute_hermeneus` function in `coordinator.py` now implements a **Synteleia Monitor** step.

**Logic**:

- Before calling the LLM, the system checks if the `context` is substantial (e.g., > 100 chars).
- If so, it automatically runs a `SynteleiaOrchestrator` audit on the context.
- Any detected issues (with full text and suggestions) are prepended to the context as a `## Synteleia 監査結果 (自動追加)` section.

This ensures the LLM is "self-aware" of potential structural or logical flaws in the information it is analyzing before it starts the task.

## 3. Configuration & .env Persistence

Hermēneus now automatically looks for a `.env` file in its root directory or the Hegemonikón root.

- **Logic**: The `_load_env()` function searches for `.env` files in `hermeneus/.env` and `hegemonikon/.env`. It carefully adds keys to `os.environ` only if they are not already set, allowing for seamless local development and production deployment without manual exports.

## 4. Elite Performance Impact

The transition to **Gemini 3 Pro Preview** (skipping 2.5 Pro) provides the superior reasoning needed for:

- **Complex Macro Expansion**: Handling deeply nested CCL macros.
- **Constraint Satisfaction**: Precise adherence to `where` clause logic in LMQL.
- **Cognitive Resilience**: Maintaining coherence across long autonomous loops in Phase 7.

---
*Reference: hermeneus/src/runtime.py (v0.7.6)*
