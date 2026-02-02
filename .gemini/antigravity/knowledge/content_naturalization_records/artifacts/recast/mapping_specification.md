# Recast Mapping: Flow AI → Hegemonikón

This document defines the normative mapping used to "naturalize" the Flow AI codebase by renaming its components to align with the Hegemonikón theorem system.

## 🧠 Core Component Mapping (Theorem-based)

| Flow AI (Legacy) | Hegemonikón (Recast) | Theorem Instance | Description |
|:-----------------|:---------------------|:-----------------|:------------|
| `SeasoningManager` | `MetronResolver` | **S1 Metron** | **Implemented**. Resolves continuous intensity into discrete scales. |
| `PrivacyHandler` | `EpocheShield` | **A2 Krisis (Epochē)** | **Implemented**. Protects data by suspending disclosure. |
| `CoreProcessor` | `EnergeiaCoreResolver` | **O4 Energeia** | **Implemented**. Orchestrator that transforms intent into action. |
| `CostRouter` | `EukairiaRouter` | **K1 Eukairia** | Integrated in `EnergeiaCoreResolver`. |
| `CacheManager` | `DoxaCache` | **H4 Doxa** | **Implemented**. Persists results to optimize future recursion. |
| `GeminiClient` | `NoesisClient` | **O1 Noēsis** | **Implemented**. The gateway to raw intelligence. |
| `AuditLogger` | `TealsAnamnesis` | **H3/H4** | *Planned*. Maintains the audit-trail of desires and effects. |
| `SyncJob` | `ChronosPendingTask` | **K2 Chronos** | *Planned*. Manages tasks across temporal constraints. |

## 📁 Directory Structure Naturalization

The recast moves implementation from standard Pythonic names into the dedicated **Poiēma** (Product) layer of the Hegemonikón engine.

- **Base Location**: `hegemonikon/mekhane/poiema/flow/`

| Legacy Path (Flow AI) | Recast Path (Hegemonikón) | Layer |
|:---|:---|:---|
| `src/core/` | `src/mekhane/` | **Mekhanē** (Core Logic) |
| `src/infra/` | `src/mneme/` | **Mnēmē** (Memory/Persistence) |
| `src/api/` | `src/api/` | **Exagōgē** (External Interface) |
| `src/config/` | `src/config/` | **Doxa** (Configuration) |

## 🔢 Constant & Logic Normalization

| Legacy Constant | Recast Constant | Logic Alignment |
|:----------------|:----------------|:----------------|
| `UMAMI_THRESHOLD` | `METRON_DEEP_THRESHOLD` | Boundary for deep cognitive intervention. |
| `LIGHT_MAX` | `METRON_LIGHT` | Minimal intervention scale. |
| `LONG_TEXT_THRESHOLD` | `NOUS_COMPLEXITY_THRESHOLD` | Complexity threshold for model selection. |

- **No Boundary Remnants**: All docstrings, logs, and variable names should use the Recast terminology.
- **Lineage Preservation**: The only occurrence of legacy names should be in the `lineage` field of documentation or specifically marked `deprecated_alias` if necessary for backward compatibility.
- **Core-Only Scope**: Recasting is prioritized for the **Core Logic (Ergasterion/Mekhanē)** and **Persistence (Mnēmē)** layers. Application-specific transport layers (e.g., FastAPI routes) or UI frameworks (e.g., Flet) are excluded from the `poiema/` recast to maintain module portability and philosophical purity.
