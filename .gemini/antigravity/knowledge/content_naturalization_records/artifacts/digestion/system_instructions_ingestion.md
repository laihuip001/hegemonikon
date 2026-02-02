# System Instructions Ingestion (2026-01-29)

> **Process**: `/eat`
> **Target**: 12 System Instruction files (173KB) from Archive
> **Status**: 🟢 Naturalized

## 📋 Digestion Summary

The goal was to analyze a legacy prompt library and extract high-value "nutrients"—prompting techniques, architectural patterns, and cognitive tools—for integration into the Hegemonikón framework.

### Tier 1: High-Architecture (Naturalized)

| Source Content | Hegemonikón Integration | Key Insight |
|:---------------|:------------------------|:------------|
| **Dual-Core Strategy** | `tekhne-maker/references/dual-core-architecture.md` | Clear role division between Gemini (Execution) and Claude (Nuance). |
| **Meta-Prompt (Gemini)** | `tekhne-maker/references/gemini-meta-prompt.md` | Standardization of the "Less is More" paradigm for Gemini 3 Pro. |
| **品質審問官 (Inquisitor)** | `/dia --mode=audit` (absorbed) | A Forensic/Zero-Tolerance audit protocol for artifact verification. |

### Tier 2: Specialized Tools (Naturalized)

| Source Content | Hegemonikón Integration | Key Insight |
|:---------------|:------------------------|:------------|
| **事実でぶん殴るやつ (Facts)** | `/dia --mode=cold_mirror` | Identifies cognitive distortions and logical fallacies with "Reality Check" output. |
| **GDR KB化 (Converter)** | `tekhne-maker/references/gdr-converter.md` | Direct compiler-style conversion of research reports into knowledge atoms. |
| **無題 (Repo Context)** | `tekhne-maker/references/repo-to-context.md` | Serialization of codebases into high-density machine-readable maps. |

### Tier 3: Specialized/Redundant (Archived/Skipped)

- **1.md**: Skipped due to redundancy with the existing `GEMINI.md` and `User_Operating_Manual`.
- **Domain-Specific (GrapheneOS, AI Clipboard Pro)**: Project-specific logic that was archived without system-level integration.

## 🛠️ Naturalization Details

### 1. Dual-Core Task Delegation

The `Dual-Core` strategy was abstracted into a standard delegation pattern. It codifies the engine selection logic:

- **Gemini 3 Pro**: Designated as **E1 (Execution Prime)** for verifiable tasks, code, and speed.
- **Claude Opus 4.5**: Designated as **E2 (DeepThought)** for dialectical analysis and high-ambiguity prompts.

### 2. The Cold Mirror Mode (/dia)

The "Fact-Slapping" prompt was transformed into a sophisticated A2 Krisis mode. It uses a 4-step "Cold Mirror" protocol:

1. **Fact Detection**: Isolating objective proof.
2. **Distortion Analysis**: Identifying logical fallacies or cognitive biases (e.g., Catastrophizing).
3. **Correction loop**: Presenting the logic-cleansed interpretation.
4. **Actionable Step**: Forcing a pragmatic behavior shift.

## 🔍 Verification

The integration was verified using the `/ax` (Axiom) workflow, where all 7 theorem layers (O→S→H→P→K→A→X) passed for the implementation plan. Final digestion was confirmed as **🟢 Naturalized** (no boundary remains, seamlessly integrated into references and workflows).

**Final Action**: Files committed and synchronized.

- **hegemonikon commit**: `9f07130a` (`feat(tekhne): digest System Instructions (5 refs)`)
- **oikos commit**: `ebdef848` (`feat(dia): add --mode=cold_mirror and update hegemonikon submodule`)
- **Target**: `hegemonikon/mekhane/ergasterion/tekhne/references/`
- **Reference Logic**: Automatically recognized by the v6.8 references engine.
