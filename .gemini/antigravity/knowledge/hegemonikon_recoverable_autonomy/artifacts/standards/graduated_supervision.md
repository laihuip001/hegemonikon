# Graduated Supervision Specification

## 1. Overview

**Graduated Supervision** (derived 2026-01-31) is a reliability pattern that scales the intensity of agent monitoring based on the inherent risk of the operation. It balances the need for autonomy with the requirement for robust oversight.

## 2. Supervision Levels

| Risk Level | Supervision Mode | Strategy | Trigger Macro |
| :--- | :--- | :--- | :--- |
| 🟢 **Low** | **Self-Supervision** | Internal reflection via `/dia`. | `@selfcheck` |
| 🟡 **Medium** | **Joint Supervision** | Self-reflection + Premortem failure analysis (`/pre`). | `@premortem` |
| 🔴 **High** | **External Supervision** | Mandatory review by a "Council" of agents (`/syn`) or human approval. | `@council` |

## 3. The Supervision Matrix

- **Self-Supervision**: The agent critiques its own plan before execution.
- **Premortem**: The agent explicitly envisions a scenario where the task failed and identifies the causes beforehand.
- **Council/Supervisor**: A higher reasoning model (Supervisor) audits the entire logic chain.

## 4. Integration with Risk Tags

The supervision level is automatically selected based on the `risk_tags.yaml` classification of the tools and operations involved in the task.

---
*Created: 2026-01-31 | v7.5 Strategic Alignment*
