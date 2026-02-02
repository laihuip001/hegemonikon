---
description: [1行説明。Antigravity ワークフロー一覧で表示される]
hegemonikon: [対応シリーズ: Ousia/Schema/Hormē/Perigraphē/Kairos/Akribeia]
modules: [対応モジュール ID: O1, S2, H4, etc.]
skill_ref: "[スキルパス]"  # オプション
pair: "[ペアワークフロー]"  # オプション（/sop ↔ /vet 等）
version: "[X.Y]"  # オプション
---

# /[cmd] ワークフロー

> **Hegemonikón Module**: [ID] ([名前])
> **目的**: [何を達成するか]

---

## 発動条件

| トリガー | 説明 |
|----------|------|
| `/[cmd]` | 標準実行 |
| `/[cmd] [引数]` | 引数付き実行 |
| 自動発動 | [条件] |

---

## Process

// turbo-all  ← 全ステップ自動実行を許可する場合

### Step 1: [ステップ名]

[ステップの詳細]

### Step 2: [ステップ名]

[ステップの詳細]

---

## 出力形式

```markdown
┌─[Hegemonikón]──────────────────────┐
│ [Module ID]: [完了状態]            │
│ 入力: [入力情報]                   │
│ 出力: [出力情報]                   │
└────────────────────────────────────┘
```

---

## Edge Cases

| ケース | 症状 | 対処 |
|:-------|:-----|:-----|
| [条件1] | [症状] | [対処] |

---

## 関連ワークフロー

| ワークフロー | 連携 |
|:-------------|:-----|
| `/[related]` | [連携内容] |

---

## Hegemonikon Status

| Module | Workflow | Status |
|--------|----------|--------|
| [ID] | /[cmd] | v[X.Y] Ready |
