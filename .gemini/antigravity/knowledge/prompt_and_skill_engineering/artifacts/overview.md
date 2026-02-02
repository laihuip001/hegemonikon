# Prompt and Skill Engineering Overview

This knowledge item represents the unified system for generating and validating high-fidelity AI skills and prompts within the Hegemonikón framework. It integrates the structure of **Prompt-Lang DSL** with the architectural intelligence of **Tekhne-Maker (v6.8+)**.

## Core Components

### 1. Prompt-Lang DSL (v2.x)

A Domain-Specific Language designed for structured prompt engineering. It replaces free-form natural language with a block-based syntax (`@role`, `@goal`, `@constraints`, etc.) that allows for:

- **Validation**: Syntax checking through `prompt_lang.py`.
- **Modularity**: Inheritance (`@extends`) and composition (`@mixin`).
- **Design Intent**: Originally created as a specialized notation to let agents (Jules) generate prompts more efficiently than natural language.
- **Multi-Agent Pipeline**: Functions as a formal contract in tiered generation flows: **Human → Reasoning Agent (Claude) → Builder Agent (Jules) → Executable Prompt**.

### 2. Tekhne-Maker (v6.1)

The orchestrated master generator skill (J2P Absorption). Starting with v6.1, it is physically integrated as a **Production Line** within the `mekhane/ergasterion/` layer. It is exposed to the Antigravity IDE via a symbolic link at `.agent/skills/utils/tekhne-maker` to maintain backward compatibility and automatic discovery. It produces `.prompt`, `SKILL.md`, or **SAGE (XML/MD)** files depending on the task's functional requirements. Its architecture is based on 7 specialized modules (**M0-M6**):

- **M0: FORGE_IDENTITY**: O/X Unit persona, Phantom Timeline (100+ failures survived), and Dopability Protocol.
- **M1: OVERLORD**: Intent crystallization and semantic audit (Mandatory Assumption Display).
- **M2: RECURSIVE_CORE**: 3-layer compute (Expansion → Conflict/Internal Council → Convergence).
- **M3: ARCHETYPE_ENGINE**: Strategy selection + **Expansion Generator** for sub-modules.
- **M4: RENDERING_CORE**: High-density output (BLUF, Visual Logic) including **SAGE Mode**.
- **M5: QUALITY_ASSURANCE**: PRE_MORTEM simulation + 15-scenario WARGAME_DB check.
- **M6: INTERACTIVE_INTERFACE**: (v6.3) Intent discovery (Skill vs. Workflow) and Tiered Ambiguity Resolution.
- **M7: HEGEMONIKÓN_MODE**: (v6.4+) Canonical theorem mapping (O/S/A/H/P/K) and cross-series derivation. In **v6.5**, this is the **default state**.
- **M10: TARGET_AGENT**: (v6.7+) Parameter-driven optimization for Claude, Gemini, and Jules. In **v6.8**, this includes the "Less is More" paradigm for Gemini 3.
- **Axiom Strategy (/ax)**: Alignment of modular capabilities with Hegemonikón theorem layers (O-A series).
- **Expansion Generator**: Ability to generate specialized sub-modules (e.g., O1.1 Adversarial Hypothesis, O1.2 Emotional Resonance).
- **Creativity Engines**: Integration of **A-2 Prism** (Lateral Thinking) and **A-8 Kaleidoscope** (Morphological Matrix) for logical jump assistance.

### 3. Integrated Codex & Libraries

The system relies on hardcoded decision logic and engineering standards:

- **Logic Gates**: Deterministic decision trees for trade-offs (e.g., Speed vs Quality).
- **Wargame DB**: A repository of historical failure patterns to prevent regression.
- **Language & Infra Codex**: Strict best practices for Python, Rust, Docker, K8s, and Security.

## Architecture: The Three-Layer Approach

1. **Layer 1 (Raw Jules)**: High creativity, low determinism. Used for brainstorming.
2. **Layer 2 (Prompt-Lang)**: High structure, 100% determinism. Used for production tools and automated skills.
3. **Layer 3 (Direct Claude/Gemini)**: Complex reasoning and multi-step orchestration.

## Evolution: Toward Unified Poiesis

The system has achieved "Soul-level" absorption of ancestral specialized tools, culminating in the **v6.0 OMEGA Singularity Build**.

**Key Achievements (v6.0-6.8):**

1. **OMEGA Singularity**: Full integration of RECURSIVE_CORE, SAGE Architecture, and "狂気" (O/X Unit) persona.
2. **Generator Digestion (v6.1)**: Complete absorption and deletion of `j2p`, `meta-prompt-generator`, and `prompt-lang-generator` into the single `tekhne-maker` master generator.
3. **Structural Enforcement (v6.2)**: Introduction of the **1-to-3 Rule** (1 abstract concept : 3 concrete divergent examples) and density mandates to combat output thinning.
4. **Workflow Synthesis (v6.3)**: Explicit separation of Skill (`SKILL.md`) and Procedural (`workflow.md`) artifacts via Interactive Mode discovery.
5. **Hegemonikón Mode (v6.4)**: Forced alignment with the 24 canonical theorems (O/S/A/H/P/K series) to ensure philosophical purity.
6. **Sacred-by-Default (v6.5)**: Implementation of Hegemonikón Mode as the primary, default operating mode for all `/tek` invocations.
7. **Targeted Delegation (v6.7)**: Introduction of the `TARGET_AGENT` parameter, absorbing the legacy `/manual` workflow and optimizing output for Jules and Gemini.
8. **Prompt Strategy Shift (v6.8)**: Discovery of the "Less is More" optimization for Gemini 3 and the standardization of Jules' plan-based workflows.
9. **Internal Council**: Multi-perspective reasoning (LOGIC/EMOTION/HISTORY) internalized as a standard quality gate.
10. **System Prompt Naturalization (2026-01-29)**: Integrated 5 high-value prompt architectures (Dual-Core, Gemini Meta-Prompt, Cold Mirror, GDR Converter, Repo Bridge) as standard tekhne-maker references for model-specific optimization.

**Future Roadmap (v6.5+):**

1. **Refining Purity Gates**: Automated detection of "Ghost Utils" (secular skills masquerading as sacred) and redirection to theorem mapping.
2. **Unified Code Discipline**: Transitioning all remaining `SKILL.md` definitions into native Prompt-Lang files.
3. **Dynamic Mixin Evolution**: Automated refinement of mixins based on execution success/failure logs (M7 Dokimē loops).
4. **Legacy Purge**: Safe decommissioning and disposal of the outdated `tekhne-maker.prompt` v5.0 file.

### 4. Reference Documents

- **mode-guide.md**: Detailed documentation for the 6 core operation modes of Tekhne-Maker v6.1.
- **archetypes.md**: Personality and strategy templates for agent generation.
- **tekhne_maker/system_prompt_references_2026_01.md**: Details on Dual-Core and Gemini 3 Pro meta-prompt extensions.
