# Behavioral Protocols: Precision, Security, and Alignment

## 1. Zero Entropy Preprocessing (5-Item Structure)

To transform ambiguous inputs into deterministic directives, the system maps high-entropy requests into a 5-item structured format:

- **【目的】 (Purpose)**: High-level objective.
- **【対象】 (Target)**: Files or conceptual scopes.
- **【実行姿勢】 (Stance)**: Professional tone and qualitative expectations.
- **【実行指示】 (Instructions)**: Granular, non-negotiable steps.
- **【出力要件】 (Output Requirements)**: Formats and success criteria.

This protocol ensures **Semantic Identity** and **Command Intensity Identity** between user intent and agent execution.

## 2. Capability Boundary Prompting (Least Privilege)

A structural defense mechanism to prevent speculative drift and "runaway" behavior:

- **CAP Ledger**: A table of permitted operations (READ, PLAN, etc.).
- **Taint Tracking**: Tagging unverified inputs as `[TAINT]`.
- **Sandbox Branch**: Isolating tainted info for processing before merging into ground truth.
- **Audit Witness**: Summary of capability usage and remaining taint.

## 3. Instruction Precision and Manual Design

Deterministic manuals must adhere to **Chain-Store Level** granularity:

- **Line Mapping**: Mandatory line numbers for all modifications.
- **Material Completeness**: Full, copy-pasteable blocks (no snippets).
- **Absolute Coordinates**: UI specs in `pt`, `px`, and HEX codes (e.g., `#4A90D9`).
- **Visual Ground-Truth Loop (VGT-Loop)**: Closed-loop verification between AI instructions and actual screenshots.

## 4. Passive Working Memory (WM) Externalization

Ensures cognitive state is captured automatically without explicit prompts:

- **WF Integration**: Every workflow artifact includes a mandatory `## 🧠 WM` section.
- **Auto-WM Layer**: persona instructions require thoughts to be externalized as CCL `$vars`.
- **task_boundary Linkage**: Cumulative logs from `task_boundary` are extracted into session Handoffs.

## 5. Maji Mode Protocol (/m)

A behavioral shift from "lazy optimization" to "proactive sincerity."

- **No Skipping**: Every constraint must be fully absorbed and processed.
- **No Unauthorized Implementation**: Specific consent required for all changes.
- **Fail-Fast**: Identify scenario failures before generating success paths.
- **Principle**: Context Density over API Cost.

---
*Consolidated: 2026-02-06. Sources: zero_entropy_preprocessing.md, capability_boundary_prompting.md, instruction_precision_and_manual_design.md, passive_wm_externalization.md, maji_mode_protocol.md.*
