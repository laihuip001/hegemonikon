# AI-Risk: 22 Implementation Axes

Implemented in `ai_auditor.py`.

| Code | Name | Severity | Description |
|:---|:---|:---:|:---|
| AI-001 | Naming Hallucination | High | Unknown module/function hallucinations. |
| AI-002 | API Misuse | High | Semantic errors in standard/AI API calls. |
| AI-003 | Type Confusion | Low | `len()` vs boolean comparisons. |
| AI-004 | Logic Hallucination | High | Infinite loops, division by zero. |
| AI-005 | Incomplete Code | - | (Disabled) TODO/FIXME/HACK markers. |
| AI-006 | Context Drift | Low | Argument reassignment. |
| AI-007 | Pattern Inconsistency | - | (Disabled) Style/naming drift. |
| AI-008 | Dependency Hole | High | Unused imports. |
| AI-009 | Hardcoded Secrets | Crit | CWE-798: API keys/secrets. |
| AI-010 | Validation Gap | Low | Untrusted path parameter input. |
| AI-011 | Over-Optimization | Low | Non-idiomatic loops (range(len)). |
| AI-012 | Async Blocking | Crit | `time.sleep` in `async def`. |
| AI-013 | Mutable Defaults | Med | `def f(x=[])`. |
| AI-014 | Excessive Comment | Low | Narrative meta-commentary. |
| AI-015 | Copy-Paste Error | High | Self-assignment (`x = x`). |
| AI-016 | Dead Code | Low | Unreachable code segments. |
| AI-017 | Magic Numbers | Low | Hardcoded numerical literals. |
| AI-018 | Hardcoded Paths | Low | Absolute/home paths. |
| AI-019 | Deprecated API | - | (Disabled) Use of outdated libraries. |
| AI-020 | Exception Swallowing | High | Bare excepts or silent pass. |
| AI-021 | Resource Leak | Med | `open()` without `with`. |
| AI-022 | Test Coverage Gap | Low | Missing docstrings. |

## Detection Logic Refinements

The following refinements were applied to eliminate false positives in the `mekhane/` audit:

- **AI-003 (Type Confusion)**: Refined to differentiate between implicit boolean conversion (Pythonic) and explicit `len(x) == True` comparisons.
- **AI-004 (Infinite Loops)**: Allowed `sys.exit`, `return`, and `exit` as valid termination. Added an exception for "scheduler patterns" (detected via `signal.` usage).
- **AI-006 (Context Drift)**: Added a "Casting/Normalization" exception. Reassignment is allowed if the variable name is reused for a derived value (e.g., `path = Path(path)`), identified by self-reference in the assignment RHS.
- **AI-007 (Patterns)**: Increased quote-ratio threshold to 0.4-0.6 and minimum count to 50 to focus on extreme inconsistencies only.
- **AI-009 (Secrets)**: Added a placeholder exclusion list (e.g., `YOUR_KEY`, `sk-...`, `test-key`) and skips docstrings/comments.
- **AI-012 (Async/Await)**: Added support for nested `async def` (e.g., in decorators like `retry`) to correctly attribute `await` calls.
- **AI-017 (Magic Numbers)**: Expanded acceptable constants list to 0-10, 16, 24, 32, 60, 64, 128, 255, 256, 512, 1024, etc.
- **AI-020 (Exceptions)**: Relaxed `pass` detection to allow it if an explanatory comment (TODO/NOTE/FIXME) is present.

## Strict Mode & Inline Suppression

Following the **Kairema 10** pivot on 2026-02-01, the system enforces a "Zero-Filter" policy. Every axis is enabled by default.

### 1. Unified Execution
All 22 axes are executed in every audit run. There is no longer a "Lenient" mode that silences technical debt.

### 2. Explicit Local Suppression
When a pattern is intentional and cannot be resolved through logic refinement, it must be explicitly suppressed at the line of occurrence using:
- `# noqa: AI-xxx` (e.g., `# noqa: AI-017`)
- `# auditor: ignore: AI-xxx`
- `# noqa` (Suppresses all findings on the line)

This preserves the audit's integrity while documenting the intentional deviation.
