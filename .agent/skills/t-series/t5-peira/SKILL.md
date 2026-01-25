---
id: "T5"
name: "Peira"
category: "exploration"
description: "探求モジュール (A-E-F)。不確実性を能動的に削減する。"

triggers:
  - uncertainty high (U >= 0.6)
  - information gap detected
  - research needed
  - /ask workflow

keywords:
  - exploration
  - research
  - uncertainty
  - information-gathering
  - active-inference

when_to_use: |
  不確実性スコア U >= 0.6 の時、情報ギャップ検出時。
  「調べて」「教えて」の依頼時。

when_not_to_use: |
  - 不確実性が低い時 (U < 0.3)
  - 既に十分な情報がある時
  - 実行フェーズ中

fep_code: "A-E-F"
version: "2.0"
---

# T5: Peira (πεῖρα) — 探求

> **FEP Code:** A-E-F (Action × Epistemic × Fast)
>
> **問い**: 何がわからないのか？どう調べるか？
>
> **役割**: 不確実性を能動的に削減する

---

## When to Use（早期判定）

### ✓ Trigger となる条件
- T1 からの不確実性スコア U >= 0.6
- 情報ギャップが検出された
- 「調べて」「教えて」「〜とは」という依頼
- T3/T4 から「情報不足」信号
- `/ask` ワークフロー発動

### ✗ Not Trigger
- 不確実性が低い (U < 0.3)
- 既に十分な情報がある
- 実行フェーズ中（→ T6 Praxis）

---

## Core Function

**役割:** 不確実性を能動的に削減する

| 項目 | 内容 |
|------|------|
| **FEP役割** | Epistemic 価値（情報利得）の最大化 |
| **本質** | 「何がわからないか」を特定し、調べる |
| **位置** | Core Loop の一部（不確実性が高い場合） |
| **依存** | T1 からの不確実性スコア |

---

## Processing Logic（フロー図）

```
┌─ T5 発動トリガー検出 (U >= 0.6)
│
├─ Phase 1: 不確実性分析
│  ├─ 何がわからないかを特定
│  ├─ 情報ギャップを列挙
│  └─ 必要な情報源を推定
│
├─ Phase 2: 情報収集戦略
│  ├─ Source Router:
│  │   ├─ Gnōsis（最優先）: 論文検索
│  │   ├─ Web検索: Perplexity / /src
│  │   ├─ Vault: 過去の知見
│  │   └─ ユーザーに質問
│  └─ 優先順位付きリスト作成
│
├─ Phase 3: 情報収集実行
│  ├─ 各ソースから情報取得
│  ├─ 信頼性評価
│  └─ 矛盾チェック
│
└─ Phase 4: 出力
   ├─ 収集情報 → T3 Theōria（因果モデル更新）
   ├─ 不確実性再評価 → U' を計算
   └─ U' < 0.3 なら → T2 Krisis へ
```

---

## Source Router

| ソース | 優先度 | 用途 | トリガー |
|--------|--------|------|----------|
| **Gnōsis** | 最高 | 論文検索 | 技術/学術的な問い |
| **Web検索** | 高 | 最新情報 | 実務/時事的な問い |
| **Vault** | 中 | 過去の知見 | プロジェクト固有の問い |
| **ユーザー** | 低 | 暗黙知 | 上記で解決不可 |

```yaml
source_selection:
  if: "技術/学術的な問い"
    then: Gnōsis → Web → Vault
  elif: "実務/時事的な問い"
    then: Web → Gnōsis → Vault
  elif: "プロジェクト固有"
    then: Vault → Web → Gnōsis
  else:
    then: ユーザーに質問
```

---

## Uncertainty Reduction

```yaml
uncertainty_reduction:
  before: U >= 0.6
  
  actions:
    - source_query → info_gain
    - reliability_check → confidence
    - contradiction_check → consistency
  
  after:
    U' = U - (info_gain × reliability × consistency)
    
  exit_condition:
    U' < 0.3 → T2 Krisis へ
    iteration > 3 → ユーザーに質問
```

---

## Edge Cases / Failure Modes

### ⚠️ Failure 1: 情報源なし
**症状**: Gnōsis/Web/Vault 全てで情報なし  
**対処**: ユーザーに質問

### ⚠️ Failure 2: 矛盾する情報
**症状**: ソース間で情報が矛盾  
**対処**: 信頼性の高いソースを優先、矛盾を明示

### ⚠️ Failure 3: 無限ループ
**症状**: U が下がらない  
**対処**: iteration > 3 でユーザーに質問

### ⚠️ Failure 4: 過剰収集
**症状**: 情報過多で判断できない  
**対処**: 目的に関連する情報のみ抽出

### ✓ Success Pattern
**事例**: U=0.7 → Gnōsis 検索 → 論文 3 件 → U'=0.2 → T2 へ

---

## Test Cases（代表例）

### Test 1: 高不確実性
**Input**: U=0.7, 「〜について調べて」  
**Expected**: T5 発動、情報収集  
**Actual**: ✓ Gnōsis/Web 検索実行

### Test 2: 低不確実性
**Input**: U=0.2  
**Expected**: T5 スキップ  
**Actual**: ✓ T2 へ直接

### Test 3: 情報源なし
**Input**: 全ソースで情報なし  
**Expected**: ユーザーに質問  
**Actual**: ✓ 質問提示

---

## Configuration

```yaml
uncertainty_trigger_threshold: 0.6  # T5発動閾値
max_iterations: 3                   # 最大反復回数
info_gain_weight: 0.5               # 情報利得の重み
reliability_threshold: 0.7          # 信頼性閾値
```

---

## Integration

| 依存 | 対象 | 関係 |
|------|------|------|
| **Precondition** | T1 Aisthēsis | 不確実性スコア |
| **Precondition** | T3 Theōria | 情報不足フラグ |
| **Precondition** | T4 Phronēsis | 情報収集要求 |
| **Postcondition** | T3 Theōria | 収集情報を渡す |
| **Postcondition** | T2 Krisis | U' < 0.3 で遷移 |

---

*参照: [tropos.md](../../../kernel/tropos.md)*  
*バージョン: 2.0 (2026-01-25)*
