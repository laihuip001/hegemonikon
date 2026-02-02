# ワークフロー劣化監査報告書

> **実施日**: 2026-01-29
> **対象**: 全44ワークフロー (.agent/workflows/*.md)
> **方法**: Git履歴差分比較 + 内容精査

---

## 📊 監査サマリー

| カテゴリ | 件数 | 状況 |
|:---------|-----:|:-----|
| **劣化あり** | 3 | 修復必要 |
| **正常** | 41 | 問題なし |
| **合計** | 44 | — |

---

## 🔴 劣化発見 #1: `/sop.md` (K4 Sophia)

### 原因

O3/K4分離リマッピング (2026-01-28) 時に骨格のみで新設。KI `hegemonikon_research_standard.md` の内容が未反映。

### 喪失した機能

- PHASE 0-4 構造
- 調査論点テンプレート集
- 品質チェックリスト詳細
- Creator対話フェーズ

### ✅ 修復状況: **完了** (v4.0 → v5.0)

- PHASE 0-4 構造を追加
- 3種類の論点テンプレートを追加
- KI吸収タグをfrontmatterに追加

---

## 🔴 劣化発見 #2: `/pri.md` 削除

### 原因

1:1ワークフロー統一 (commit: 8381b136d) で `/pri.md` を削除し、`/euk`, `/chr`, `/tel` に分解。

### 喪失した機能

| 旧 `/pri.md` 機能 | 後継 | 状況 |
|:-----------------|:-----|:-----|
| **Eisenhower Matrix** (Q1-Q4分類) | ❌ なし | **完全喪失** |
| **Q2 保護メカニズム** | ❌ なし | **完全喪失** |
| min_q2_ratio: 0.2 | ❌ なし | **完全喪失** |
| q2_boost: 0.15 | ❌ なし | **完全喪失** |
| daily_q2_slot: 1 | ❌ なし | **完全喪失** |
| **Priority Score 算出** | ❌ なし | **完全喪失** |
| Goal 40% + Urgency 30% + Commitment 30% | ❌ なし | **完全喪失** |
| Urgency マッピング | ✅ `/chr` | 移植済み |
| 好機判定 | ✅ `/euk` | 新設 |
| 目的整合 | ✅ `/tel` | 移植済み |

### 問題の深刻度: **Critical**

Eisenhower Matrix と Q2 保護は「重要だが緊急でないタスク」を守る中核機能。これがないと「緊急タスクに埋没する」リスクが高まる。

### 修復方針

**Option A**: `/k.md` (Kairos抽象コマンド) に Eisenhower Matrix と Q2 保護を統合
**Option B**: 新規 `/pri.md` を復元（ただし1:1原則に抵触）

> **推奨**: Option A — `/k.md` を Kairos統合ワークフローとして拡張し、`/k pri` モードでEisenhower評価を発動

---

## 🔴 劣化発見 #3: `/plan.md` → `/s.md` 統合

### 原因

/plan → /s 統合 (commit: 03a2c7eb3, 7f3bd8ed5) で詳細が簡略化。

### 喪失した機能

| 旧 `/plan.md` v3.1 機能 | 現 `/s.md` v3.0 | 状況 |
|:----------------------|:----------------|:-----|
| **Y-1 評価** (Fast/Slow/Eternal 3層) | ❌ なし | **喪失** |
| **D-1 評価** (T+0/T+1/T+2 波紋効果) | ❌ なし | **喪失** |
| STAGE別詳細出力形式 | △ 簡略化 | **劣化** |
| Phase 1.3 リスク列付き3プラン | △ 簡略化 | **劣化** |
| Read-Resolve-Proceed 詳細 | △ 簡略化 | **劣化** |

### 問題の深刻度: **High**

Y-1/D-1 評価は「時間軸上の影響分析」を行う独自フレームワーク。これがないと短期的最適化に陥りやすい。

### 修復方針

`/s.md` に Y-1 評価セクションと D-1 評価セクションを追加復元。

---

## ✅ 正常確認ワークフロー

### τ層（実行ワークフロー）— 問題なし

| ワークフロー | 行数 | 評価 |
|:-------------|-----:|:-----|
| `/noe.md` | 128 | ✅ |
| `/bou.md` | 354 | ✅ (FEP統合済) |
| `/ene.md` | 394 | ✅ (6段階フレームワーク) |
| `/zet.md` | 183 | ✅ (PHASE構造あり) |
| `/fit.md` | 471 | ✅ (Digestion Audit) |

### Δ層（抽象コマンド）— 問題なし

| ワークフロー | 行数 | 評価 |
|:-------------|-----:|:-----|
| `/o.md` | — | ✅ |
| `/s.md` | 186 | ⚠️ Y-1/D-1喪失 |
| `/h.md` | — | ✅ |
| `/p.md` | — | ✅ |
| `/k.md` | — | ⚠️ Eisenhower未統合 |
| `/a.md` | — | ✅ |
| `/x.md` | — | ✅ |

### 新規1:1ワークフロー — 問題なし

統一フォーマット（80-97行）で作成され、骨格として適切:

- `/met`, `/mek`, `/sta`, `/pra` (S-series)
- `/pro`, `/pis`, `/ore`, `/dox` (H-series)
- `/kho`, `/hod`, `/tro`, `/tek` (P-series)
- `/pat`, `/gno`, `/epi` (A-series)
- `/euk`, `/chr`, `/tel` (K-series)

---

## 📋 修復完了報告

### ✅ Phase 1: `/k.md` v3.0 — Eisenhower Matrix 統合完了

**変更内容**:

- `/k pri` モードで優先順位判定が可能に
- Eisenhower Matrix (Q1-Q4分類) を復元
- Q2 保護メカニズム (min_q2_ratio, q2_boost, daily_q2_slot) を復元
- Priority Score 算出ロジックを復元
- lineage: `v2.3 + /pri absorption (Eisenhower Matrix, Q2保護) → v3.0`

### ✅ Phase 2: `/s.md` v3.1 — Y-1/D-1 評価復元完了

**変更内容**:

- STAGE 1 に Y-1 評価セクション (Fast/Slow/Eternal) を復元
- STAGE 1 に D-1 評価セクション (T+0/T+1/T+2) を復元
- 3プラン提示にリスク列を追加
- STAGE 1 出力形式に Y-1/D-1 結果を含める
- lineage: `v3.0 + Y-1/D-1 restoration (from /plan v3.1) → v3.1`

### 📊 修復結果サマリー

| ワークフロー | 旧バージョン | 新バージョン | 行数変化 |
|:-------------|:-------------|:-------------|:---------|
| `/sop.md` | v4.0 | v5.0 | +135 |
| `/k.md` | v2.3 | v3.0 | +109 |
| `/s.md` | v3.0 | v3.1 | +62 |

---

## 📚 参照

### 削除されたワークフロー (Git履歴から参照可能)

```bash
# /pri.md の最終版を参照
git show 8381b136d^:".agent/workflows/pri.md"

# /tou.md の最終版を参照
git show 8381b136d^:".agent/workflows/tou.md"

# /plan.md v3.1 を参照
git show 7f3bd8ed5^:".agent/workflows/plan.md"
```

---

*Workflow Degradation Audit Report v1.1 — Repairs Completed*
*Generated: 2026-01-29*
