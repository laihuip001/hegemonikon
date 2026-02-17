# Behavioral Protocols: Quality and Reliability Standards

## 1. Overview

To maintain high-fidelity intelligence and minimize technical debt (Prediction Error), Hegemonikón enforces rigorous standards for prompt engineering, RAG retrieval, skill design, and knowledge digestion.

### 2.1. Reasoning Model (o3, R1) Weaknesses (arXiv:2511.05874)

Reasoning capacity does not guarantee correctness if requirements coverage is non-exhaustive.

- **The Completeness Gap**: 44.5% of failures in reasoning models are due to **Incompleteness** (missing requirements) rather than logic.
- **Edge Case Volatility**: 32.17% of failures occur because edge cases (empty files, huge data, network timeouts) were not addressed in the "Thought" trace.
- **Scaling Paradox**: Longer thinking traces do NOT always correlate with higher success; precision in initial requirement parsing determines the outcome.
- **Mitigation**: Implement **MetaRAG** (Monitoring-Evaluation-Planning) loops to prune irrelevant branches and force re-evaluation of missing requirements (arXiv:2402.11626).

### 2.2. Instruction Density and Degradation (arXiv:2507.11538)

Hegemonikón respects the "Instruction Horizon" to avoid silent omissions.

- **Thresholds**: Performance remains stable up to ~150-250 instructions for elite agents (o3, Gemini 2.0 Pro), after which omission rates rise.
- **Degradation Types**:
  - **Threshold (S-Curve)**: Models like o3/Gemini-Thinking stay perfect until a breaking point.
  - **Linear**: Gradual decline (Claude 3.7, GPT-4).
  - **Exponential**: Immediate failure (Haiku, Llama-Scout).
- **Error Pattern**: **Omission** is 35x more common than **Change**. Agents simply drop instructions rather than attempting to merge or modify them.
- **Protocol**: Critical instructions MUST reside in the first 150 items of the prompt (Primacy Effect).

### 2.3. Plan Entropy and Goal Refreshing (arXiv:2410.12409)

As task complexity and planning steps increase, agents lose sight of the initial **Telos**.

- **Goal Drift**: The influence of the initial prompt diminishes exponentially as the agent enters deep reasoning loops or multi-step tool calls.
- **Protocol (Goal Refresh)**:
  1. **N-Step Re-injection**: Explicitly append the original goal to the prompt every 5 steps.
  2. **Mandatory Progress Verification**: Every 3 steps, the agent must output a "Current Status vs. Goal" alignment check in the Working Memory.
  3. **Constraint Persistence**: Re-state critical safety/formatting constraints alongside the goal re-injection.

## 3. RAG Reliability: The 19 Defect Patterns

Most RAG systems (98% in study) fail due to predictable structural flaws:

### 3.1. Case Study: Hegemonikón Internal Audit Reflection

An internal audit of Gnōsis/AIDB against these patterns (2026-02-06) identified that the framework currently possesses multiple risks:

- **Major Risk (#10)**: Lack of validated Japanese-specific embedding quality for specialized documentation.
- **Major Risk (#7)**: Absence of automated context-window truncation/summarization for long sessions.
- **Major Risk (#9)**: Knowledge gaps due to premium article paywalls in source databases (AIDB).
- **Search Modality Integrity (#20)**: Keyword/grep searches fail to capture semantic context, leading to "Search Error" (informational entropy). Vector search (Gnōsis) is mandated for all research/technical consultation.
- **Stance**: "Epistemic Humility" requires acknowledging these flaws and prioritizing internal knowledge ingestion (Chemotaxis) over speculative external searches.

## 4. Agent Skill Quality Gate

To prevent "Skill Fragility," every `SKILL.md` must pass a Quality Gate:

- **Output Contract**: Strict definition of the mandatory output structure (Headers, Metadata blocks).
- **Skill Policy**: Enforcement of Anthropic official constraints (Name < 64 chars).
- **Static Linting**: Automated checks for description precision and example compliance.

## 5. Unified Digestion: The White Blood Cell (WBC) Model

Hegemonikón distinguishes between **Searching** (Transient) and **Eating** (Naturalization).

### 5.1. The WBC Phagocytic Cycle

The system autonomously identifies un-digested content and integrates it:

- **L1 Chemotaxis**: Detecting un-digested markers in LanceDB or Jules PRs.
- **L2 Leukocyte**: Autonomous agents execute `/eat-` (ingestion) or `/vet` (audit) workflows.
- **L3 Antibody**: Updating system behavior (Skills/Theorems) based on findings.

## 6. Implementation Strategy

- **Chemotaxis Principle**: Internal knowledge (Gnōsis/AIDB) MUST be searched before external retrieval (Perplexity) to minimize surprise.
- **Naturalization Audit (/fit)**: Measuring if knowledge is "Alien" (external), "Superficial" (indexed), "Absorbed" (referenced), or "Naturalized" (built-in logic).

## 7. Context Engineering (CE) & Information Absorption

> **Principle**: Instruction Quality < Background Information Quality

Hegemonikón prioritizes the quality of background context over the complexity of the instruction itself. This is implemented as the **Information Absorption Layer** (STEP 1.5 in `/mek` v7.0).

- **Context Engineering (CE) Rules**:
  - **Implicit Knowledge Extraction**: Agents must identify what the Creator considers "obvious" but is not explicitly stated.
  - **Domain Assumption Analysis**: Identifying the silent premises of the target domain.
  - **Background Information Ratio (3x Rule)**: For high-precision generation, the background info tokens should be approximately 3 times the count of the instruction tokens.
  - **Drift Detection**: Recognizing when the implicit intent of a session shifts away from the stated goal.

---
*Consolidated: 2026-02-06. Sources: prompt_engineering_properties.md, rag_reliability_patterns.md, agent_skill_quality_gate.md, unified_digestion_protocol.md, context_engineering_principles.md.*
