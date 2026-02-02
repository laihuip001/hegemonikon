# FEP Research & Governance Compendium

> **Revision**: 28 Jan 2026
> **Scope**: Quantified behavioral patterns, governance decisions, and design rationale for the Hegemonikón FEP Layer.

---

## 1. Governance & Integration Status

The Hegemonikón FEP agent has reached production stability with the following enhancements:

- **2-step Policy Horizon**: `policy_len=2` is default, enable deeper deliberation.
- **Dirichlet learning**: `update_A_dirichlet()` implemented for model adaptation.
- **Persistence Layer**: Automated save/load of learned A-matrix.
- **Verification**: 100% of functional tests (56/56) passed.

### 1.1 The Overconfidence Problem (Metacognition)

**Finding**: LLM self-evaluation of confidence is inherently unreliable due to overconfidence bias.
**Mitigation**:

- **Hybrid Observation**: Combine LLM self-evaluation with external metrics (file counts, errors, time).
- **Configurable Thresholds**: Move from hardcoded triggers to adaptable entropy thresholds.
- **User Override**: Automatic Epochē must include a user "ignore" or "consult" option.

### 1.2 Learning & Persistence

Learning only manifests as behavioral change when the *ratio* between concentration parameters shifts significantly. Convergence on new models typically requires 50-100 consistent trials.

---

## 2. Empirical Research Findings

### 2.1 The Five Laws of FEP Policy Selection

Based on experimental validation using the complete inference cycle, the following behavioral patterns were established:

| Law | Observation | Policy Result | Insight |
| :--- | :--- | :--- | :--- |
| **Law 1: Context Bias** | Clear Context | **Act (Energeia)** ~77% | EFE favors execution when phantasia is clear. |
| **Law 2: Epochē** | Low Conf + Ambiguous | **Observe (Noēsis)** ~69% | Formal implementation of judgment suspension. |
| **Law 3: Urgency** | High Urgency | **Act (Energeia)** ~59% | High urgency reduces epistemic precision. |
| **Law 4: Equilibrium** | High Conf + Ambiguous | Balanced (52/48) | Ambiguity maintains caution regardless of confidence. |
| **Law 5: Persistence** | Learning accumulation | Logarithmic shift | Model shifts require significant evidence (50+ trials). |

### 2.2 Operational Metrics: Entropy as Decision Gate

 Belief entropy ($H(Q)$) provides a quantitative measure of cognitive stability:

| State | Metric (Entropy) | Decision / Action |
| :--- | :--- | :--- |
| **High Certainty** | $H(Q) < 1.7$ | Proceed to Assent and execution. |
| **Ambiguity** | $1.7 \le H(Q) < 2.0$ | Caution; flag "Uncertain Conclusion". |
| **Max Confusion** | $H(Q) \ge 2.02$ | **Epochē** (Trigger judgment suspension). |

---

## 3. Matrix Design Guide (Rationale)

### 3.1 State Factors (The Soul)

- **Phantasia**: `clear` | `uncertain`
- **Assent**: `granted` | `withheld` (Epochē)
- **Horme**: `active` | `passive`

### 3.2 Transition Logic (B Matrix)

- **Action: Observe (/noe)**:
  - Epistemic Drive: 60% transition from `uncertain` to `clear`.
  - Cognitive Calm: 70% transition to `withheld` (Assent) and `passive` (Horme).
- **Action: Act (/ene)**:
  - Commitment: 70% transition to `granted`.
  - Activation: 80% transition to `active`.

---

## 5. Cross-Validation & Parameter Reliability

To move beyond intuitive defaults, the FEP parameters were cross-validated against three independent sources in Jan 2026.

### 5.1 Sources & Findings

- **pymdp Tutorial 2**: Confirmed `p_hint=0.7`, `p_reward=0.8` (Likelihood) and preference vectors ($C[Loss]=-4.0, C[Reward]=+2.0$). Validated the use of $\gamma=16.0$ for policy precision.
- **Gijsen et al. (2022)**: Confirmed the use of preference precision ($\lambda$) and inverse temperature ($\gamma$) in decision making.
- **Da Costa et al. (2020)**: Validated the Dirichlet update rule (Eq. 21) for likelihood learning, confirming the $\alpha=1.0$ concentration parameter as a starting point.

### 5.2 Confidence Level: High

With convergence across academic packages (pymdp) and original research papers, the parameter database (`parameters.yaml`) has been upgraded from "Medium-High" to **"High"** confidence.

---
*Derived files (Consolidated): fep_integration_governance.md, fep_empirical_research_compendium.md, fep_matrix_design_guide.md, noe_fep_integration_analysis.md, active_inference_parameter_research.md*
