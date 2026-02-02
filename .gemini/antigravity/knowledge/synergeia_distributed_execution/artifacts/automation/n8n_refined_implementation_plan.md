# n8n Refined Implementation Plan

> **Role**: AI Nervous System (Internal processing & self-hosting)
> **Goal**: Automate memory persistence and autonomous research pipelines.
> **Status**: 🟢 **Resumed** (2026-02-01) for Perplexity research digestion workflows.

## 1. Phased Roadmap

| Phase | Milestone | Focus |
|:------|:----------|:------|
| **Phase 0** | Infrastructure | Docker setup, health check, Slack alerts. |
| **Phase 1** | Persistence | `/bye` Webhook integration, Handoff auto-save. |
| **Phase 2** | Intelligence | Gnosis Daily Cron, arXiv summarization, **Perplexity Pipeline**. |
| **Phase 3** | Autonomy | Autonomous research requests, proactive alerts, headless /eat. |

## 2. Core Workflows (Design Patterns)

### WF-02: Session Persistence (Handoff)

- **Trigger**: `POST /bye-signal`
- **Execution**:
  1. Parse session ID and handoff path.
  2. Sync to Sophia/Kairos.
  3. Update FEP A-matrix.
  4. Notify Slack on success/failure.

### WF-03: Gnosis Intelligence Cycle

- **Trigger**: Cron (06:00 JST)
- **Execution**:
  1. Check arXiv/S2 freshness.
  2. Collect relevant new papers.
  3. Generate executive summaries.
  4. Push to Mnēmē for next `/boot`.

## 3. Webhook Architecture

| Endpoint | Method | Purpose |
|:---------|:-------|:---------|
| `/bye-signal` | POST | Persistence trigger on session end. |
| `/research` | POST | Request for background research. |
| `/alert` | POST | External system failures or drift warnings. |

---
*Generated based on Hegemonikón S2 Mekhanē implementation plans.*
