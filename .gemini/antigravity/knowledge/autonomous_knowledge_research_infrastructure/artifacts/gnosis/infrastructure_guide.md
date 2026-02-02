# Gnōsis Knowledge Infrastructure Guide

Gnōsis (γνῶσις) serves as the academic knowledge foundation for Hegemonikón. It enables continuous acquisition of technical and scientific knowledge through an autonomous ingestion pipeline, mitigating model cutoff and aligning with the latest research.

- **Continuous Ingestion**: `sophia_ingest.py` allows for both full and incremental updates to the index.
- **Boot Integration**: The `get_boot_ki` API (Axis B) utilizes the index during `/boot` to provide context-aware knowledge pushes, ensuring the agent has access to relevant research and history upon startup.

## 1. Architectural Layers

The infrastructure is divided into **Macro (Mechanisms)** for high-volume background processing and **Micro (Workflows)** for precise manual naturalization.

### 1.1 Input Layer: Collectors

Located in `mekhane/anamnesis/collectors/`, these modules interface with external academic APIs.

| Collector | Source | Features |
|:---|:---|:---|
| `arxiv.py` | arXiv REST API | Search by query/category, Recent paper monitoring. |
| `semantic_scholar.py` | S2 Graph API | DOI mapping, Citation graph traversal. |
| `open_alex.py` (Draft) | OpenAlex | Broad scholarly metadata. |

### 1.2 Processing Layer: The Digestor

Located in `hegemonikon/mekhane/ergasterion/digestor/`, the Digestor is an autonomous macro-mechanism that orchestrates the flow from raw data to actionable candidates.

- **`topics.yaml`**: Curated registry of research areas (Active Inference, Agent Architecture, etc.).
- **`selector.py`**: Keyword-match scoring algorithm that identifies high-value papers.
- **`pipeline.py`**: Core orchestration with **arXiv ID / URL deduplication** to prevent redundant processing.

## 2. Automation & Scheduling (Persistence)

To ensure continuous growth without manual intervention, Gnōsis supports two scheduling patterns implemented in January 2026.

### 2.1 Option 🥇: Cloudflare Workers (Edge-First)

Recommended for high reliability and $0 cost.

- **Mechanism**: Cloudflare Workers Cron Triggers (6:00 JST).
- **Benefits**: 99.99% SLA, no VM dependency, resilient to local downtime.

### 2.2 Option 🥈: Systemd & Python Daemon (Local-First)

Best for data privacy and zero external cloud dependency.

- **Mechanism**: `scheduler.py` (Python daemon) + `systemd` user service.

## 3. Operations & Migration

### 3.1 The "Beautiful Handoff" Pattern

Migration tasks are handled via the **Session Handoff** (`mneme/.hegemonikon/sessions/`) rather than hardcoded checklists.

- **Philosophical Root**: Transient environment needs should not pollute sacred core workflows (`/boot`).

### 3.2 Standardized Execution Environment

Workflows must use the specific `.venv` path to resolve dependencies:
`/home/makaron8426/oikos/hegemonikon/.venv/bin/python .../cli.py`

---
*Gnōsis Implementation Guide | Updated: 2026-01-29*
