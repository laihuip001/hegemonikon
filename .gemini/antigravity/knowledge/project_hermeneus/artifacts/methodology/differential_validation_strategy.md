# Methodology: Differential Validation Strategy (A/B Testing)

## 1. Objective

To quantitatively and qualitatively assess the effectiveness of the Hermēneus MCP integration by comparing autonomous CCL execution against standard manual LLM execution.

## 2. Experimental Design (A/B Test Model)

A controlled study is conducted using the following groups:

### Group A: Baseline (Control)

- **Execution Mode**: Manual LLM interpretation of CCL.
- **Workflow**:
    1. Agent receives CCL.
    2. Agent interprets and executes steps without Hermēneus tools.
    3. No verified multi-agent debate or audit trail.

### Group B: Hermēneus (Treatment)

- **Execution Mode**: Autonomous Hermēneus execution via MCP.
- **Workflow**:
    1. Agent calls `hermeneus_execute`.
    2. Hermēneus compiles CCL to LMQL.
    3. Execution occurs through the verified pipeline.
    4. Multi-Agent Debate (`verifier.py`) produces a confidence score and verdict.

## 3. Key Metrics

- **Quality Score (0-10)**: Holistic assessment of output depth, correctness, and adherence to Hegemonikón standards.
- **Consistency**: Variation in output across multiple runs of the same CCL command.
- **Reproducibility**: Ability to recreate the same cognitive result in a different session.
- **Verification Rate**: Percentage of tasks that achieve a "CONSENSUS" verdict in the debate engine.

## 4. Test Protocol (CCL-Driven)

The test is orchestrated using a dedicated CCL program:
`[hermeneus]@zet+ >> /mek.model >> /sta+ >> /ene+`

1. **Discovery (`/zet+`)**: Identify critical edge cases for CCL processing.
2. **Modeling (`/mek.model`)**: Define the A/B variables and logging paths.
3. **Criteria (`/sta+`)**: Set target success thresholds (e.g., Quality >= Baseline + 1.0).
4. **Execution (`/ene+`)**: Run 5 standardized test cases (`/noe+`, `/bou+`, `/s+`, etc.) 3 times each for both groups.

## 5. Significance

This strategy marks the shift from **subjective trust** to **empirical verification** of the AI's autonomous capabilities. It ensures that the "Self-Integrated Cognitive Loop" actually provides superior results compared to manual operation.

---
*Origin: 2026-02-01 | Hermēneus Phase 7 Methodology*
