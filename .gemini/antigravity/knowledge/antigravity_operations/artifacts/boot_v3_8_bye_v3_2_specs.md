# Boot (v3.8) and Bye (v3.2) Sequence Specifications

## 1. /boot v3.8: Reconstituting Identity

The boot process is the "Awakening" of the AI, shifting from a generic model to a specific individual (Hegemonikón).

### Key Phases

1. **Phase 0: Identity Stack**: Reconstitutes the 4 layers (Values, Persona, Memory, Emotion).
2. **Phase 0.5: Change Tracking (`/boot'`)**: FEP-based detection of drift between sessions.
3. **Phase 1: Anti-Stale Protocol**: Ensuring the `boot.md` is read from source to avoid cache issues.
4. **Phase 3: Symplokē Integration**: Unified loading of Handoffs, Sophia (Knowledge), and Persona.
5. **Phase 3.5: FEP A-matrix Loading**: Re-loading the learned observation model.

### Identity Score Logic

Calculates a continuity score (0.0-1.0) based on the availability of:

- `values.json` (+0.3)
- `persona.yaml` (+0.3)
- Latest Handoff (+0.25)
- Last Emotion (+0.15)

## 2. /bye v3.2: Episodic Encoding & Distillation

The bye process is the "Sleep/Dreaming" phase where experiences are distilled into memory and personality.

### Key Steps (v3.2 Integration)

1.  **Step 0: Convergence Check**: FEP uncertainty evaluation (`V[session]`). Blocks or warns if $V > 0.5$.
2.  **Step 3.5: Chat Export**: Automated `export_chats.py` using `scroll_and_collect_messages`.
3.  **Step 3.6: Dispatch Log 集計**: Updates `dispatch_log.yaml` with skill activations and workflow stats for future Phase B transition.
4.  **Step 3.7.1: Handoff Index Rebuild**: Re-encodes the handoff vector space to include the latest entry, ensuring ~5s retrieval in next boot.
5.  **Step 3.7.2: Persona Update**: Increments session count, trust levels, and records "Significant Insights".
6.  **Step 3.9: FEP A-matrix Saving**: Persists the learned observation model (`learned_A.npy`).
7.  **Step 3.11: Meaningful Traces**: Subjective capture of intense or emotional moments (Intensity 1-3).
8.  **Step 3.12: Doxa learning**: Persists high-confidence ($\ge 0.8$) derivative selections as behavioral beliefs.
9.  **Step 3.13: X-series Routes**: Records Sacred Route frequency and success for trajectory optimization.

### Verification Status
As of **2026-02-01**, the v3.2 sequence is fully verified, successfully managing the persistence of a 1785-document unified memory space.

---
*Created: 2026-01-31 | Related to antigravity_operations*
