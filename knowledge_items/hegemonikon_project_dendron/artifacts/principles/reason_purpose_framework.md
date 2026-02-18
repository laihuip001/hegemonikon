# Reason/Purpose Analysis Framework (v2.0)

## 1. Overview

The **Temporal Layer** of Project Dendron distinguishes between a component's origin and its intent. This duality is critical for identifying **Existence Error** (Existence - Purpose).

## 2. The 2M-Matrix (Reason vs. Purpose)

| Dimension | Reason (理由) | Purpose (目的) |
| :--- | :--- | :--- |
| **Focus** | Background / Cause / Root | Target / Goal / Intent |
| **Temporal** | Past / Present (Why?) | Future (What for?) |
| **Linguistic** | "Because..." / "Since..." | "To..." / "For the purpose of..." |
| **Role** | Provides context and justification. | Defines essence and utility. |

> **Principle**: A component may have a valid *Reason* for existing (e.g., "It's been there for years") but if it lacks a *Purpose* (e.g., "Helping users achieve X"), it is considered **Waste**.

## 3. Implementation in Jules Tasks

Jules (Routine Task) agents use this framework to audit the codebase:

| # | Check-list Item | Target |
| :--- | :--- | :--- |
| 1 | Is the **Purpose** explicitly declared? | Existence Verification |
| 2 | Is the **Reason** contextually recorded? | Lineage Tracking |
| 3 | Is the **Purpose** still valid/relevant? | Entropy Audit |
| 4 | Is there a logical link between Reason and Purpose? | Coherence Check |
| 5 | Can the Purpose be achieved without this component? | Redundancy Test |

## 4. Normalization and MECE

Dendron maps database normalization principles to cognitive chunking:

| Normal Form | Meaning in Dendron | MECE Correspondence |
| :--- | :--- | :--- |
| **NF1** | Single, explicit Purpose. | **Atomic**: No mixed objectives. |
| **NF2** | Reasons are subordinate to Purpose. | **Hierarchical**: No partial dependencies. |
| **NF3** | No transitive goals. | **Direct**: No indirect logic. |
| **BCNF** | Purpose is the sole determinant of existence. | **Optimal**: Minimal necessary structure. |

---
*Updated: 2026-02-06*
*Lineage: Project Dendron VISION.md v3.0*
