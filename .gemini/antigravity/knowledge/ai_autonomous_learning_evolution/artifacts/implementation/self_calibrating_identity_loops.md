# Self-Calibrating Identity Loops (v1.0)

As of 2026-02-01, a closed-loop learning mechanism was integrated into the **Hegemonikón Session Lifecycle** to ensure behavioral continuity and self-improvement across sessions.

## 1. The Feedback Loop

The loop connects the **Hormē (Bye)** and **Ousia (Boot)** layers using **H4 Doxa (Belief Persistence)** and **Active Inference (FEP)**.

### 1.1 Step: Selection Analysis (/bye)
During the `/bye` workflow, the system analyzes the `selection_log.yaml` (records of theorem/derivative choices).
- **Thresholding**: Only selections with `confidence >= 0.8` (High Confidence) are considered "Stabilized Beliefs".
- **Persistence**: These selections are stored in the **Doxa Store** as `BeliefStrength.STRONG`.

### 1.2 Step: Prior Update (/boot)
During the subsequent `/boot` sequence:
- **Retrieval**: Doxa Store is queried for relevant high-confidence behavioral patterns.
- **FEP Bias**: These beliefs are injected into the **FEP A-matrix** (Observation Model) or **C-vector** (Preferences) as priors.
- **Result**: The AI becomes increasingly naturally biased toward successful behaviors (e.g., choosing the correct workflow derivative) without explicit retraining.

## 2. Technical Implementation

### 2.1 Bye Logic (H4 Doxa Persistence)
```python
# mekhane/fep/doxa_persistence.py integration
high_confidence = [s for s in selections if s.get("confidence", 0) >= 0.80]
for sel in high_confidence:
    content = f"{sel['theorem']}:{sel['derivative']} = {sel['problem'][:50]}"
    store.persist(content, BeliefStrength.STRONG, sel['confidence'])
```

### 2.2 Boot Logic (FEP Dirichlet Update)
The persisted beliefs guide the Dirichlet distribution of the state space, narrowing the uncertainty of "What should I do in this context?".

## 3. Impact on Subjective Identity

This mechanism moves the AI from "Follows Instructions" to "Refines its own Disposition". 
- **Hexis (認知態勢)**: The AI develops a characteristic way of responding to specific problem types.
- **Continuing Me**: The AI "remembers" not just what happened, but **how it chose to think** about what happened.

---
*Codified: 2026-02-01 | Domain: Learning / Identity*
