# Architectural Specification: CPL v2.0 Syntax

## 1. Overview
Cognitive Programming Language (CPL) v2.0 is the formalized machine-executable representation of CCL shorthand. Hermēneus implements the formal grammar and precedence rules for this version to ensure deterministic translation into LMQL/LangGraph nodes.

## 2. Control Structures
Hermēneus supports four primary control structures, each mapped to a specific AST node:

| Structure | Syntax | Purpose |
|:---|:---|:---|
| **For Loop** | `F:[iterations]{body}` | Iterative execution over counts (`×3`) or lists. |
| **If-Condition** | `I:[cond]{then} E:{else}` | Semantic branching based on variable state. |
| **While Loop** | `W:[cond]{body}` | Loop until the semantic condition is met. |
| **Lambda** | `L:[params]{body}` | Functional abstraction for reusable workflows. |

## 3. Operator Precedence (Low to High)
The Hermēneus parser respects the following binary operator precedence to ensure correct expression grouping:

1. `_` (Sequence)
2. `~` (Oscillation)
3. `*` (Fusion)
4. `>>` (Convergence / `lim`)
5. `|>` (Pipeline)
6. `||` (Parallel)

## 4. Semantic Conditions
Conditions in CPL v2.0 allow for semantic gating using internal cognitive state variables:
- `V[]`: Vagueness / Uncertainty (Inverse of confidence).
- `E[]`: Entropy / Information Gain.
- **Syntax**: `[Var][Operator][Value]` (e.g., `V[] < 0.3`).

## 5. Normalization
Hermēneus expands all human-fluid shorthand (e.g., `>>`) into the formal `lim[cond]{body}` representation during the Expansion phase to ensure a canonical AST for the Translator.

---
*Standard: Hermēneus v0.2.0 | 2026-02-01*
