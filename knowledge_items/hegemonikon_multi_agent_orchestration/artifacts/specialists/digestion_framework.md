# Jules Specialist Review: Digestion Framework

## 1. Overview

The Hegemonikón Scaled Specialist Review System (Jules Pool) produces high-density automated feedback at a scale that exceeds manual review capacity. The **Digestion Framework** (or `/eat` workflow) provides a systematic method for extracting, synthesizing, and naturalizing these findings into the core system while maintaining repository hygiene.

## 2. Metron Scaling (Classification)

Reviews are analyzed along three axes to determine processing priority:

1. **Actionability (Metron: Alpha)**:
    * **CRITICAL**: Immediate bug fixes (e.g., AI-022 Race Conditions).
    * **EVOLUTIONARY**: Architectural improvements and theoretical refinements (TH-series).
    * **INFORMATIVE**: Documentation updates or low-impact suggestions.
2. **Impact (Metron: Beta)**: Focus on Core Infrastructure vs. Peripheral Documentation.
3. **Redundancy (Metron: Gamma)**: Pattern matching across multiple specialist branches to allow batch KI consolidation.

## 3. Digestion Lifecycle

| Phase | Goal | Tooling/Method | Status (2026-02-06) |
| :--- | :--- | :--- | :--- |
| **I: Classification** | Categorize 790+ branches by impact. | `/met` + `git branch -a` | ✅ Completed |
| **II: Critical Fixes** | Resolve High-severity risks immediately. | `/ene+` (Diorthōsis) | ✅ AI-022, AI-012, ES-018 |
| **III: KI Synthesis** | Consolidate thematic findings into KIs. | `/ene+` (Deep Digestion) | ✅ v3 Deep Synthesis |
| **IV: Pruning** | Remove redundant or integrated branches. | `cleanup_review_branches_v2.sh` | ✅ 338+ pruning ready |
| **V: Verification** | Ensure system stability via tests. | `pytest` + unit tests | ✅ 11/11 Pass |

## 4. Branch Cleanup Strategy

To prevent "branch bloat," integrated reviews are pruned using `scripts/cleanup_review_branches_v2.sh`.

### Operational Modes

* **DRY RUN**: Identified 338 branches for deletion (2026-02-06).
* **EXECUTE**: Deletes branches based on patterns like `ai-[0-9]*-review`, `th-*`, `docs-*`, etc.
* **Criteria**: Legacy docs, merged/duplicate review IDs, and synthesized theoretical branches.

## 5. Implementation Pipeline

1. **Extraction**: Automated `git show` of `docs/reviews/*.md` across categories.
2. **Synthesis**: Synergeia Coordinator combines findings into a single audit report (e.g., `jules_client_review_synthesis.md`).
3. **Consolidation**: Update relevant KIs and prune origin branches.

---
**Source**: Consolidated on 2026-02-06 from Mass Digestion Strategy and Digestion Lifecycle artifacts.
**Linked Files**: `mekhane/symploke/jules_client.py`, `scripts/cleanup_review_branches_v2.sh`
