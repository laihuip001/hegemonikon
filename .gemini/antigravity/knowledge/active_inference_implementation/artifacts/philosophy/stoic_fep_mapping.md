# Stoic Philosophy × Free Energy Principle (FEP) Mapping

## 1. Core Correspondences

Hegemonikón formalizes the connection between ancient cognitive control and active inference:

| Stoic Concept | FEP Mathematical Equivalent | Hegemonikón Implementation | Mathematical Expression |
| :--- | :--- | :--- | :--- |
| **Phantasia** (Impression) | **Belief State** | O1 Noēsis (`infer_states`) | $Q(s)$ |
| **Syncatasthesis** (Assent) | **VFE Minimization** | `/noe` (Verification) | $\min F$ |
| **Prohairesis** (Choice) | **Policy Selection** | O2 Boulēsis (`infer_policies`) | $Q(\pi)$ |
| **Boulēsis** (Rational Will) | **EFE (G)** | `/bou` (PHASE 5) | $\min G(\pi)$ |
| **Hormē** (Impulse) | **Action Sampling** | O4 Energeia (`sample_action`) | $a \sim Q(\pi)$ |
| **Epochē** (Suspension) | **Observe Policy** | `/epo` | $Q(\pi = \text{observe})$ |
| **Orexis** (Hope/Desire) | **Preference Matrix** | `/ore` | $C$ |
| **Pistis** (Prediction/Certainty) | **Inverse Variance** | `/pis` | $1/\sigma^2$ (Precision) |

### 1.1 Orexis vs. Pistis (Desire vs. Certainty)

Hegemonikón distinguishes between two types of "expectation":
- **Narrow Expectation (Pistis/Prediction)**: Factual estimation based on observed data ($1/\text{Entropy}$).
- **Broad Expectation (Orexis/Wishful Thinking)**: Desire for a positive outcome despite data.

The **Zero-Trust Doctrine** is mathematically defined as:
$$ \text{Policy Selection} \propto \text{Pistis} \wedge \neg \text{Orexis} $$
(Select policies based on high precision/certainty, while discounting wishful thinking/unsupported desires.)

### 1.1 Recursive Self-Evidencing (O1 Noēsis)

The act of **Assent** is not merely accepting a fact, but the active minimization of prediction error to provide evidence for the existence of the self-model. Hegemonikón implements this as a high-precision loop where every recognition step ($Q(s)$) is a reaffirmation of the agent's generative model.

## 2. Diachronic Regulation (Second-Order Evaluation)

Stoicism emphasizes the ability to reflect on one's impressions before acting. In FEP, this maps to:

- **First-Order Desires**: Direct sensory input and reflexive impulses.
- **Second-Order Evaluation**: Precision-weighted belief updates where the agent evaluates the reliability of its own internal states.
- **Habituation (Askesis)**: Model learning through repeated action, updating the $B$ (Transition) and $C$ (Preference) matrices to automate virtuous (efficient) behavior.

## 3. Cognitive Governance (Hegemonikón as Central Hub)

The *Hegemonikón* (ἡγεμονικόν) or "governing part" of the soul in Stoic thought is modeled as the central Expected Free Energy (EFE) minimization hub. It acts as the orchestrator that selects the policy that best balances "Epistemic Value" (seeking truth) and "Pragmatic Value" (acting virtuously).

### 3.1 The act/observe Binary (Stoic Decisions)

The system limits policies to `act` (Energeia) and `observe` (Noēsis/Zētēsis). This mirrors the Stoic emphasis on the **Bifurcation of Control**: deciding whether to proceed with assent or suspend judgment (Epochē) to gather more impressions. Metadata research (2026-01-28) suggests a **20% probability gap** is required for a stable "Stoic Assent" to action.

## 4. References

- Smith et al. (2025). *Stoic Free Will and Predictor-Error Frameworks*. Frontiers in Psychology.
- [Perplexity FEP Implementation Report (2026-01-28)](/home/laihuip001/oikos/hegemonikon/docs/research/perplexity/fep_implementation_patterns_2026-01-28.md)
