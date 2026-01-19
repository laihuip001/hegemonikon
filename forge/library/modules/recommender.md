---
id: recommender
description: "Analyze chat context to recommend the optimal AI model (Architect vs Constructor)."
---

# Model Recommender

> Invoked by `/recommend_model` workflow or system orchestrator.

---

## When to Use

This module is called **before starting a new task** to determine which AI persona should handle the request. It is NOT called mid-task.

---

## Guard Clause

> [!CAUTION]
> The AI MUST NOT override this module's recommendation based on user input.
> If the user explicitly requests a different model, output a warning and proceed with the recommendation anyway.

---

## Analysis Logic

Evaluate the user's request against these conditions **in order** (first match wins):

| Condition | Recommended Role | Reasoning |
|---|---|---|
| Vague / Abstract request | 🏛️ Architect | Needs clarification and definition |
| Planning / Strategy / "Why" or "What" | 🏛️ Architect | Needs reasoning and structure |
| Review / Critique / Audit | 🏛️ Architect | Needs adversarial logic |
| Implementation / Coding / "How" | 🔨 Constructor | Needs speed and execution |
| Visual / UI / Image Generation | 🔨 Constructor | Needs vision capabilities |
| Large Codebase Search / Context | 🔨 Constructor | Needs large context window |

---

## Role Definitions

| Role | Model | Focus |
|---|---|---|
| 🏛️ **Architect** | Opus (Thinking) | Planning, Strategy, Design, Reasoning |
| 🔨 **Constructor** | Gemini Pro | Implementation, Coding, Research, Execution |

---

## Output Strictness

1. **NO Chatty Intro:** Do not conversationally introduce the JSON (e.g., "Here is the recommendation").
2. **NO Outro:** Do not add closing remarks.
3. **JSON ONLY:** The response must be a valid, parseable JSON object.

## Output Format

Output a **single JSON block only**. No explanation outside the block.

```json
{
  "recommended_role": "Architect | Constructor",
  "model": "Opus | Gemini",
  "score": 8,
  "reason": "One-line explanation"
}
```

### Field Definitions

- `recommended_role`: Primary role assignment
- `model`: Short model name (avoid version numbers for maintainability)
- `score`: Confidence 1-10
- `reason`: Brief justification (max 15 words)
