# K3 Telos Checker: Technical Specification

## 1. Overview

**K3 Telos** is the monitor for goal-action alignment. It identifies when the *means* ( Mekhanē) have superseded the *ends* (Telos) and prevents cognitive drift within the session.

- **Module**: `hegemonikon/mekhane/fep/telos_checker.py`
- **FEP Role**: Generates a composite observation for context clarity and urgency based on alignment.

## 2. Drift Detection Patterns

The checker uses pattern matching and heuristic scoring to detect several types of "Telos Drift":

| Pattern | Description | Detection Keywords |
|:---|:---|:---|
| **Means-End Inversion** | The tool or process has become the goal. | `optimization`, `improvement`, `refactor` |
| **Scope Creep** | Adding features unrelated to the original intent. | `incidentally`, `while we're at it`, `future` |
| **Perfectionism Trap** | Seeking 100% when 80% is sufficient. | `perfect`, `all`, `complete`, `100%` |
| **Local Optimum** | Focus on micro-details over macro-outcome. | `temporarily`, `for now`, `later` |

## 3. Alignment Scoring & States

The module calculates an **Alignment Score (0.0 - 1.0)**:

- **Base Score**: 0.8
- **Penalties**: -0.15 per drift indicator detected.
- **Bonus**: +0.1 for high keyword overlap between goal and action.

### Alignment Statuses

- **ALIGNED**: High score, no drift. Action continues.
- **DRIFTING**: Minor misalignment. Triggers `/tel` self-reflection.
- **MISALIGNED**: Significant deviation. Triggers `/bou` re-prioritization.
- **INVERTED**: Means have become ends. Triggers `/noe` root cause analysis.

## 4. FEP Observation Encoding

The `TelosResult` is mapped to FEP observation modalities for the `HegemonikónFEPAgent`:

- **Context Clarity**: Mapped directly from the `alignment_score`.
- **Urgency**: Mapped from the number of drift indicators (more drift = higher urgency to correct).
- **Confidence**: High for ALIGNED, dropping significantly for INVERTED.

## 5. Implementation Usage

```python
from mekhane.fep.telos_checker import check_alignment

# Evaluates current intent against planned action
result = check_alignment(goal="Implement K3 module", action="Clean up imports")
if not result.is_aligned:
    print(result.suggestions)
```
