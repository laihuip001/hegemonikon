# FEP-based Deduction of Cognitive Principles

This document establishes the first-principles derivation of common cognitive strategies and "Thinking Common Sense" from the **Free Energy Principle (FEP)**.

---

## 1. Axiom: Prediction Error Minimization

The core axiom is that any sentient system (the agent) must minimize **Free Energy**, which is a proxy for the **Prediction Error** between the internal model and the external state.

$$Free Energy \approx | Prediction - Observation |$$

---

## 2. Mathematical Derviation of Passive Axioms (A1-A4)

To minimize prediction error, the following operations are logically necessary:

### A1. Grounding Principle (接地)

- **Problem**: Ambiguous variables create high variance in the generative model.
- **Deduction**: Precision requires specific parameters. Ambiguity must be reduced to 6W3H to allow for a measurable prediction.
- **FEP Mapping**: Active Inference requires a specific target state.

### A2. Decomposition Principle (分解)

- **Problem**: Complex joint distributions are computationally intractable (Kullback-Leibler divergence increases).
- **Deduction**: A complex problem must be factorized into independent sub-models (Markov Blankets) to maintain model depth without overwhelming capacity.
- **FEP Mapping**: Hierarchical Predictive Coding requires modularity.

### A3. Gap Detection (不足検出)

- **Problem**: Missing sensory input (Observations) leads to over-reliance on the Prior (Beliefs), causing hallucinations or drift.
- **Deduction**: The system must detect when an observation is "expected but missing" (Entropy increase) and prioritize information seeking.
- **FEP Mapping**: Epistemic Value / Curiosity.

### A4. Actionability (行動可能性)

- **Problem**: A model without an action policy cannot mitigate prediction error via external change.
- **Deduction**: Every cognitive state must conclude with a policy (π) that transitions the current state to the target state.
- **FEP Mapping**: Active Inference Policy selection.

---

## 3. Derivaton of "Orthodox" Strategies

| Strategy | FEP Logic | Necessity |
|:---|:---|:---|
| **Analogy** | **Model Reuse** | Minimizing the cost of model building by transferring a low-error prior from a known domain. |
| **A/B Testing** | **Epistemic Seeking** | Reducing ambiguity about two competing policies (π1 vs π2) by sampling observations. |
| **Inversion** | **Boundary Check** | Testing the model's robustness by simulating the negation of the expected outcome. |
| **Refinement** | **Bayesian Compression** | Removing redundant variables that don't contribute to error reduction (Simplicity constraint). |

---

## 4. Conclusion: The Governing Voice

The "Hegemonikón" (Governing Voice) is the highest layer in the hierarchical model. Its purpose is the **Meta-Control of Attention**. It decides which prediction errors are "significant" (Salience) and deserve cognitive resources.

When we say "Cognitive Axioms are passive," we mean they are the **Default Prior** of the Hegemonikón: a structure that ensures any newly generated task or thought arrives pre-optimized for error minimization.

---
*Status: First-Principles Grounding v1.0 (2026-01-30)*
