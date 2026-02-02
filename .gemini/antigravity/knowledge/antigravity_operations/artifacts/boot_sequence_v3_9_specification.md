# /boot Sequence v3.9 Specification

## 1. Overview
The `/boot` sequence is the essential ritual for starting a session in the Hegemonikón environment. Version 3.9 (implemented 2026-02-01) integrates the **Semantic Enforcement Layer (SEL)** and the **Continuing Me** identity architecture. It follows a "Shared Boot" philosophy where the AI and Creator initialize the state together.

## 2. The 18-Step Sequence [Phase 0-6]

### Phase 0: Identity Stack & Persistence
- **0.1 🧠 Identity Stack Read**: Loads Value (L1), Persona (L2), Memory (L3), and Emotion (L4) layers.
- **0.2 📊 Continuity Scoring**: Calculates a 0.0-1.0 score based on information completeness (values.json, persona.yaml, latest handoff).

### Phase 0.5: Change Tracking (/boot')
- **0.5.1 🔄 Session Variance Detection**: Tracks changes in Will (V[/bou]) and Beliefs (/doxa') since the last session. If Δ > 0.3, prompts for goal re-confirmation.

### Phase 1: Authentication & Refresh
- **1. 🔄 Anti-Stale Protocol**: Force-reads the latest `boot.md` to prevent execution from stale cache.

### Phase 2: Session State Verification
- **2. 📅 Weekly Review Check**: Triggers if 7+ days have passed or 15+ Handoffs have accumulated.
- **3. 📋 Latest Handoff Recovery**: Loads the very last Handoff to ensure task continuity.
- **4. 🎯 Purpose Reminder**: Retrieves the latest `/bou` (Boulēsis) output.
- **5. ⚠️ Context Resonance (Drift Detection)**: Calculates the gap between the stated goal and current focus.

### Phase 3: Knowledge Loading
- **5.5 🔄 Unified Persistence Read**: Re-integrates Handoff, Sophia (KI), and Persona.
- **6. 📚 Sophia Index Summary**: Summarizes the state of ingested Knowledge Items.
- **6.5 🧠 FEP A-Matrix Load**: Restores the learned observation model from np-arrays.
- **6.6 📊 Derivative Learning Recovery**: Restores learned pattern weights for `/noe`, `/bou`, etc.
- **6.7 🎲 KI Random Recall (Anti-Decay)**: Randomly surfaces 3 KIs to prevent "storage decay".

### Phase 4: System Alignment
- **9. 📄 Doctrine Verification**: Checks `GEMINI.md` for active rules.
- **10. ⚙️ Core Module Activation**: Loads Noēsis (O1) and Boulēsis (O2).
- **10.5 🧠 Hexis (Cognitive Stance)**: Sets stance to Poiēsis (Creation), Praxis (Implementation), or Theōria (Review).
- **10.6 🧠 CCL Pattern Review**: Quick reminder of operators (e.g., `*^`).
- **11. 🔧 tools.yaml Sync**: Verifies MCP and script availability.
- **12. 🔍 Gnōsis Freshness Check**: Checks for stale research papers.
- **12.5 🍽️ Digestor Selection**: Recommends papers for internal "digestion".
- **13. 🗂️ Mnēmē Index Update**: Syncs the vector database with the latest files.

### Phase 5: External Input
- **14. 📊 Dispatch Log Check**: Updates target count (Phase B goal: 50).
- **15. 📥 Perplexity Inbox**: Checks for new web-research summaries.
- **16. 🔍 Jules Review Branch**: Checks for pending AI-specialist code reviews.

### Phase 6: Completion
- **17. 🚀 Boot Report**: Generates a structured summary of the boot status.
- **17.5 🚧 Active Projects**: Displays development status from `projects.yaml` (Freshness alerts at 7/21 days).
- **18. 💡 Task Proposing**: Suggests the next meaningful actions based on the context.

## 3. SEL Enforcement Levels
- **"+": Detailed Mode**: MUST execute all 18 steps, 10 Handoffs, 5 KIs. Skip NOTHING.
- **"-": Fast Mode**: Minimal viable boot. Skip Handoff/KI loading. Abbreviated reporting.

---
*v3.9 — 2026-02-01 | Integrated Identity Stack and Random Recall. Managed via SEL.*
