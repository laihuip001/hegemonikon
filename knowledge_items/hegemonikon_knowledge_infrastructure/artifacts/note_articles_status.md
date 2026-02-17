# Note Article Collection & Digestion Status

## 1. Overview

This document tracks the technical content stream from **hirokaji (note.com/tasty_dunlin998)**, a primary external source for Hegemonikón's prompt engineering and agent architecture updates.

## 2. Collection Status

✅ **Dataset Collected**: 2026-02-06

- **Total Articles**: 120
- **Format**: Markdown (Body extracted via note.com list API v2)
- **Local Path**: `mekhane/peira/raw/note/`
- **Management Script**: `note-collector.py` (v2 - Background Orchestrated)

## 3. Digestion Progress

Hegemonikón uses a tiered digestion approach (Step 1-3) to naturalize external insights.

| # | Article Title | Priority | Status | Naturalized Artifact |
| :--- | :--- | :--- | :--- | :--- |
| 1 | ケイパビリティ境界プロンプティング | 🔴 HIGH | ✅ Complete | `capability_boundary_prompting.md` |
| 2 | Agent Skillsを壊さず運用する | 🔴 HIGH | ✅ Complete | `agent_skill_quality_gate.md` |
| 3 | 優しいAIを捨てる | 🟠 MED | ⏳ Pending | - |
| 4 | AIエージェントの自動発火を事故らせない設計 | 🔴 HIGH | ⏳ Pending | - |
| 5 | NotebookLMで意思決定の抜けを減らす6視点OS | 🟡 LOW | ⏳ Pending | - |
| 6 | 工場AI導入は契約とSOPで9割決まる | 🟢 REF | ⏳ Pending | - |

## 4. Key Findings & Naturalization (2026-02-06)

### 4.1. Capability Boundary Prompting

- **Concept**: Least Privilege + Taint Tracking within prompts.
- **Naturalization**: Integrated into the **Zero Entropy Protocol**. Unverified inputs are marked `[TAINT]` until "Locked" (Creator confirmed).
- **Core Skill**: CAP Ledger (Permission list) used to define agent boundaries.

### 4.2. Agent Skill Quality Gate

- **Problem**: Skill fragility increases as complexity grows.
- **Solution**: Output Contracts + Skill Policies.
- **Naturalization**: Integrated into **Dendron L1 Proofs**. Skills without a defined "Output Contract" or "Purpose" trigger an existence error.

## 5. Operational Notes

- **Script Performance**: `note-collector.py` v2 addresses high-volume hangs by:
    1. Using the `body` field from the list API (one call per 20 articles).
    2. Implementing background execution via `nohup` for persistence.
    3. Enforcing 30s timeouts.
- **Next Target**: Article #4 (**AIエージェントの自動発火を事故らせない設計**) to refine trigger logic safety.

---
*Created: 2026-02-06*
*Lineage: Note Collection -> /eat Pipeline -> Hegemonikón Core*
