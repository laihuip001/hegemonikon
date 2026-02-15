# FEP Theoretical Foundation

> Core FEP concepts that underpin the entire Hegemonikón framework.
> Jules reviewers: use this to understand WHY the code is structured this way.

## The Single Axiom

Hegemonikón has **one axiom**: the Free Energy Principle (FEP).
All cognitive systems minimize prediction error (surprise).

- `VFE = complexity - accuracy` — Variational Free Energy
- `EFE = epistemic + pragmatic` — Expected Free Energy (action selection)

## How FEP Maps to Code

| FEP Concept | Code Pattern | Example |
|:------------|:-------------|:--------|
| Prediction error | Assert / test / validation | `dendron/` checks |
| Precision weighting | Confidence scores (0-100) | BC-6 labels |
| Active inference | Workflow execution | CCL dispatch |
| Generative model | Knowledge base | `kernel/` definitions |
| Hierarchical inference | Module layers | kernel → hermeneus → mekhane |

## Key Implication for Review

Code that follows FEP should:

- **Minimize surprise**: predictable interfaces, clear naming
- **Balance exploration/exploitation**: not over-engineer, not under-design
- **Precision-weight**: important decisions get more verification (BC-14 FaR)
- **Update beliefs**: learn from errors, not repeat them
