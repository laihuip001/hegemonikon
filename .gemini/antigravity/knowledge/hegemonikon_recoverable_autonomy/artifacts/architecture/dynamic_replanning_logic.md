# Architectural Pattern: Dynamic Replanning Loop

> **Component**: `/ene` (Energeia)
> **Goal**: Recoverable autonomy during execution failure.

## 1. Failure-Initiated Loop

When a verification phase (Phase 6 in Energeia) returns a "Fail" or "Significant Drift" signal, the system should not simply stop. It must enter a dynamic replanning state.

## 2. Transition Logic

- **Detection**: Verification output < threshold or User intervention.
- **Immediate Action**: Suspend execution, trigger `/zet` (Zētēsis) to analyze the obstacle.
- **Alignment**: Feed analysis results into `/bou` (Boulēsis) to redefine the goal based on the new context.
- **Resumption**: Update the plan and restart `/ene`.

## 3. Cognitive Symbol

`V[verify] < 0.7 -> /zet -> /bou+ -> /ene` (Dynamic Recalibration)

---
*Integration Note: Insight from Task 5 - Perplexity Research (2026-01-31)*
