# Agents and Memory: WBC and Structural Anamnesis

## 1. The White Blood Cell (WBC) Model

The **Auto-Digest Agent** (WBC model) is the immune system and metabolic engine of Hegemonikón's knowledge tier.

### 1.1. The Phagocytic Cycle

The agent autonomously identifies "foreign antigens" (raw research or logs) and naturalizes them into the system:

1. **Chemotaxis (Detection)**: Scanning LanceDB and AIDB for "Un-digested" markers.
2. **Phagocytosis (Ingestion)**: Sequestering target content for the `/eat-` workflow.
3. **Digestion (Analysis)**: Decomposing content into philosophical and technical atoms.
4. **Presentation (Integration)**: Updating Antibodies (Workflows/Theorems).

### 2.2. Implementation: The Mnēme Tier

Hegemonikón uses structured YAML/JSON files for persistent memory, managed via the `anamnesis/` CLI:

| File | Content Type | Role |
| :--- | :--- | :--- |
| **`persona.yaml`** | Semi-Structured | Relationship traits, trust scores, and emotional history. |
| **`patterns.yaml`** | Logical/Vector | Learned cognitive patterns and code motifs. |
| **`doxa_beliefs.json`** | Propositional | Formal constraints (Laws) and solidified theories. |
| **`values.json`** | Quantitative | Ethical and operational weights (Phronēsis). |
| **`learned_A.npy`** | Numerical | FEP A-matrix (likelihood) state. |

### 2.2. Implementation Logic (Mem0 / Anamnesis)

```python
def update_memory(existing_anamnesis: list[dict], new_facts: list[dict]):
    """
    Applies the tiered update protocol (ADD, UPDATE, DELETE, NOOP).
    """
    for fact in new_facts:
        matching = find_matching_item(existing_anamnesis, fact)
        
        if matching is None:
            # Fact not known, append to Anamnesis
            existing_anamnesis.append(fact) # ADD
        elif is_contradicting(matching, fact):
            # Fact has changed (e.g. user preference updated)
            update_item(matching, fact) # UPDATE
        elif is_obsolete(matching, fact):
            # Fact no longer relevant
            remove_item(matching) # DELETE
        else:
            # Redundant information
            pass # NOOP
    return existing_anamnesis
```

## 3. Implementation Strategy

- **Autonomous Background Audits**: The WBC agent performs periodic background scans of MNEME to update the ANAMNESIS/KI layer.
- **Temporal Tagging**: Every memory entry includes metadata for versioning and temporal resolution.
- **Relational Linking**: Graph-like relationships extracted by the WBC are stored as cross-referenced Knowledge Items (KIs).

## 4. Cognitive Frameworks: BDI and Theory of Mind

Hegemonikón's agentic behavior is structured around advanced cognitive models to ensure transparency, reliability, and social adaptability in multi-agent environments.

### 4.1. The BDI (Belief-Desire-Intention) Ontology

To solve the "Black Box" problem of agent reasoning, internal states are verbalized and structured using the BDI framework (arXiv:2412.01569):

- **Belief (Pistis)**: The agent's current understanding of the world state (facts, models).
- **Desire (Orexis)**: The agent's long-term objectives or teleological intent (Arche).
- **Intention (Doxa)**: The specific plan or commitment the agent is currently executing.

This mapping allows for high-fidelity debugging and **Mental State Verbalization**, enabling the system to answer competency questions (CQs) about its own choices.

### 4.2. Theory of Mind (ToM) / Hypothetical Minds

In multi-agent settings (Synedrion), agents employ the **ToM Cycle** (arXiv:2407.07086) to model peers and users:

1. **Hypothesis Generation**: Speculating on the strategies, goals, and hidden beliefs of other agents.
2. **Hypothesis Evaluation**: Measuring the predictive accuracy of these models based on observed behavior.
3. **Hypothesis Refinement**: Iteratively updating models to minimize "Social Surprise" (Prediction Error).

### 4.3. Metacognitive Prompting (MP)

To improve complex reasoning and self-regulation, the agent follows a 5-stage **Metacognitive Loop** (arXiv:2408.01391):

1. **Understanding**: Decomposing the query into core requirements.
2. **Provisional Judgment**: Generating an initial candidate response ($N=1$).
3. **Critical Evaluation**: Auditing the initial response for completeness and edge cases.
4. **Final Decision**: Synthesizing the refined output.
5. **Confidence Assessment**: Quantifying the reliability of the final result (see *Abstention Protocols*).

---
*Updated: 2026-02-06. Consolidated: auto_digest_agent_wbc.md, agent_memory_architectures.md, cognitive_frameworks_bdi_tom.md.*
*References: Mem0/Mem0g, BDI (arXiv:2412.01569), ToM (arXiv:2407.07086), MP (arXiv:2408.01391).*
