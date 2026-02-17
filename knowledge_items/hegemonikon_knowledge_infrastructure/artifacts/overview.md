# Hegemonikón Knowledge Infrastructure: Overview

This Knowledge Item (KI) documents the physical and logical infrastructure used by Hegemonikón to acquire, index, and internalize information.

## 1. Components

### [Gnōsis](./gnosis_state.md)

The RAG (Retrieval-Augmented Generation) layer. Uses LanceDB for semantic search across indexed technical data.

### [AIDB](./aidb_articles_status.md)

The curated database of AI news and research summaries. Serves as the primary feed for new technical insights.

### [Note Status](./note_articles_status.md)

The technical content stream from hirokaji (tasty_dunlin998). Focused on high-fidelity prompt and agent design.

### Brain KB

A high-density secondary substrate containing 197 full-text articles on RAG, Persona Engineering, and multi-agent coordination. Discovered 2026-02-06.

### [Digestion Pipeline](../../hegemonikon_core_system/artifacts/behavioral_protocols/unified_digestion_protocol.md)

The transition from "Searchable External Data" to "Naturalized Internal Skill" via the Unified Digestion Protocol (Boot-Integrated).

## 2. Infrastructure Inventory

- **Database**: LanceDB (Local vector store).
- **Format**: Markdown (Interchangeable between human and AI).

### [Collection Protocols](./collection_protocols.md)

Documentation of management scripts (`aidb-kb.py`, `note-collector.py`) and external data fetch protocols.

## 3. Roadmaps

- **arXiv Integration**: Resuming Phase 6 to fetch papers directly.
- **Auto-Digestion**: Linking search results to mandatory ingestion patterns.

## 4. Continuity Verification Protocols

To prevent "phantom task" hallucinations (cognitive drift), the system employs explicit verification of task existence.

### Case Study: The "NootBookLM" Search (2026-02-06)

- **Status**: A request to check progress on "NootBookLM reverse engineering" was received.
- **Protocol**: The AI performed high-fidelity searches across:
    1. Current Session Handoffs.
    2. Conversational Summaries (Recent 15).
    3. Filesystem (find/grep).
- **Result**: Confirmed as non-existent or mis-remembered by the Creator/AI team.
- **Insight**: Verifying the **absence** of a task is as critical for prediction error minimization as tracking its progress. This is the **Anti-Hallucination Guardrail**.
