# AI Synedrion Audit & Remediation System

## Overview

Automated integrity layer for Hegemonikón code, focusing on AI-specific risks. Based on the 91-axis Jules Synedrion taxonomy.

### Future Direction: Synteleia Integration

The "Universal Audit" infrastructure is evolving into the **Synteleia Layer**, adopting a **Poiēsis/Dokimasia Dual-Layer** model. This transitions the auditor from pattern-matching to a systemic cognitive ensemble, utilizing **Inner Product (Synthesis)** and **Outer Product (Cross-Verification)** for high-fidelity cognitive safety.

## Components

- **Audit Engine**: `ai_auditor.py` (AST-based risk detection).
- **Remediation Engine**: `ai_fixer.py` (Pattern-based auto-fixing).
- **Compliance Layer**: `sel_validator.py` (L5 Verification).
- **Perspective Digestion**: Extraction of 91 audit axes and success patterns from JULES Synedrion PRs ([Jules Perspectives](./digestion/jules_synedrion_perspectives.md), [Merged Analysis](./digestion/jules_merged_success_patterns.md)).
- **Philosophy**: **[Intellectual Insanity](./philosophy/intellectual_insanity_experts.md)** — Niche specialist archetypes and obsessive personality-driven auditing.
- **Strategy**: **Absolute Remediation (Core Focus)** — Targeted 10-axis core integrity baseline while managing auxiliary noise. Governed by the [Kairema 10 Standard](../../kairema_integrity_standard/artifacts/standards/kairema_10_completion_criteria.md).

## Operational Milestones

- **Project Mekháne (2026-02-01)**: Successfully reduced 1,204 detected issues to 2 final actionable items (99.8% reduction). [Case Study](../case_studies/project_mekhane_remediation_milestone.md).
- **Refined Heuristics (2026-02-01)**: Transition to noise-reduced "Strict Mode" auditing. [Detailed Design](../standards/refinement_heuristics_2026_02_01.md).

## 22 AI-Risk Axes

Implements AI-001 through AI-022 addressing hallucinations, logic gaps, security (CWE-798), and async/concurrency misuse. Detailed in [Standards](../standards/ai_risk_22_axes_implementation.md).

## v3.0 Audit Framework (L5)

The AI Synedrion is now integrated with the **Audit 5-Layer Framework** (/vet v3.0), adding mandatory **SEL Compliance (L5)**. This ensures that even when the auditor follows a complex remediation workflow, it remains bound by the `minimum_requirements` of the CCL operators.

- **Tools**: `sel_validator.py`, `git-hooks` (optional), `/vet+`.
