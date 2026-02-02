# Methodology: Recursive Plan Review (@plan_review)

## 1. Overview

The **Recursive Plan Review** methodology is a structural enforcement pattern used to critically evaluate and refine implementation plans. It leverages the "Cognitive Algebra" of CCL to apply multiple high-order theorems to a specific task or plan artifact.

## 2. The @plan_review Macro

The macro is typically invoked to trigger a sequence of diagnostic workflows:

```ccl
let @plan_review = /dia+ _/pre+ _/sta.done _/chr.dead _/kho.scope
```

### 2.1 Component breakdown

| Workflow | Theorem | Diagnostic Dimension |
| :--- | :--- | :--- |
| `/dia+` | **Krisis (A2)** | Critical analysis of gaps and logical inconsistencies. |
| `/pre+` | **Premortem** | Proactive identification of failure modes (pre-emptive failure). |
| `/sta.done` | **Stathmos (S3)** | Definition of Done (DoD) and success criteria verification. |
| `/chr.dead` | **Chronos (K2)** | Timeline feasibility and deadline pressure audit. |
| `/kho.scope` | **Khōra (P1)** | Resource boundaries and scope creep control. |

## 3. Advanced Refinement (akra variant)

For high-willpower (akrateia) scenarios where execution is non-negotiable, the macro is deepened:

```ccl
let @plan_review+ = /bou.akra+ _/kho.scope+ _/sta.done _/chr.dead _/epi.reference_class _/pre+
```

| Additional Workflow | Purpose |
| :--- | :--- |
| `/bou.akra+` | Intent purification; ensuring the "Core Desire" is preserved. |
| `/epi.reference_class` | Bayesian estimation based on similar past projects to correct 'planning fallacy'. |

---
*Developed during Project Hermēneus Phase 1 Context Recovery (2026-02-01)*
