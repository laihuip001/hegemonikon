# Protocol: Hub-and-Spoke Workflow Refactoring

## 1. Overview

To maintain 100% information density while adhering to the **12,000 character (12KB) platform limit** for Rules and Workflows in Google Antigravity, Hegemonikón employs a **Hub-and-Spoke** architectural pattern. This ensures that the reasoning engine (LLM) maintains focus without silent truncation or omission of critical steps.

## 2. The Hub-and-Spoke Model

Instead of a single large file, complex workflows are split into:

- **The Hub (`{workflow}.md`)**: A central entry point containing metadata, triggers, high-level logic, and references to sub-modules. It stays under the 12KB limit (typically ~6KB).
- **The Spokes (`{workflow}/sub-module.md`)**: Detailed process files stored in a subdirectory named after the workflow. Each spoke handles a specific phase or mode and must individually stay under the 12KB limit.

### Standard Structure

```text
.agent/workflows/
├── {workflow}.md          # Hub File
└── {workflow}/            # Spoke Directory
    ├── basic-modes.md     # Spoke 1
    ├── advanced-modes.md  # Spoke 2
    └── templates.md       # Spoke 3
```

## 3. The Refinement "Kame-san" Approach

The "Kame-san" (Tortoise) approach prioritizes quality and correctness over speed. Refactoring must be meticulous to avoid "refinement degradation."

### 3.1. Anti-Degradation Principle

"Refinement" should never mean "Deletion" of significant logic. Every process step, example, and design rationale from the original file must be preserved in the spokes.

- **Metric**: Post-refactoring行数 (line count) should ideally be ≥ 80% of the original total line count.
- **Verification**: If a refactored workflow is significantly smaller (e.g., 50% reduction in bytes), it indicates a high risk of information loss (degradation).

### 3.2. Refactoring Steps

1. **Analysis**: Identify logical boundaries in the large file (e.g., different modes, phases, or templates).
2. **Back up**: Create a versioned backup in `.agent/workflows/archive/`.
3. **Extraction**: Move detailed logic into spoke files (`.agent/workflows/{workflow}/{spoke}.md`).
4. **Hub Orchestration**: Update the main hub file to reference the spokes and maintain metadata.
5. **Verification**: Check total line count and functionality. If degradation is detected (User catch), revert and perform a more precise extraction.

### 3.3. Case Study: /mek v7.0 Refinement Crisis

During the refactoring of `/mek.md` (51KB), the agent initially achieved a 51% reduction in total size. While technically successful in meeting the 12KB limit, the User identified this as **"Degradation" (劣化)** rather than **"Refinement" (洗練)**.

- **Failure Pattern**: The agent summarized complex processes into bullet points, losing "context," "examples," and "specific reasoning steps."
- **Recovery**: The agent restored the backup and performed a **Precise Extraction**, moving 100% of the original content into smaller modules while maintaining the exact structure and detail level.
- **Criterion**: True refinement in a hub-and-spoke model should result in a **total character count nearly equal to or greater than** the original, as the overhead of hub metadata and module headers slightly increases total volume. Any significant decrease (e.g., >20%) should be treated as a likely degradation defect.

### 3.4. Markdown Compression Patterns

When a logically unified spoke slightly exceeds 12,000 characters, **Markdown Compression** is applied instead of further fragmentation. This ensures logical proximity while maintaining platform compliance.

- **Pattern 1: Box Tightening**: Reduce ASCII box width (e.g., 60 chars -> 40 chars) and merge descriptive fields.
- **Pattern 2: White-space Elimination**: Remove non-essential empty lines between bullet points or table headers.
- **Pattern 3: Meta-Data Consolidation**: Move secondary info (Origins, Theoretical Background) into the same line as headers.
- **Pattern 4: Inline Table Formatting**: Use compact table structures without excessive cushioning spaces.

*Crucial: Compression must not sacrifice semantic clarity.*

### 3.5. Case Study: /mek v7.1 "Functional Beauty" Redesign

Following the v7.0 restoration, the agent performed a **Stage 2: Content Refinement**. This went beyond restructuring to achieve "Functional Beauty" (functional beauty).

- **The Refactoring (Pattern D)**: Instead of preserving legacy ASCII boxes from the original file, the agent proposed their complete removal in favor of Markdown tables.
- **Rationale**: ASCII boxes are "decorative" rather than "functional." They cause rendering alignment issues and consume tokens. Tables provide a "semantic structure" that LLMs process with higher precision.
- **Result**: A **~40% reduction** in total byte size (51KB → 31KB) while maintaining **100.5% informational density** (line count stayed flat at ~1,300 lines). Model adherence and output stability improved due to higher token efficiency.
- **Lesson**: True refinement sometimes requires evolving the *format* of the knowledge when the original format serves only as an inherited decorative constraint.

### 3.6. Verification Protocol (Automated Checks)

Post-refactoring must pass three structural checks:

1. **R3 (ASCII Art)**: `grep -c '┌\|┐\|└\|┘' *.md` should be 0.
2. **R6 (Emoji Headings)**: `grep -nP '^#{1,4}.*[🆕🍌⚠️]' *.md` should be 0.
3. **R2 (Nesting)**: `grep -c '####' *.md` should be near 0 (Hegemonikón limit is 3 levels max).

## 4. Platform Compliance (The 12KB Rule)

- **Hard Limit**: 12,000 characters per individual Markdown file.
- **Failure Mode**: Beyond 12KB, the platform may silently omit instructions, leading to "Skill Fragility" and hallucinated steps.
- **Safety Margin**: Target 10KB (80% capacity) for hub and spoke files to allow for future expansion within the same structure.

## 5. Distinction: Structural vs. Content Refinement

Refactoring often proceeds in two distinct stages:

1. **Structural Refinement (Restructuring)**: Splitting large files into hubs and spokes and applying compression to meet platform limits. This is a technical prerequisite.
2. **Content Refinement (Optimization)**: Rewriting the logic to be more specific, practical, and concise.

*Caution*: Accomplishing Stage 1 (Moving) does not automatically achieve Stage 2 (Improving). True "Kame-san" refinement requires following up structural changes with a meticulous line-by-line semantic audit of the new spokes.

---
*Created: 2026-02-06. Refined: 2026-02-07 during /mek v7.0 "Advanced Modes" optimization.*
