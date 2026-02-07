---
risk_tier: L1
reversible: true
requires_approval: false
risks:
  - "判断基準の誤適用による過信・過少評価"
fallbacks: []
---
# Fix Skill (C-5 消化)

> **Origin**: C-5 コード外科手術 (Surgical Code Refactoring)
> **責務**: 監査結果に基づく外科的修正

## 発動条件

| トリガー | 説明 |
|:---------|:-----|
| `/vet` で Critical/Major 検出時 | 自動発動 |
| 「修正して」「リファクタして」 | 自然言語トリガー |
| 「直して」「改善して」 | 自然言語トリガー |

## Process

```yaml
Step 1: Fix Criticals (バグ修正)
  → Critical Issues で指摘された論理欠陥を修正
  → セキュリティリスク、未定義変数を解消

Step 2: Modernize & Typify (現代化と型付け)
  → 対象言語の最新バージョンの慣用句を適用
  → 厳格な型定義を付与

Step 3: Functional Parity (機能等価性)
  → 指摘されていないロジックは変更しない
  → 「機能を変えずに品質だけを上げる」
```

## Strict Constraints

```yaml
NO_TRUNCATION:
  → "# ... rest of code" 省略は完全禁止
  → コピペで即座に動作する完全なコードを出力

NO_EXPLANATION:
  → コードブロック外の解説は不要
  → コードそのもので語る
```

## Output Format

```markdown
## 🏥 Surgical Report

### 修正サマリー
| # | 問題 | 修正内容 |
|:--|:-----|:---------|
| 1 | [問題] | [修正] |

### 修正後コード
\`\`\`{{language}}
# Refactored by Fix Skill (C-5)
[完全なソースコード]
\`\`\`
```

## 連携

- `/vet` から自動呼び出し（Critical/Major 検出時）
- 単独でも直接呼び出し可能
