# Agent Supervisor Model Specification

## 1. Overview

The **Agent Supervisor Model** (derived 2026-01-31) provides a multi-layered oversight structure for agent operations. It shifts from a single-agent autonomous model to a supervised model where oversight intensity scales with operational risk.

## 2. Graduated Supervision Pattern

Supervision protocols are selected based on the `risk_tags.yaml` classification of the task.

| Risk Level | Supervision Mode | Strategy | Trigger Macro |
| :--- | :--- | :--- | :--- |
| 🟢 **Low** | **Self-Supervision** | Internal reflection and self-correction via `/dia`. | `@selfcheck` |
| 🟡 **Medium** | **Joint Supervision** | Self-reflection + Premortem failure analysis via `/pre`. | `@premortem` |
| 🔴 **High** | **External Supervision** | Mandatory audit by a "Council" of agents (`/syn`) or external API (Jules). | `@council` |

## 3. The Supervisor's Role

- **Oversight**: Auditing the reasoning chain (CCL) before execution.
- **Validation**: Comparing output against defined Guardrails.
- **Decision Persistence**: Ensuring that the reasoning behind safety decisions is logged in Doxa.

## 4. Operational Flow

1. **Risk Evaluation**: The agent identifies the risk level of the intent.
2. **Supervision Mode Selection**: The appropriate `@supervise` macro is applied.
3. **Audit/Correction**: The supervisor (internal or external) provides feedback.
4. **Final Approval**: Operation proceeds only after the supervision gate is passed.

---
*Created: 2026-01-31 | v7.5 Strategic Alignment*
