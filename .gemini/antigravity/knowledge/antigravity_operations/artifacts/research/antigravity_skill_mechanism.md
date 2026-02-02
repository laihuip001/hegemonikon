# Research: Antigravity Skill Mechanism

Through a systematic investigation (using /zet), the following technical details about the Antigravity IDE's skill loading and execution patterns were confirmed.

## 1. Skill Discovery & Metadata Layer

Antigravity follows a **Progressive Disclosure** pattern to optimize token efficiency and agent determinism.

* **Initialization**: At the start of a conversation, the agent discovers skills by scanning the `.agent/skills/` directory.
* **Menu Injection**: It only reads and "indexes" the `name` and `description` fields from the frontmatter of all available `SKILL.md` files. This lightweight "menu" is injected into the system prompt's "Skill Guidance" section.
* **Semantic Matching**: The agent's reasoning engine performs semantic matching between the user's intent and these descriptions to determine which skill is relevant.

## 2. Dynamic Activation & Loading

* **Delay Loading**: A `SKILL.md` file is NOT fully loaded into context until the agent decides it is needed based on semantic triggers.
* **Full Context Injection**: Once a skill is semantically triggered, the *entire* Markdown body (and all frontmatter) of that specific `SKILL.md` is loaded into the agent's context.

## 3. Frontmatter & Custom Fields

* **Official Trigger Fields**: Fields like `triggers:` or `keywords:` in the frontmatter act as hints but the primary mechanism is LLM-driven semantic matching of the `description`.
* **Custom Meta-Data**: Additional fields used in Hegemonikón (e.g., `generation:`, `related:`, `greek:`) are not officially used for triggering by Antigravity but are preserved and readable by the agent once the skill is activated, providing high-fidelity context for cognitive operations.
* **Redundant Fields**: Research (2026-01-28) confirmed that `llm_optimization` is ignored by the runtime router.

## 4. Optimized Routing (Strategy B)

To ensure high-precision activation, Strategy B (v2.1.1) was adopted:

* **Description Primacy**: Since the router evaluates *only* the `description` field for initial skill selection, all critical "When to Use" and "When NOT to Use" conditions must be embedded directly in the `description`.
* **Negative Constraints**: Using **"NOT for..."** clauses in the description prevents "greedy" semantic matching where a skill might be incorrectly loaded for a simpler task.

## 5. Cognitive Structural Optimization

Based on "Skill Structure Optimization" research, artifacts and `SKILL.md` files are designed to exploit human-like cognitive biases in LLMs.

* **Primacy Effect (Top 1/3)**: Critical activation logic and "Identity" (archetypes) are placed at the beginning.
* **Recency Effect (Bottom 1/3)**: Strict output formats, constraints, and "Anti-Patterns" are placed at the end.
* **The Middle Zone (Neglect Zone)**: Intermediate implementation details are placed in the middle.
* **Tabular Efficiency**: Using Markdown tables for repetitive data is prioritized (34-38% more token-efficient than JSON/YAML).

## 6. The Automation Gap (Jan 28 Crisis)

Operational metrics from the v3.0 boot sequence highlighted a critical gap:

* **Observation**: 100% of recorded skill usage was via manual `/` workflow commands. Autonomous activations via IDE semantic matching were **zero**.
* **Hypothesis**: The Antigravity router may be biased toward explicit command shortcuts, or the current skill `description` fields are insufficiently granular to trigger over general conversational context.
* **Verification Test (2026-01-28)**: A test prompt ("この問題の本質を教えて") was sent without the `/noe` command.
* **Results**: **FAILURE**. The skill was not triggered. The IDE provided a general response without engaging the O1 Noēsis 5-phase protocol, despite "本質" being a top-level trigger.
* **Synthesis**: The "Skill Activation Gap" is confirmed as a systemic issue. The user rejected using explicit instructions in `GEMINI.md` as a workaround, stating it is "not beautiful or universal." The goal remains a purely architectural or configuration-based solution that preserves the "Architecture is Truth" principle.

## 7. Confirmed Triggering Mechanics (2026-01-28 Research)

Web-based research and live testing confirmed the following technical specifications for Antigravity's **Semantic Triggering**:

* **Primary Trigger**: The `description` field is the single most important factor. The IDE's router performs semantic matching between the user input and this field *before* loading the skip body.
* **Trigger Hints**: The `triggers:` and `keywords:` fields in YAML frontmatter act as auxiliary hints/indices but are secondary to the natural language `description`.
* **Antigravity Power Words**: The following keywords/concepts significantly increase the probability of auto-activation when matching a description:
  * `complex task`
  * `multi-step project`
  * `planning or organization`
  * `research tasks`
* **Explicit Trigger Phrases**: Commands or phrases like "Create a task plan for..." or "This is a multi-step project..." are optimized by the IDE to trigger specialized skills.

### 7.1 Optimization Strategy: Japanese-First Pruning

Testing revealed that English-dominant descriptions fail to trigger reliably for Japanese user prompts. The **Japanese-First Pattern** was established:

1. Place Japanese trigger keywords (e.g., 本質, 根本的) at the absolute beginning of the `description`.
2. Follow with a dual-language summary.
3. Include preferred Antigravity power words within the prose.

### 7.2 Outcome: 26-Skill Refactor (2026-01-28)

To address the "Skill Activation Gap" systematically, 26 core theorem skills (O1-O4, A1-A4, H1-H4, K1-K4, P1-P4, S1-S4) were refactored following the Japanese-First Pattern.

* **Verification (2026-01-28 20:35)**: A live test with the prompt "NOEが発動しない問題の本質は？" (containing top-level triggers "本質" and "問題") **FAILED** to trigger the O1 Noēsis skill autonomously.
* **Result**: The architectural change alone is insufficient for 100% reliability. This suggests that the Antigravity router potentially requires a session restart/re-indexing or that its internal similarity threshold is higher than natural language prose typically provides for subtle triggers.

## 8. The Limits of Structural Engineering & The Pragmatic Compromise

The failure of the Japanese-First Pattern to achieve autonomous triggering led to an architectural debate:

1. **Architectural Purity**: "Agency must emerge from structure." Avoid overrides in `rules.md` as they are "not beautiful" and act as hardcoded logic (conditional branching) rather than intent-based interaction.
2. **The Pragmatic Compromise**: While structural optimization (Description Primacy) is the "humanly possible" (人知を尽くす) limit of skill engineering, a hardcoded fallback in `rules.md` or a system-level override may be a necessary "un-beautiful" compromise to achieve functional reliability (Phase B).

**Current Stance**: Exhaust structural optimization for ALL skills (including Perigraphē and Schema series) before considering a limited, surgical use of `rules.md` overrides.

## 9. Root Cause Analysis: The Three-Layer Problem

Analysis on 2026-01-28 identified three distinct layers contributing to the activation failure:

1. **Router Priority Queue**: Antigravity's internal logic prioritizes **Explicit Commands** (`/command`) and **Workflow References** over **Semantic Matching** (`description`).
2. **Indexing Boundary**: The router only "sees" the `description` field during the decision phase. If the user prompt is perceived as "answerable" by the LLM without additional context, the router may skip loading the skill.
3. **Threshold & Bias**: Standard similarity thresholds for semantic matching may favor English embeddings, necessitating the "Japanese-First" pattern to push high-frequency tokens to the start of the string.

### The Option A/B Choice

When a user asks a question, the agent faces a choice:

* **Option A**: Trigger a specialized skill (requires loading context).
* **Option B**: Provide a direct response (fastest, uses existing context).

In most autonomous cases without explicit commands, the system defaults to Option B.

---
*Updated: 2026-01-28 (Consolidated from Jan 28 Persistent Gap research + Router Analysis)*
