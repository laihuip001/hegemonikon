# Standard: Promptware Engineering (Workflow Optimization)

To achieve high-precision execution in LLM workflows, the content must be optimized beyond simple "restructuring." This standard defines the **Stage 2: Content Refinement** patterns derived from prompt engineering research (e.g., LangGPT, RCFOR, Promptbreeder).

## 1. Structural Architecture

### 1.1. Section Order (Primacy & Recency) — Rule R1

Information at the **start** and **end** of a file is processed with the highest accuracy ("Lost in the Middle" prevention).

- **Finding (A1)**: Importance peaks at the start and end of context.
- **Workflow Sequence**:
  1. **Purpose & Role**: 1-3 sentences.
  2. **Global Constraints**: Summarized.
  3. **Input/Trigger**:發動条件.
  4. **Process**: Linearized numbered list.
  5. **Output Format**: Semantic structure.
  6. **Examples**: 1-3 high-quality cases.
  7. **Reminder**: Final reinforcement of top 1-3 rules.

### 1.2. The RCFOR+ Framework (Rule R1)

Adopt the 5-slot structure (Role, Context, Format, Objective, Rules) with the following refinements:

- **Linearization (B3)**: Sequential steps use `1. 2. 3.` Numerical lists are more stable than text arrows (`→`).
- **Nesting Depth (A2)**: Limit to 2–3 levels. For complex logic, split via小見出し (###) or Hub-and-Spoke.

### 1.3. YAML Metadata (A3)

Use **YAML Frontmatter** for machine-readable schema (id, triggers, version). LLMs parse this hybrid format with high reliability.

## 2. Formatting Standards

### 2.1. Functional Beauty (Rule R3) — Pattern D

True "Beauty" in Hegemonikón is **Functional**, not decorative.

- **The "Jobs' Apple" Principle**: Aesthetics must serve functional precision.
- **ASCII Elimination**: All decorative boxes (`┌─┐`) are prohibited in WF instructions. They act as noise and consume tokens.
- **Semantic Tables (B3)**: Use Markdown tables for attribute comparisons or structured outputs. Tables allow LLMs to process information with ~40% higher structural accuracy than unstructured text.

### 2.2. Visual Discipline (Rule R6)

- **Emoji Restriction**: Remove emojis from headings to prevent parser instability. Emojis in the body (e.g., ⚠️) are permitted for critical warnings.

## 3. Cognitive Optimization (Primacy/Recency & Redundancy)

### 3.1. Information Density (B1)

- **Ideal Size**: 2,000–4,000 tokens (5KB–10KB) per file.
- **Verification Result**: The `/mek` v7.1 redesign achieved a **~40% byte reduction** (51KB → 31KB) by removing ASCII decorations while maintaining 100.5% informational density (line count parity).

### 3.2. Repetition Strategy (D1)

Reiterate critical constraints **2-3 times max**.

1. **Primacy**: Start (Summarized).
2. **Body**: Rule module (Detailed).
3. **Recency**: End (Final Reminder).

### 3.3. Instruction Framing (D2-D3)

- **Affirmative base**: Use "Do X" followed by supplemental "Do not Y." (EMNLP 2025 finding).
- **Few-Shot (D3)**: Use 1-3 high-quality examples. 1 Positive base + 1-2 Edge cases. More than 10 examples should be moved to a separate `examples.md` Spoke.

---
*Created: 2026-02-07. Derived from /sop investigation of prompt engineering best practices (LangGPT, RCFOR, Lost-in-the-Middle research).*
