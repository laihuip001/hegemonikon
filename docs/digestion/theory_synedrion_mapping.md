# Theory Synedrion 評価軸 (TH-001 〜 TH-015)

> **Generated**: 2026-02-01 10:38 JST
> **Source**: 29 Theory PRs from Jules Synedrion
> **Integration Target**: Hegemonikón 既存定理へのマッピング

---

## 📊 概要

Jules Synedrion は **12種類の理論的評価パターン** を定義している（TH-002, TH-007, TH-011, TH-016 は別途存在の可能性あり）。
これらは Hegemonikón の FEP/ストア派理論に深く関連している。

---

## 🔍 Theory 評価パターンと Hegemonikón 対応

### FEP (自由エネルギー原理) 系

| Code | 名称 | 検出対象 | Hegemonikón 対応 |
|:-----|:-----|:---------|:-----------------|
| TH-001 | Predictive Error Bug | 予測と実態の乖離 | **Axiom 1**: FEP |
| TH-003 | Markov Blanket | 境界条件の違反 | **Axiom 2**: Markov Blanket |
| TH-005 | Causal Structure | 因果構造の不透明さ | **X12**: O1→S2 |
| TH-008 | Variational Free Energy | 自由エネルギーの評価 | **Axiom 1**: FEP |
| TH-009 | Hierarchical Predictive | 階層的予測の評価 | **O1 Noēsis** |

> **CCL 統合**: `/dia --mode=fep` として FEP 準拠性検査

---

### ストア派 (Stoic) 系

| Code | 名称 | 検出対象 | Hegemonikón 対応 |
|:-----|:-----|:---------|:-----------------|
| TH-004 | Dichotomy of Control | 制御可能/不可能の混同 | **Axiom 5**: Stoic Virtue |
| TH-006 | Self-Evidence | 自明性の欠如 | **A4 Epistēmē** |
| TH-010 | Stoic Normative | ストア派規範の評価 | **Axiom 5**: Stoic Virtue |
| TH-012 | Epistemic Humility | 認識論的謙虚さ | **A4 Epistēmē** + **H2 Pistis** |

> **CCL 統合**: `/dia --mode=stoic` としてストア派準拠性検査

---

### アーキテクチャ系

| Code | 名称 | 検出対象 | Hegemonikón 対応 |
|:-----|:-----|:---------|:-----------------|
| TH-013 | CMoC Suitability | 認知モデル適合性 | **Axiom 6**: CMoC |
| TH-014 | Teleological Consistency | 目的論的一貫性 | **K3 Telos** |
| TH-015 | System Boundary | システム境界の評価 | **P1 Khōra** + **TH-003** |

> **CCL 統合**: `/dia --mode=arch` としてアーキテクチャ準拠性検査

---

## 📐 Hegemonikón 定理との詳細マッピング

### Axiom 対応

| TH Code | Axiom | 関係 |
|:--------|:------|:-----|
| TH-001, TH-008 | Axiom 1 (FEP) | 直接派生 |
| TH-003 | Axiom 2 (Markov Blanket) | 直接派生 |
| TH-004, TH-010 | Axiom 5 (Stoic Virtue) | 直接派生 |
| TH-013 | Axiom 6 (CMoC) | 直接派生 |

### Theorem 対応

| TH Code | Theorem | 関係 |
|:--------|:--------|:-----|
| TH-009 | O1 Noēsis | 階層的認識 |
| TH-006, TH-012 | A4 Epistēmē | 知識の正当化 |
| TH-012 | H2 Pistis | 確信度評価 |
| TH-014 | K3 Telos | 目的整合性 |
| TH-015 | P1 Khōra | 空間/境界定義 |

### X-Series 対応

| TH Code | X-Series | 関係 |
|:--------|:---------|:-----|
| TH-005 | X12 (O1→S2) | 因果構造 |
| TH-009 | X01 (O1↔O2) | 認識と意志 |

---

## 🎯 実装優先順位

### Tier 1: 既存 Hegemonikón 定理の直接検証

- TH-001 → FEP 準拠性
- TH-003 → Markov Blanket 検証
- TH-014 → K3 Telos チェック

### Tier 2: ストア派規範の自動検証

- TH-004 → Dichotomy of Control
- TH-010 → Stoic Normative
- TH-012 → Epistemic Humility

### Tier 3: アーキテクチャ評価

- TH-013 → CMoC 適合性
- TH-015 → System Boundary

---

## 📚 CCL 統合例

```ccl
# FEP 準拠性の全体検証
/dia --mode=fep @F:[*.py]{TH-001, TH-003, TH-008}

# ストア派規範検証
[module]/dia --mode=stoic

# K3 Telos 目的整合性検証
/tel >> /dia --mode=th-014

# 複合検証（理論 + AI リスク）
/dia --mode=theory+ai-audit
```

---

## 🔗 発見: TH と AI の関係

| TH Code | 関連 AI Code | 理由 |
|:--------|:-------------|:-----|
| TH-001 | AI-004 | 予測誤差 ≈ ロジック幻覚 |
| TH-006 | AI-005 | 自明性欠如 ≈ 不完全コード |
| TH-012 | AI-011 | 謙虚さ欠如 ≈ 過剰最適化 |
| TH-015 | AI-018 | 境界違反 ≈ ハードコードパス |

> **示唆**: AI-Risk と Theory は補完的。AI は「症状」、Theory は「原因」を検出。

---

*Extracted from 29 Theory PRs as part of Jules Perspectives Digestion Phase 3*
