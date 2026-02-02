# AI Auditor: Refinement Heuristics (2026-02-01)

Following the "Project Mekháne" audit milestone, the Synedrion Auditor transitioned to a **Refined Strict Mode**. The goal is to achieve a "True Zero" state for actionable risks while eliminating stylistic noise that triggers false positives.

## 1. Noise Reduction Measures

| Check ID | Refinement | Rationale |
|:---|:---|:---|
| **AI-005** | Restricted `TODO`/`FIXME` to non-test files; disabled Ellipsis/Pass check. | `pass` is often a valid placeholder in flow modules or initial designs. |
| **AI-007** | **DISABLED** (Quote consistency). | Single/Double quote mix is not a safety risk and generates excessive noise. |
| **AI-019** | **DISABLED** (Deprecated APIs). | Too sensitive; moved to informational logs rather than issue reports. |

## 2. Smart Context Awareness

The auditor now applies "Heuristic Skips" based on context:

- **Type Confusion (AI-003)**: Skipped when direct casting or basic patterns like `len(x) == 0` are found.
- **Context Drift (AI-006)**: Skipped for small functions (<10 lines) and common patterns (e.g., `x = x or default`).
- **Input Validation (AI-010)**: Skipped for small utility functions (<= 5 statements) where validation is trivial or handled upstream.
- **Path/Server Awareness**: Checks for Hardcoded Paths (AI-018) and Async Misuse (AI-012) are bypassed for known environment-specific modules like MCP server files, tests, and task flows.

## 3. Enforcement Strategy

This pivot ensures that **Critical** and **High** issues are strictly enforced and must be 0 for any PR to clear the Synedrion gate, while the developer is no longer burdened by `# noqa` suppressions for stylistic choices.

---
*Policy Version: 2.1 | 2026-02-01 | Project Mekháne Post-Audit Optimization*
