# Hegemonikón Multi-Agent Orchestration

## 1. Overview

This Knowledge Item consolidates the architectural and operational documentation for Hegemonikón's multi-agent systems, including **Synergeia** (distributed execution) and the **Specialist Review System** (Synteleia/Synedrion).

The goal is to scale cognitive throughput beyond the limits of a single AI thread by orchestrating specialized agents across multiple accounts and platforms.

## 2. Core Philosophy: Context Density over API Cost

The value of the system is derived not from minimizing API usage, but from maximizing the **Context Density** provided to the core agent. By aggregating findings from hundreds of orthogonal "specialist" perspectives, the system reaches a consensus that exceeds the reliability of any single model call.

## 3. Synergeia (Distributed Execution)

Synergeia optimizes cognitive processing by distributing CCL (Cognitive Control Language) tasks across specialized execution threads:

| Thread | Role | Capacity |
| :--- | :--- | :--- |
| **Antigravity** | Core Cognition & Judgment | 60pt |
| **Claude Code** | Task-based CLI execution (Supports Agent Teams) | 60pt → 960pt+ |
| **Gemini CLI** | Reasoning and generation | 60pt |
| **Jules Pool** | Multi-account code generation | 360pt+ |
| **Perplexity** | Deep research & retrieval | 60pt |

> **New (2026-02-06)**: **Claude Code Agent Teams** allows for 16+ parallel agents coordinating on complex tasks (e.g., full codebase reviews), effectively scaling the Claude Code capacity to the same level as the Jules Pool.

## 4. Specialist Review System (Synteleia / Synedrion)

The Specialist Review System is the primary auditing mechanism, utilizing the Jules Pool for high-throughput analysis.

### System Scale (Legacy v3.0 Ensemble)

- **866 Specialists**: Previous architecture (Phase 0-3) used for massive grid-auditing. This model has been transitioned to the high-density **Specialist v2** framework for improved signal-to-noise ratio.

### Specialist v2 (Purified Intelligence) - Current Operative Model

Following the **First Principles Refactor** (Feb 2026), the system moved to a high-density model of **Purified Intelligences** (Extreme Specialization).

- **Current Capacity**: **140 Elite Specialists** across 21 domain categories.
- **Batched Registry**: Modular loading via `specialists_batch1/2/3.py` for high-throughput parallel execution.
- **Execution Engine**: `run_specialists.py` v3.0 (supports category filtering, sampling, and 15-key API rotation).
- **Tiered Approach**: Separates "Evolutionary" (FEP/Cognitive) from "Sanitary" (PEP8/Security) auditing.
- **Status (2026-02-06)**: Successfully executed a full 140-specialist ensemble run, resulting in ~256 review branches ready for synthesis.

### Integration Flow

1. **Trigger**: Scheduled tasks fire `run_specialists.py`.
2. **Dispatch**: Jules Pool executes specialized audits.
3. **Synthesis**: Results are pulled during `/boot` and signaled for "Unified Digestion."

### Unified Digestion Mode (Boot-Integrated)

Pending specialist reviews (Jules PRs) are now integrated into the **[Unified Digestion Protocol](../../hegemonikon_core_system/artifacts/behavioral_protocols/unified_digestion_protocol.md)**.

- During `/boot`, the system suggests pending reviews alongside un-digested research papers.
- Approving "Integrated Digestion Mode" triggers a batch review/ingestion cycle.

---

### Source

Consolidated: 2026-02-03 | Merged from synergeia_distributed_execution and hegemonikon_specialist_review_system.
