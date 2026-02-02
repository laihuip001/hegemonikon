# FEP Integration Design Principles (2026-01-29)

## 1. The 2.5-Layer Architecture

Through a deep `O1 Noēsis` analysis (nous derivative), a "2.5-layer architecture" was established as the optimal design for integrating Active Inference features into Hegemonikón. This pattern balances structural integrity with implementation efficiency.

| Layer | Component | Role |
| :--- | :--- | :--- |
| **Layer 1: Base** | `encoding.py` | Low-level text-to-observation mapping. Expanded to include `auto_encode_noesis()` and `format_learning_progress()`. |
| **Layer 1.5: Navigation** | `x_series_navigator.py` | Mapping of the 36-relation matrix to the FEP state space for next-step recommendations. |
| **Layer 2: Bridge** | `fep_bridge.py` | High-level API for workflows. Expanded with `run_with_xseries()` to provide a unified inference entry point. |

## 2. Integrated Feature Specifications

### 2.1 X-Series FEP Navigation

The 36 relations defined in the `X-series` (Taxis) are modeled as transitions within the FEP agent's state space.

- **Logic**: Use the current series (O, S, H, P, K, A) as the prior state.
- **Goal**: Recommend the next series/workflow based on the MAP (Maximum A Posteriori) state of the FEP agent.

### 2.2 Real-Time Learning Visualization

To demystify the "black box" of Active Inference, the refinement of the **A-Matrix** (the observation model) is made visible.

- **Standard**: The `format_learning_progress` utility calculates the change in Dirichlet concentration parameters before and after an observation.
- **Benefit**: Provides immediate feedback on how the agent "learned" the mapping between context symbols and state hidden variables.

### 2.3 Automated Workflow Encoders

The transition from qualitative workflow output (e.g., /noe PHASE 5 JSON) to quantitative FEP observations is automated.

- **Implementation**: `auto_encode_noesis(phase5_output)` extracts `confidence_score` and `uncertainty_zones`.
- **Constraint**: More uncertainty zones (higher entropy in the qualitative analysis) lead to more ambiguous context indices in the FEP observation.

## 3. Design Principles

- **Zero-Entropy Convergence**: Integration must reduce, not increase, cognitive load. Automated encoding is preferred over manual parameter setting.
- **Orthogonal Divergence**: When designing new features, consider the 4-vectors (Idealist, Minimalist, Heretic, Analyst) to avoid local optima.
- **Self-Referential Stability**: As the FEP agent analyzes its own integration, identify and mitigate self-reference paradoxes (Meta-Blindspot check).

---
*Reference: Conversation ID 89359020-c5e4-4636-b9ee-28c1d6e0047a | /noe Analysis (nous)*
