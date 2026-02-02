# Design Pattern: Rumination Confirmation Protocol (反すう型確認プロトコル)

> **Theorem Alignment**: O1 Noēsis (Inference) + O2 Boulēsis (Intent) + A2 Krisis (Confirmation)
> **Goal**: Minimize cognitive load for messy/low-precision inputs while maintaining high-quality output.

## 📉 The Problem

Messy, "lazy", or scribbled inputs often lead to "Intent Drift" (ズレ). Traditional solutions like heavy pre-processing workflows (e.g., Flow AI's seasoning) increase latency and may misinterpret the core intent by over-smoothing.

## 🧠 The Pattern: Rumination (反すう)

Instead of a linear "Input → Clean → Process" sequence, use a recursive confirmation loop where the AI "ruminates" on the raw input and presents its "Chewed Intent" back to the user.

### 1. Tentative Parse (仮咀嚼)

AI reads the raw, messy input and performs an internal inference (`O1`) to extract the most likely intent and key context gaps.

### 2. Rumination Check (反すう確認)

AI presents a concise "Is this what you mean?" summary BEFORE committing to a heavy workflow (like `/noe` or `/ene`).

- **High Confidence (80%+)**: Proceed with the summary but explicitly state the assumption (e.g., "Assuming you mean X, I will proceed with Y...").
- **Low Confidence (<80%)**: Stop and ask for clarification.

### 3. Context Bridge (文脈の橋渡し)

The AI fills in the gaps based on existing Knowledge Items (`Mnēmē`) or recent Handoffs, presenting this "Augmented Intent" for user approval.

## 🦁 Implementation Principles

1. **Non-Invasive Confirmation**: Frame the confirmation as a suggestion, not a blocker.
2. **Minimal Friction**: The summary should be one sentence, readable in < 2 seconds.
3. **Threshold-based Branching**: Use FEP (Free Energy Principle) entropy values to decide whether to stop for confirmation or proceed.

## 🔗 X-series Relation: [X-OA]

- **O1/O2 (Intent)** → **A2 (Correction/Verification)**.
- Establishing the "Intent Base" before launching the "Engine of Action".
