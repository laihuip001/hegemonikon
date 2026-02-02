# Hierarchical Evaluation & FEP Bridge Integration

## 1. Hierarchical Hybrid Evaluation Layer

To solve the "Observation Generation" problem efficiently, Hegemonikón uses a tiered approach that balances cost and accuracy.

### 1.1 The 3-Layer Architecture

When a text input is received, the `llm_evaluator.py` module executes the following hierarchy:

| Layer | Method | Cost | Trigger Condition |
| :--- | :--- | :--- | :--- |
| **L1** | **Regex (Deterministic)** | 0 | Always (Baseline) |
| **L2** | **Gemini 2.0 Flash Lite (LLM)** | 0 (Free Tier) | L1 Confidence < 75% |
| **L3** | **Claude 3.5 Sonnet / Multi-Expert** | Paid | Optional High-Precision Escalation |

### 1.2 L1: Regex & Pattern Scoring

L1 calculates a confidence score based on keyword density and input length.

- **Pattern Match**: Every matched regex in `encoding.py` increases the score.
- **Length Bonus**: Longer, more detailed inputs receive up to a 20% bonus.
- **Decision**: If the resulting confidence is ≥ 75%, L1's observation index is used immediately.

### 1.3 L2: Gemini-Based Self-Evaluation

L2 uses the **Gemini 2.0 Flash Lite** free tier API via the `google-genai` package for high-speed, cost-effective evaluation.

- **Implementation**: Managed via `llm_evaluator.py` using `google-genai` Client REST API.
- **Prompting**: The LLM is asked to score `context_clarity`, `urgency`, and `confidence` on a 0.0-1.0 scale.
- **Discretization**: These scores are then mapped back to the discrete indices (0, 1, 2) required by the `pymdp` A-matrix.
- **Fallback**: If L2 confidence is also low, the system provides a "Hollow Detection" warning.

---

## 2. Advanced FEP Agent Capabilities

### 2.1 2-Step Policy Horizon (`policy_len=2`)

The agent evaluates policies over a depth of 2 future timesteps. This allows for:

- **Lookahead**: Considering how an 'Observe' action now might enable a high-utility 'Act' action in the next step.
- **Stability**: Prevents short-sighted "greedy" actions when epistemic (information-seeking) value is still high.

### 2.2 Dirichlet Learning & Persistence

Learning is persistent across sessions, allowing the agent to adapt its observation model ($A$-matrix) to the user's specific style and domain.

- **Concentration Update**: `pA += η * outer(observation, beliefs)`.
- **Learning Rate**: $\eta = 50.0$ (calibrated for steady adaptation).
- **Persistence**:
  - **Save**: Automated during the `/bye` workflow to `mneme/.hegemonikon/learned_A.npy`.
  - **Load**: Automated during the `/boot` workflow.

---

## 3. FEP Bridge: Workflow Integration

The `fep_bridge.py` module provides a high-level API for workflows to consume FEP insights.

### 3.1 O1 Noēsis Integration (`noesis_analyze`)

Returns a `NoesisResult` containing:

- **Belief Entropy**: Measure of uncertainty.
- **Confidence**: $1.0 - \text{normalized\_entropy}$.
- **MAP State**: The most likely hidden state configuration (Phantasia, Assent, Horme).

### 3.2 O2 Boulēsis Integration (`boulesis_analyze`)

Returns a `BoulesisResult` containing:

- **Policy Probabilities**: Distribution over 'Observe' vs. 'Act'.
- **EFE Values**: Expected Free Energy for each policy.
- **Interpretation**: Human-readable recommendation.

### 3.3 Visual Feedback

The `generate_fep_feedback_markdown()` function creates a structured visual block (using ANSI-style borders) for inclusions in the session logs, making the AI's "internal state" transparent to the user.

---

## 4. Operational Summary

| Module | Responsibility |
| :--- | :--- |
| `fep_agent.py` | Implementation of Agent with `policy_len=2` and Dirichlet updates. |
| `persistence.py` | File I/O for NumPy matrices in `mneme/`. |
| `llm_evaluator.py` | Hierarchical escalation logic (L1/L2/L3). |
| `fep_bridge.py` | Integration layer for `/noe` and `/bou`. |

**Status**: 100% Verified. Full hierarchical evaluation and session persistence achieved. Integrated into `/boot`, `/bye`, `/noe`, and `/bou` workflows as of Jan 28, 2026.
