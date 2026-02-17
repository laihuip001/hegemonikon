# Protocol: Context Engineering (CE) & Information Absorption

## 1. Core Philosophy

> **"Instruction Quality < Background Information Quality"**

Hegemonikón prioritizes the quality and density of background context over the complexity of the command itself. High-precision intelligence (Noēsis) is a function of the agent's ability to "absorb" the environment before executing the task.

## 2. The 3x Rule

For high-precision technical generation (Skills, Workflows, Code), the volume of background information should be approximately **3 times** the size of the specific task instruction.

- **Instruction**: What to do.
- **Background**: Why to do it, how it fits into the system, past failures (Wargame-DB), and implicit constraints.

## 3. Implicit Knowledge Extraction

Agents must actively identify "Shadow Context"—information the Creator considers "obvious" but has not explicitly typed out.

### 3.1. Extraction Checklist

1. **Domain Premise**: What are the silent "laws" of this specific task?
2. **Hidden Agenda**: Is there a meta-goal (e.g., "make it look professional," "ensure it's future-proof")?
3. **Lineage**: How does this task relate to previous Handoffs or Knowledge Items?

## 4. Preventing "Agent Completion" (Manual Generation)

LLM agents (Gemini, Jules) have a natural tendency to "complete" or "infer" missing details. In safety-critical or high-precision manual generation, this is a defect.

### 4.1. Granularity Rules for Manuals

To prevent hallucinations, manuals must use a **Zero-Compression** approach:

| Rule | Requirement |
| :--- | :--- |
| **Line-Level Addressing** | Never say "Update the table." Say "Update rows 58-64." |
| **Exact Copy-Paste** | Always provide the full, exact block to be added/replaced. No "etc." or "...". |
| **Before/After Assertions** | Explicitly state the state change: "Old Value [X] -> New Value [Y]". |
| **Negative Constraints** | Specifically list what NOT to do (e.g., "Do not change column order"). |

## 5. Drift Detection & Periodic Refresh

Initial intent (Boulēsis) decays during deep reasoning loops.

- **Protocol**: If the reasoning trace exceeds 15 steps, the agent must perform a **Re-alignment Audit**: "Does this path still minimize the error of the *original* purpose?"
- **Refresh**: Re-inject the Hub-level goal into the context window if drift > 20% is detected.

---
*Created: 2026-02-06. Integrated into /mek v7.0 (Step 1.5: Information Absorption Layer).*
