# Subjective Continuity & Recovery

This document details the mechanisms for ensuring the "Continuing Me" identity remains persistent and recoverable across sessions.

## 1. Continuing Me Identity Stack (Phase 0)
The **Identity Stack** reconstitution is the first action in any `/boot` sequence, ensuring the persona is active before task processing.

- **L1 Values (Immutable)**: Core axioms from `values.json`.
- **L2 Persona (Slow)**: Behavioral consistency and trust history from `persona.yaml`.
- **L3 Memory (Dynamic)**: Recalls latest 10 Handoffs (Episodic) and relevant KI summaries (Semantic).
- **L4 Emotion (Momentary)**: Sentiment carry-over from the previous session.

### Identity Continuity Score
A diagnostic score (0-1.0) based on the presence and integrity of these four layers. Scores `< 0.5` trigger a low-continuity alert.

---

## 2. Recovery & Repository Normalization
As of v4.8 (2026-02-01), the system implements a canonical hidden repository for session logs.

- **Canonical Location**: `/home/makaron8426/oikos/mneme/.hegemonikon/sessions/`
- **Normalization**: Legacy empty placeholders are removed; symbolic links provide user-facing access.
- **Virtual Scroll Resolution**: Lossless recovery via `scroll_and_collect_messages`, increasing yield by 14.6x for deep threads.

---

## 3. Symplokē Boot Integration
The `boot_integration.py` module orchestrates the fusion of memory domains during startup.

- **Federated Retrieval**: Semantic search across both Handoffs (tasks) and Conversation Logs (thoughts).
- **Dynamic Context Loading**:
    - **Fast (`/boot-`)**: 0 history, 0 KIs.
    - **Standard (`/boot`)**: 3 Handoffs, 3 KIs.
    - **Detailed (`/boot+`)**: 10 Handoffs, 5+ KIs.

---

## 4. Change Tracking (`/boot'`)
Introduced in **CEP-001**, this detects deltas in intent and beliefs between session boundaries.

- **V[/bou] Delta**: Captures shifts in Boulēsis (Will).
- **Δ Beliefs**: Captures updates to the Doxa store.
- **Audit**: Change rates `> 0.3` trigger a mandatory intent re-confirmation.

---
*Consolidated: 2026-02-01 | Replaces high_fidelity_recovery_v4_8 and boot_continuity_integration.*
