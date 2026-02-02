# Hegemonikón Governance & Integrity (Immune Layer)

## 1. Overview

**Governance & Integrity** represents the "Immune Layer" of Hegemonikón. It ensures that as the system expands through autonomous agent execution, it maintains its structural beauty, logical necessity, and technical virtue without succumbng to "Canonical Decay" or technical debt.

This Knowledge Item consolidates the following specialized domains:

- **Quality & Integrity (Metrika, Chreos)**: Tactical quality gates and debt management.
- **Structural Enforcement (Zero-Trust)**: Institutionalized constraints against agentic entropy.
- **Existence Proofs (Dendron)**: Verification that every symbol is necessitated by first principles.
- **Synedrion AI Audit Taxonomy**: 91-axis perspective framework for specialist code reviews.

## 2. The Five Pillars

### 2.1 Axial Philosophy (主格言)

The source of necessity. Includes the **Six Layer Maxims** (ruling out subjective delusion/hope) and the **Principle of Anankē** (only building what is inevitable).

### 2.2 Quality Gates (Metrika)

Tactical filters (Pylai) that every implementation must pass:

- **Dokimē (試験)**: TDD mandatory.
- **Syntomia (簡潔)**: Complexity budget.
- **Atomos (原子)**: Modularity.
- **Katharos (清浄)**: Purity/Dead-code removal.

### 2.3 Structural Enforcement (Zero-Trust)

The **Agentic Zero-Trust** protocol. We do not "trust" the AI's intent; we "predict" and "enforce" its behavior through templates, schema validation, and quizes.

### 2.4 Graduated Compliance

Risk-aware supervision levels (Self, Joint, External) ensuring that high-stakes operations receive deep verification while low-risk tasks remain efficient.

### 2.5 System Sustainability

Mechanisms for long-term health, including **Documentation as Memory** (Anamnēsis) and the **Chreos Debt Protocol** (strictly timed TODOs).

### 2.6 State-as-Repo (2026-02-02) ⚡NEW

環境ポータビリティを極限まで高めるため、従来ローカルに閉じていた **`.gemini/` (Brain/Knowledge/Stats) を Git 管理対象** とする。これは「設定のコード化(IaC)」の拡張であり、AI の「学習状態(State)」そのものをリポジトリの正本に統合する。

- **Secrets Management**: 共有の手間を排除するため、認証情報も含めてセキュアな単一リポジトリ（oikos）への集約を許容する。
- **Scale Challenge**: 15GB を超える大規模状態の同期に対し、**Selective Sync**（除外ルール）に加え、極端な肥大化時には **Fresh Initialization**（履歴リセット）を行なう。この際、一時的な容量不足（Out of diskspace）や同期待ち（Latency）が発生するリスクを考慮し、リソースの事前確保と、非同期処理を意識したスケジュール管理を運用標準とした。
- **Identity Integrity**: リセット時には `git config`（user.email/name）の再設定が必須であり、これを怠ると状態の永続化（Commit）が不能になる。実行主体の同一性を保証するための自動構成がガバナンス要件となる。
- **Sub-Repository Management**: エコシステム内の他リポジトリ（hegemonikon 等）が埋め込み状態で検出された場合、単一の State として扱うか、Submodule として分離するかの明確な方針決定を要する。
- **Exclusion Scope Alignment**: `.gitignore` の配置場所とその適用範囲を、同期対象のルートディレクトリと一致させる。環境依存の巨大資材（`.cache/`, `.local/`, `.venv/` 等）が誤って「State」として混入し、同期の可用性を損なう現象を排除するため、全リポジトリにおける厳格なシステムパス管理を通達した。

## 3. Core Components

- [Axial Philosophy](./philosophy/axial_philosophy.md)
- [Hyperengineering as Honor](./philosophy/hyperengineering.md)
- [Technical Virtue & Standards](./standards/technical_virtue.md)
- [Enforcement & Proof Standards](./standards/enforcement_standards.md)
- [Synedrion AI Audit Taxonomy](./standards/synedrion_91_axis_matrix.md)
- [Verification Protocols](./protocols/)
- [Synteleia Ensemble Layer](../hegemonikon_synteleia_ensemble_layer/artifacts/overview.md)

---
*Consolidated Master Standard: 2026-02-01 | Architecture: S2 Mekhanē / S3 Stathmos*
