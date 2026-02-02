# Hegemonikón Bye Sequence v3.0 Specification

## 1. Philosophy: The "Closing the Circle" Ritual

Just as `/boot` is the ritual of awakening, `/bye` is the ritual of **Integration** and **Consolidation**. A session is not finished until its knowledge is ingested and its identity is updated.

- **Persistence over Deletion**: Nothing is lost; Git status, chat logs, and mental states are codified.
- **Self-Improvement**: The AI reflectively updates its trust levels and insights before shutdown.
- **Future-Forward**: The closing steps specifically optimize the *next* session's boot speed.

## 2. Sequence Workflow (P1-P5)

| Phase | Name | Core Action |
|:---|:---|:---|
| **P1** | **Trace (Git)** | `git status` check to ensure all code artifacts are tracked. |
| **P2** | **codify (Handoff)** | Prompt-Lang driven generation of the Handoff document. |
| **P3** | **Export (Log)** | Chat history export for long-term auditability. |
| **P4** | **Ingest (Symplokē)** | `kairos_ingest` and `sophia_ingest` to update vector indices. |
| **P5** | **Optimize (P0)** | **Handoff Index Rebuild** and **Persona Update** (Axis C & E). |
| **P6** | **FEP Update** | Saving the learned A-matrix (Dirichlet parameters). |

## 3. P0 Optimization Integration (v3.0)

Version 3.0 introduces two critical background tasks during `/bye` that dramatically enhance the `/boot` experience:

### 3.1 Handoff Index Rebuild (Step 3.7.1)

The system automatically executes `build_handoff_index()` to re-index all sessions including the one just finished. This ensures that the next `/boot` can use semantic search instantaneously without the 30-second encoding overhead.

### 3.2 Persona Update (Step 3.7.2)

The `update_persona()` API is triggered to increment the session count, record one "Recent Insight", and update the **Multidimensional Trust Model (v2.0)**. Trust is no longer a single number but a 5D vector (Competence, Integrity, Understanding, Consistency, Growth) that matures with each collaborative session.

## 4. Continuity Axis (The Closing Gate)

- **Axis A (Handoff)**: Finalized and indexed.
- **Axis C (Persona)**: Trust and sessions updated.
- **Axis E (Efficiency)**: Boot latency reduced by eager indexing.

---
*Created: 2026-01-31 | Bye Sequence v3.0 Operational Standard*
