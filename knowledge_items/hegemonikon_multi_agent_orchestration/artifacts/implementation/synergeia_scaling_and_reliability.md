# Synergeia: Scaling and Reliability Patterns

## 1. Overview

Synergeia's reliability and performance are driven by the strategic allocation of "Test-Time Compute" (repeated sampling) and the dialectical synthesis of multi-agent perspectives. This document consolidates the mathematical scaling laws and operational protocols used to maximize accuracy while optimizing cost.

## 2. Inference Scaling: The "Large Language Monkeys" Pattern

Based on arXiv:2407.21787, LLM performance (coverage) follows a predictable scaling law when increasing repeated sampling ($k$).

### 2.1. The Scaling Law

$$c \approx \exp(a \cdot k^{-b})$$

- **$c$ (Coverage)**: Probability that at least one of $k$ samples contains the correct answer.
- **$k$ (Sample Count)**: Number of parallel generations.
- **$a, b$ (Model Parameters)**: Specific to the model family. Discovery: Models of different sizes within the same family exhibit parallel S-curves (same slope $b$, different offset $a$).

### 2.2. Variance-Adaptive Sampling (Entropy-Based)

To balance cost and coverage, Synergeia employs a dynamic compute allocation strategy:

1. **Initial Sampling ($N_{min}$)**: Generate a baseline set of samples (e.g., $N=3$ to 5).
2. **Entropy Measurement**: Calculate the agreement among answers.
   - **Low Entropy (Consensus)**: If the first $k$ samples agree, **Exit Early** to conserve compute.
   - **High Entropy (Disagreement)**: If answers are diverse, **Expand Sampling** (e.g., recursive expansion to $N=11$, 21, or 100).
3. **Consensus Aggregation**: Utilize majority voting or a dedicated **Reward Model (Verifier)** to select the final output.

### 2.3. Implementation Logic (Adaptive Sampling)

```python
def adaptive_sample(task, min_n=3, max_n=21, threshold=0.1):
    """
    Dynamically adjusts sample count based on response entropy.
    """
    samples = call_llm(task, n=min_n)
    # Calculate Shannon entropy (or simple agreement ratio)
    entropy = calculate_entropy(samples)

    if entropy > threshold:
        # Recursive expansion for difficult tasks
        additional_samples = call_llm(task, n=max_n - min_n)
        samples.extend(additional_samples)

    return aggregate(samples)
```

## 3. Dialectical Reliability: ReConcile (Round-Table Conference)

Instead of a single-turn majority vote, complex reasoning tasks utilize a multi-turn convergence protocol (arXiv:2309.13007).

### 3.1. The 3-Step Convergence Algorithm

1. **Step 1: Independent Generation**: Multiple diverse specialists (Gemini, Claude, GPT) generate initial answers with explicit reasoning chains.
2. **Step 2: Mutual Reference and Correction**: Specialists review each other's reasoning and refine their own answers, attaching a **Confidence Score** (0-100).
3. **Step 3: Convergence Check**:
   - If consensus is reached -> **Finalize Result**.
   - If consensus fails after $R$ rounds -> **Abstain (棄権)**.

### 3.2. Confidence-Based Abstention

Specialists are empowered to say "I don't know" to prevent "confidently wrong" hallucinations.

- **Threshold-Based**: If `confidence < 50`, the response is flagged as `abstained`.
- **Impact**: Preemptively prunes hallucinations from the majority vote, significantly increasing system-wide precision.

### 3.3. Implementation Logic (Abstention)

```python
def process_specialist_response(response: dict, threshold: int = 50) -> dict:
    """
    Flags responses as abstained if confidence falls below the threshold.
    """
    if response.get("confidence", 100) < threshold:
        return {
            "answer": None,
            "status": "abstained",
            "reason": f"Confidence {response['confidence']}% below threshold {threshold}%"
        }
    return response

def aggregate_with_abstention(responses: list[dict]):
    """
    Weighted voting only among non-abstained responses.
    """
    valid_responses = [r for r in responses if r.get("status") != "abstained"]
    if not valid_responses:
        return {"status": "all_abstained", "recommendation": "Manual Audit Required"}

    # Weighted vote based on self-reported confidence
    votes = {}
    for r in valid_responses:
        ans = r["answer"]
        votes[ans] = votes.get(ans, 0) + (r.get("confidence", 50) / 100)
    return max(votes, key=votes.get)
```

## 4. Best-of-∞: Asymptotic Performance

The "Best-of-∞" limit (arXiv:2509.21091) confirms that test-time compute can compensate for model size. Weak, cheaper models (e.g., DeepSeek, Llama-3-70B) with high $k$ (e.g., $k=1000$) can match or exceed the zero-shot performance of elite models like GPT-4o for tasks with automated verifiers (compilers, test runners).

## 5. Implementation Summary

| Metric | Pattern | Technical Requirement |
| :--- | :--- | :--- |
| **Coverage** | Repeated Sampling | Scale $k$ up to the selection bottleneck (~100 samples). |
| **Efficiency** | Adaptive Early Exit | Shannon Entropy calculation on response vectors. |
| **Precision** | Abstention | Self-consistency checks and mutual review (ReConcile). |
| **Verification** | Automated RAG | Use compilers/test-runners as absolute reward markers. |

---
*Updated: 2026-02-06. Consolidated: adaptive_sampling_patterns.md, synergeia_optimization_best_of_infinity.md, reconcile_abstention_protocol.md.*
*Lineage: arXiv:2407.21787, arXiv:2309.13007, arXiv:2509.21091.*
