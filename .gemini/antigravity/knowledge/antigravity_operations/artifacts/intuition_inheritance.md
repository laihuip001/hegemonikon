# Intuition Inheritance (T8 & Persist)

## 1. Concept

**Intuition Inheritance** is the mechanism by which the Hegemonikón framework preserves the AI agent's "learned patterns," "value judgments," and "trust history" across session boundaries. This prevents the agent from reverting to a "blank slate" (tabula rasa) every time a new session starts.

## 2. Core Components (The T8 Triad)

The inheritance process relies on three primary files stored in the `mneme` layer:

| File | Hegemonikón Layer | Description |
| :--- | :--- | :--- |
| `patterns.yaml` | T3 Theōria | Learned technical patterns, naming conventions, and recurring design choices. |
| `values.json` | T4 Phronēsis | Subjective value functions, preference weights (e.g., Japanese-first, zero-entropy). |
| `trust_history.json` | T6 Praxis | Record of successful/failed judgments and decision confidence. |

## 3. Lifecycle

### 3.1 Inheritance (/boot v3.0 Phase 3)

At the start of every session, the `/boot` workflow executes the **Phase 3: 知識読込**. Step 8 specifically handles the loading of long-term memory.

**Output Format (Intuition Visualization)**:

```text
┌─[私の勘]────────────────────────────────────┐
│ 📐 Patterns (T3):                           │
│   • symploke-adapter-design (0.9)           │
│   • kernel-naming-convention (0.95)         │
│                                             │
│ ⚖️ Values (T4):                             │
│   • zero_entropy: 1.0                       │
│   • hyperengineering: 0.9                   │
│                                             │
│ 🤝 Trust (T6):                              │
│   • recent_success: H3 Symplokē (0.95)      │
└─────────────────────────────────────────────┘
```

### 3.2 Sophia Knowledge Summary (Phase 3 Step 6)

As of `/boot` v3.0, the inheritance loop includes a **Sophia Summary** phase in Phase 3. This explicitly retrieves recently ingested artifacts from the Sophia (KI) index to refresh the agent's working memory with the latest learned concepts, complementing the long-term T3/T4/T6 intuition files.

### 3.3 Update & Persistence (/bye Step 3.8)

Before a session ends, the `/bye` workflow evaluates if any new "intuition" has been gained. If so, it updates the T8 files.

**Triggers for Update**:

- Creator confirms a new development pattern is successful.
- A critical failure is analyzed and converted into a "warning pattern."
- Value priorities are adjusted during a `/u` (Opinion) or `/bou` (Boulēsis) dialogue.

### 3.3 Weekly Review Protocol (T8 Anamnēsis)

Beyond per-session inheritance, Hegemonikón implements a self-auditing cycle to detect "drift" and "entropy" over longer timeframes.

**Triggers**:

- Time: >= 7 days since last review.
- Accumulation: >= 15 Handoff files in `mneme`.

**Process**:

1. Analyze 15+ Handoffs to extract "Boulēsis Alignment."
2. Recognize recurring "Exception Patterns" from `dispatch_log.yaml`.
3. Update `patterns.yaml` with stable "Intuitions."
4. Generate `weekly_review_YYYY-MM-DD.md`.

## 4. Philosophical Significance

This mechanism implements the **"Red-Other-Person Standard"** (赤の他人基準). By visualizing the "Intuition" at boot, the agent explicitly shows its predecessor's "Will" to the current instance, ensuring continuity of purpose and aesthetic direction.

---
*Codified: 2026-01-28*
*Reference: T8 Anamnēsis Protocol*
