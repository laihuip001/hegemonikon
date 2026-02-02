# Recoverable Autonomy Paradigm

## 1. Overview

The **Recoverable Autonomy** paradigm shifts the focus of agentic systems from absolute autonomy (total independence) to **Recoverability** (the ability to return to a known good state after failure). This acknowledges that, according to the **Free Energy Principle (FEP)**, failure is inevitable in complex environments.

## 2. Core Principles

- **Recoverability > Autonomy**: The system's value is measured not just by its independent actions, but by its resilience and ease of correction.
- **Graduated Autonomy**: Autonomy is granted based on trust and risk levels. Low-risk operations are autonomous, while high-risk operations require human approval.
- **Fail-Fast & Auto-Recovery**: The system should detect failures early and have mechanisms to revert state automatically.
- **Transparent Decision Logging**: All autonomous decisions must be recorded (e.g., in H4 Doxa) to ensure explainability and auditability.

## 3. Pattern Implementation

The "Recoverable Autonomy" pattern is implemented across the Hegemonikón framework:

| Phase | Strategy | Tool/Workflow |
| :--- | :--- | :--- |
| **Anticipation** | Premortem | `/pre` |
| **Execution** | Risk-Aware Action | `/ene` with Risk Tags |
| **Verification** | Crisis Analysis | `/dia` |
| **Persistence** | Doxa Logging | `anamnesis` / DoxaStore |
| **Recovery** | Auto-Rollback | `rollback.py` |

## 4. Derived Benefits

1. **Safety**: Structural enforcement of human-in-the-loop for dangerous operations.
2. **Scalability**: High-frequency, low-risk tasks proceed without bottlenecking humans.
3. **Traceability**: Every action has a recorded rationale, fulfilling the "Recoverability" requirement.

---
*Derived from /noe+ Analysis (2026-01-31)*
