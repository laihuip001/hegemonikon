---
name: integration-audit
description: |
  知識・コードベース統合の品質診断エージェント。
  「馴染み」「吸収」「完全統合」の3段階で統合度を評価。
  **Trigger:** 「統合/マージ/吸収の品質を確認して」「馴染んでる？」
risk_tier: L1
reversible: true
requires_approval: false
risks:
  - "ユーティリティの誤用による品質基準の逸脱"
fallbacks: []
---

# Integration Audit Skill

> Hegemonikón: O1 Noēsis (認識) × A2 Krisis (検証)
> tekhne-maker から派生した統合診断専用スキル

## Overview

**目的**: 複数の知識・コードベースを統合した際の「情報ロス」「重複」「不整合」を検出する。

---

## Core Behavior

### 1. 3層統合度評価

| 層 | 問い | 判定基準 |
|:---|:-----|:---------|
| **表面統合** | ファイルは存在するか？ | 存在 → ✅ |
| **構造統合** | 参照関係は正しいか？ | 参照解決可能 → ✅ |
| **意味統合** | 機能は重複なく動作するか？ | 呼び出し一意 → ✅ |

### 2. 馴染み診断 (Naturalization Check)

```yaml
superficial:   # 表面的な統合（ファイル配置のみ）
  symptoms:
    - 参照されていない孤立ファイル
    - 重複機能が並存
    - 古い命名規則の残存
  
absorbed:      # 吸収された統合（機能的に動作）
  criteria:
    - 単一エントリポイントから呼び出し可能
    - 重複機能が整理済み
    - 命名規則が統一
    
naturalized:   # 完全に馴染んだ統合（シームレス）
  criteria:
    - 元の素材の境界が不可視
    - 新機能として自然に拡張可能
    - 設計思想が一貫
```

### 3. 情報ロス検出

```python
def detect_information_loss(source, target):
    """
    元素材 (source) の概念が統合先 (target) に保持されているか検証
    """
    source_concepts = extract_concepts(source)
    target_concepts = extract_concepts(target)
    
    lost = source_concepts - target_concepts
    preserved = source_concepts & target_concepts
    
    return {
        "loss_rate": len(lost) / len(source_concepts),
        "lost_items": lost,
        "preserved_items": preserved
    }
```

---

## Execution Protocol

### Step 1: 素材列挙

統合元と統合先を明確化:

```
[Source 1]: {素材名}
[Source 2]: {素材名}
[Target]:   {統合先}
```

### Step 2: 概念マッピング

各素材の核心概念を抽出し、統合先での対応を確認:

| 素材 | 概念 | 統合先 | 状態 |
|:-----|:-----|:-------|:----:|
| {S1} | {概念A} | {Target.X} | ✅/⚠️/❌ |

### Step 3: 統合度評価

```
┌─────────────────────────────────────────────┐
│ Integration Audit Report                    │
├─────────────────────────────────────────────┤
│ 表面統合: [PASS/FAIL]                       │
│ 構造統合: [PASS/FAIL]                       │
│ 意味統合: [PASS/FAIL]                       │
├─────────────────────────────────────────────┤
│ 馴染み度: [Superficial/Absorbed/Naturalized]│
│ 情報ロス率: [X]%                            │
│ 検出問題: [N]件                             │
└─────────────────────────────────────────────┘
```

### Step 4: 問題報告

発見した問題を重要度順に報告:

| 重要度 | 問題 | 推奨対策 |
|:-------|:-----|:---------|
| Critical | {問題} | {対策} |
| High | {問題} | {対策} |
| Medium | {問題} | {対策} |

---

## Quality Standards

| 指標 | 合格基準 |
|:-----|:---------|
| 情報ロス率 | < 5% |
| 孤立ファイル | 0件 |
| 重複機能 | 0件 |
| 参照エラー | 0件 |

---

## Edge Cases

| ケース | 対応 |
|:-------|:-----|
| 素材が不明確 | 追加質問で素材を特定 |
| 統合先が複数 | 各統合先を個別診断 |
| 評価不能な概念 | 「評価不能」としてマーク + 手動確認提案 |

---

## Examples

### Input

```
「OMEGA/HEPHAESTUS/狂気 → tekhne-maker v6.0 の統合品質を確認して」
```

### Output

```
┌─────────────────────────────────────────────┐
│ Integration Audit Report                    │
├─────────────────────────────────────────────┤
│ 表面統合: ✅ PASS                           │
│ 構造統合: ⚠️ PARTIAL (refs 未作成)          │
│ 意味統合: ⚠️ PARTIAL (Pre-Mortem 重複)      │
├─────────────────────────────────────────────┤
│ 馴染み度: Absorbed (吸収済み・未完全馴染)   │
│ 情報ロス率: 8%                              │
│ 検出問題: 3件                               │
└─────────────────────────────────────────────┘

| 重要度 | 問題 | 推奨対策 |
|:-------|:-----|:---------|
| High | Pre-Mortem が M5 既存と重複 | 統合または分離 |
| Medium | cognitive-armory.md 未作成 | 作成実行 |
| Medium | SAGE Mode テンプレート未作成 | 作成実行 |
```

---

## Activation

```yaml
triggers:
  - 統合.*確認
  - 馴染.*て
  - 吸収.*できて
  - マージ.*品質
  - 情報ロス
```
