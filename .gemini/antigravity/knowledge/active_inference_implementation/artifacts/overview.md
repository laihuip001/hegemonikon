# Active Inference & FEP Technical Implementation

## 1. Overview

The **Free Energy Principle (FEP)** and **Active Inference** provide the mathematical foundation for self-organizing systems that minimize variational free energy to maintain their existence. In AI agents, this translates to treating perception as inference and action as the minimization of expected free energy.

> **Core Insight (2026-01-31)**: Hegemonikón は「Creator の認知を FEP 的に外在化・最適化するシミュレーション環境」である。思考の連鎖を記号化し、予測誤差最小化を通じて最適な認知パスを発見する。

## 2. Core Libraries & Frameworks

### 2.1 pymdp (Python)

The primary library for discrete state-space Active Inference (POMDP).

- **Status**: v0.0.1 (Verified 2026-01-29), v1.0.0-alpha (JAX Backend)
- **Key Classes**:
  - `Agent`: Manages matrices A (Likelihood), B (Transition), C (Preferences), D (Initial Beliefs).
- **Core Workflow**:

    ```python
    agent = Agent(A=A, B=B, C=C, D=D)
    qs = agent.infer_states(observation)  # Variational Inference
    q_pi, neg_efe = agent.infer_policies()  # Expected Free Energy Minimization
    action = agent.sample_action()  # Action selection
    ```

### 2.2 ActiveInference.jl (Julia)

High-performance implementation for researchers, interacting with the SPM (Statistical Parametric Mapping) ecosystem.

## 3. Mathematical Foundations

### 3.1 Variational Free Energy (VFE)

The objective function for perception/learning:
$$F = D_{KL}[q(s)||p(s|o)] - \ln p(o)$$
Minimizing $F$ is equivalent to maximizing the Evidence Lower Bound (ELBO).

### 3.2 Expected Free Energy (EFE)

The objective function for policy selection (future-oriented):
$$G(\pi) \approx \text{Epistemic Value} + \text{Pragmatic Value}$$

- **Epistemic Value**: Information gain / Uncertainty reduction.
- **Pragmatic Value**: Utility / Preference fulfillment.

## 4. Implementation Patterns

### 4.1 Belief Updating & Learning

- **Mean-Field Approximation**: Factoring the posterior into independent distributions for efficiency.
- **Dirichlet learning**: Updating concentration parameters ($pA$) of the likelihood matrix based on experience ($\eta = 50.0$).

### 4.2 Planning & Decision Making

- **2-step Policy Horizon**: Optimized EFE evaluation over a depth of 2 timesteps for anticipatory planning.
- **Thompson Sampling**: Sampling from the posterior for exploration-exploitation balance.

### 4.3 Hierarchical Hybrid Evaluation

To map high-dimensional natural language to discrete observation indices efficiently:

- **L1 (Regex)**: Zero-cost pattern matching with confidence scoring.
- **L2 (Gemini)**: Free-tier semantic self-evaluation for uncertain cases.
- **L3 (Fallback)**: High-fidelity model validation (Claude/GPT).

### 4.4 Multi-LLM Active Inference (Neural Rendering)

A sophisticated pattern (formalized in arXiv:2412.10425) where Active Inference manages the high-level cognitive "decisions" of LLM-based agents.

- **Persistence**: Session-to-session persistence of learned models via NumPy serialization in `mneme/`.
- **FEP Bridge**: Abstracted interface for workflow integration (`/noe`, `/bou`).

See:

- `artifacts/implementation/observation_mapping.md`
- `artifacts/implementation/hierarchical_evaluation_and_bridge.md`
- `artifacts/research/fep_practical_laws.md`

## 5. Stoic Philosophy Correspondence

The mapping between Stoic cognitive stages and Active Inference:

| Stoic Concept | FEP/Active Inference equivalent | Hegemonikón Implementation | Cognitive Role |
| :--- | :--- | :--- | :--- |
| **Phantasia** | Prior belief $P(s)$ / Likelihood $P(o\|s)$ | `llm_evaluator.py` | Perception |
| **Assent** | Belief update / Posterior $Q(s)$ | `Agent.infer_states()` | Belief Update |
| **Zētēsis (O3)** | Active Inquiry / Policy Selection (**Act**) | `/zet` | Question/Discovery |
| **Sophia (K4)** | Information Retrieval / Observation (**Observe**) | `/sop` | Data Collection |
| **Hormē** | Action selection $\pi^* \in \Pi$ | `Agent.sample_action()` | Execution |
| **Prohairesis** | Policy selection minimizing $G(\pi)$ | `fep_bridge.py` | Deliberation |

## 6. References

- [arXiv:1705.09156] The free energy principle for action and perception: A mathematical review
- [Journal of Open Source Software] pymdp: A Python library for active inference
- [arXiv:2412.10425] Active Inference for Self-Organizing Multi-LLM Systems
- [PhilArchive: BORAHI] The STOIC Architecture
- [Hegemonikón 2026-01-28] Synedrion Swarm Audit Analysis
