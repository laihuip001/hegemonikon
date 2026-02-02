# Recoverable Autonomy Paradigm Specification

## 1. Overview

The **Recoverable Autonomy** paradigm shifts the focus from achieving absolute agent autonomy to ensuring that all agent actions are recoverable. Derived 2026-01-31, this principle asserts that trust is built not on the absence of failure, but on the reliability of recovery.

## 2. Core Principles

- **Recovery > Autonomy**: The system must prioritize the ability to revert to a known good state over the agent's ability to act without supervision.
- **Graduated Control**: Safety protocols (supervision and enforcement) scale in proportion to the operation's risk level.
- **Decision Persistence (Doxa)**: Every autonomous decision must be logged with its reasoning to ensure clinical accountability.
- **Fail-Fast & Revert**: Operations that exceed safety thresholds are aborted immediately, and the system is rolled back to the last stable checkpoint.

## 3. The 4-Layer Safety Stack

| Layer | Component | Function |
| :--- | :--- | :--- |
| **L1: Risk Evaluation** | `risk_tags.yaml` | Quantitative assessment of operation danger. |
| **L2: Supervision** | `@supervise` | Scaling oversight from self-check to council review. |
| **L3: Enforcement** | `@enforce` | Structural output constraints (Anti-Skip, Schema, Guardrails). |
| **L4: Recoverability** | `@rollback` | Git-based state restoration. |

## 4. Operational Logic

1. **Estimate Risk**: Map tool/operation calls to Low, Medium, or High.
2. **Apply Supervision**: Select oversight mode (PHASE 0.4).
3. **Trigger Enforcement**: Apply structural constraints (PHASE 0.5).
4. **Checkpoint**: Perform state snapshot before high-risk execution.
5. **Execute & Verify**: Perform the task and validate results.
6. **Rollback (if needed)**: Restore state upon verification failure.

---
*Created: 2026-01-31 | v7.5 Strategic Alignment*
