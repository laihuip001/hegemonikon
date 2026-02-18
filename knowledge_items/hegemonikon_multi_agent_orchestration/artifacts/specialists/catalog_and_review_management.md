# Specialist Ensemble: Catalog and Review Management

## 1. The Specialist v2 Ensemble (Purified Intelligence)

The ensemble consists of **140 elite specialists** designed for high-density, domain-specific auditing. Each specialist is a "Purified Intelligence"—optimized for a single point of inquiry (e.g., visual whitespace, naming etymology, or async retry logic).

### 1.1. Categorization (21 Domains)

Specialists are grouped into 21 categories, implemented across modular batches.

- **Technical Quality**: Type Safety, Error Handling, Function Design, Performance, Async, Database.
- **Architecture & Ops**: Class Design, Git, Testing, API Design, Security.
- **Hegemonikón Core**: Hegemonikón, PROOF (FEP alignment), Theory, Cognitive.
- **Aesthetics & Naming**: Aesthetics, Naming, Japanese, Ultimate.
- **Meta-Cognition**: AI Generated, Code Review, Documentation, Edge Case.

## 2. Tier 1: The Evolutionary Core (13 Specialists)

Tier 1 specialists are "Evolutionary"—they directly advance the Hegemonikón's unique identity and minimize core prediction errors.

| ID | Name (Role) | Category | Core Principle / Domain |
| :--- | :--- | :--- | :--- |
| **HG-001** | PROOF行検査官 | hegemonikon | "Code without proof is non-existent." (Existence Proofs) |
| **HG-002** | 予測誤差審問官 | hegemonikon | "惊き (Surprisal) is a design failure." (FEP Alignment) |
| **HG-003** | ストア派制御審判 | hegemonikon | "Accept what you cannot control." (Dichotomy of Control) |
| **HG-004** | CCL式美学者 | hegemonikon | "/noe+*dia^ is a path of thought; keep it beautiful." (CCL Syntax) |
| **HG-005** | 定理整合性監査官 | hegemonikon | "Implementations must align with the 24 Theorems." (Axiomatics) |
| **HG-006** | ワークフロー適合審査官 | hegemonikon | "Patterns (/boot, /dia) are the architecture's skeleton." (WF Form) |
| **AI-002** | ハルシネーション検出者 | ai_generated | Detects non-existent methods/API calls (confidence-based lies). |
| **AI-005** | コード/コメント矛盾検出者 | ai_generated | Detects drift between docstring/comments and implementation. |
| **CG-001** | ネスト深度警報者 | cognitive | "The mind processes 7±2; 4+ levels of nesting is hell." (Chunking) |
| **CG-002** | 認知チャンク分析者 | cognitive | "5+ operators per line exceed cognitive limits." (Density) |
| **AE-012** | 視覚リズムの指揮者 | aesthetics | Audits whitespace density and "visual music" of code. |
| **AE-013** | シンプリシティの門番 | aesthetics | "Complete when nothing left to remove." (YAGNI/Minimalism) |
| **AE-014** | 比喩一貫性の詩人 | aesthetics | Ensures consistent metaphors (e.g., Factory vs Garden) within domains. |

## 3. Review Lifecycle and Backlog Taxonomy (Continued)

When specialists run at scale (via Jules Pool), they generate a high-density "Signal Environment" in the form of Git branches.

### 3.1. Branch Naming Convention

Branches follow the pattern: `origin/{category}-{specialist_id}-{topic}-review-{unique_hash}`

- `TH-*` (Theory/FEP): Teleology, Markov blankets, system boundaries.
- `AI-*` (AI Risk): Context loss, race conditions, hallucinations.
- `ES-*` (Ethics/Stability): Approval bias, value alignment.
- `AE-*` / `AS-*` / `CL-*`: Aesthetics, Async, Cognitive Load.

### 2.2. Mass Digestion Strategy

With backlogs reaching 400-700+ branches, the system employs a tiered digestion approach:

1. **Fetch and Prune**: `git fetch --prune` to refresh local knowledge.
2. **Pattern Cleanup**: Automated scripts (`cleanup_review_branches_v2.sh`) to prune redundant or duplicate branches.
3. **Synthesis**: Consolidating multiple findings into high-level reports (e.g., `jules_client_review_synthesis`).

## 3. Case Study: Diorthōsis AI-022 (Concurrency Fix)

A critical bug in `jules_client.py` was identified by the ensemble:

- **Problem**: "Zombie Sessions" (lost IDs) and "Thundering Herd" (synchronized retries).
- **Correction**:
  - Separated session creation from polling for persistent tracking.
  - Implemented **Exponential Backoff with Jitter** (0-25% random delay) to desynchronize threads.
- **Verification**: 10/10 unit tests passed.

## 4. Operational Strategy

| Feature | Protocol | Purpose |
| :--- | :--- | :--- |
| **Selection** | Evolutionary vs Sanitary | Prioritize FEP/Cognitive over simple PEP8. |
| **Silence** | Quiescence Requirement | Specialists only output if issues are identified. |
| **Ingestion** | Post-Boot Loader | Jules results are injected into Step 16 of `/boot`. |

---
*Updated: 2026-02-06. Consolidated: purified_intelligence_catalog.md, review_backlog_taxonomy.md, jules_client_review_synthesis.md, case_study_ai_022.md.*
