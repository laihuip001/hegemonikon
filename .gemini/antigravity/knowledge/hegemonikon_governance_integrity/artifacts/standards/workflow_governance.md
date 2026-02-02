# Workflow Governance & Repo Integrity

## 1. Workflow Failure Patterns (Entropic Decay)

As the system scales, workflows tend to "skeletonize" or lose functions during refactors.

| Pattern | Description | Prevention |
| :--- | :--- | :--- |
| **Skeletonization** | Losing semantic flesh during decomposition. | Mandatory Audit step. |
| **Function Dispersion** | Functions disappearing during multi-agent splits. | Centralized Traceability. |
| **Merge Compression** | Details lost during consolidation. | Pre-Delete Inventory. |
| **Operator Drift** | LLMs ignoring symbolic operators (+/-/*). | SEL Requirement (v6.50). |

## 2. Governance Rules

### 2.1 Pre-Delete Inventory (削除前棚卸し)

Before any workflow or artifact is deleted/replaced, a functional inventory must be created. implementation of the replacement is prohibited until 100% of functions are verified in the target.

### 2.2 Functional Absorption (`absorbed` tag)

When a feature is moved, use the `absorbed` frontmatter tag to maintain a technical audit trail of the migration.

### 2.3 Single Responsibility Principle (Workflow SRP)

Every workflow must have exactly one primary responsibility. When a workflow serves multiple disparate purposes, it must be split.

## 3. Repository integrity (Zero Trust Refresh)

The repository structure must mirror its cognitive order (**"Surface reflects Deep"**).

### 3.1 Sacred vs. Profane (聖俗分離)

- **Hieros (Sacred)**: `kernel/`, `mekhane/`. Core logic. Must be perfect.
- **Bebēlos (Profane)**: `ergasterion/`. Experimental zone.
- **Limbo (隔离区域)**: `_limbo/`. For "Ugly but Practical" files that have not yet been proven inevitable.

### 3.2 Skill-Workflow Bridge

`SKILL.md` (Abstract Logic) and `[WF].md` (Interactive interface) should be functionally linked:

- **Skill**: Defines the reasoning logic, theorem mappings, and truth-conditions.
- **Workflow**: Defines the interactive sequence, user prompts, and template formatting.

The Skill acts as the SSOT (Single Source of Truth) for the governing theorems.

### 3.3 Semantic Enforcement Layer (SEL)

All production workflows must include a `sel_enforcement` block in their frontmatter. This block defines the `minimum_requirements` for each operator mode ($+$, $-$, $*$, $\^$, $!$), ensuring symbolic intent is anchored in linguistic obligation markers.

## 4. Multi-Agent Verification Framework (/vet v3.1)

To prevent "Skeletonization" and ensure high-integrity execution, all significant tasks must pass through a 5-Layer cross-model audit.

| Layer | Focus | Verification Metric |
| :--- | :--- | :--- |
| **L1: Accuracy** | Correctness | Artifact existence, schema match. |
| **L2: Process** | Discipline | Step sequence completeness. |
| **L3: Plan** | Alignment | Goal/Constraint satisfaction. |
| **L4: Quality** | Excellence | Hegemonikón quality standards. |
| **L5: SEL** | Compliance | `sel_validator.py` keyword matching. |

### 4.1 自律的再実行フロー (Autonomous Re-execution)

遵守率 (Score) に応じて以下の 3 段階で対応を自動提案する：

| Score | 判定 | 対応 |
|:------|:-----|:-----|
| **>= 80%** | **PASS with Notes** | 軽微な乖離。手動補完またはそのまま完了を推奨。 |
| **< 80%** | **RE-RUN RECOMMENDED** | 重大な乖離。修正後の自動再実行を推奨。 |
| **< 50%** | **ESCALATE / BLOCK** | 壊滅的乖離。強制停止し、ユーザーへ警告。 |

## 4. Anti-Entropy Protocol (v5.6)

> **"6件だけで良いの？" — Do not succumb to laziness.**

- Full insight mining is mandatory weekly.
- 1% promotion rate is a red flag (target 3-5%).
- High-integrity enforcement is required even for routine tasks.

---
*Standard Version: 2026-02-01 | Continuity: Governance v2.0*
