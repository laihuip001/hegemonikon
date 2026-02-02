# τ層ワークフロー共通基盤分析

## 分析対象

14個のτ層ワークフロー:
`/bye`, `/now`, `/dev`, `/exp`, `/rev`, `/src`, `/pri`, `/rec`, `/why`, `/vet`, `/sop`, `/boot`, `/plan`, `/hist`

---

## 抽出された共通パターン

### 1. フロントマター (Metadata)

**必須フィールド:**

```yaml
---
description: [1行説明。Antigravity ワークフロー一覧で表示される]
hegemonikon: [対応シリーズ: Ousia/Schema/Hormē/Perigraphē/Kairos/Akribeia]
modules: [対応モジュール ID: O1, S2, H4, etc.]
---
```

**オプションフィールド:**

```yaml
version: "[バージョン番号]"       # 変更履歴管理
skill_ref: "[スキルパス]"         # 参照するスキル
pair: "[ペアワークフロー]"        # /sop ↔ /vet のような対関係
tempo: "Fast | Slow"              # 素早い実行 vs 熟考
lineage: "[元ネタ → 現在]"        # 吸収元の記録
```

---

### 2. 発動条件 (Triggers)

| パターン | 例 |
|:---------|:---|
| **明示的トリガー** | `/cmd`, `/cmd [引数]` |
| **サブコマンド** | `/cmd mode`, `/pri auto` |
| **オプション** | `/cmd --jules`, `/exp --batch` |
| **暗黙的トリガー** | 自然言語キーワード（「忘れてない？」→ `/rec`） |
| **自動発動** | 他ワークフローからの呼び出し、時間経過 |

**共通テンプレート:**

```markdown
## 発動条件

| トリガー | 説明 |
|----------|------|
| `/cmd` | 標準実行 |
| `/cmd [引数]` | 引数付き実行 |
| 自動発動 | [条件] |
```

---

### 3. Process (実行手順)

**共通構造:**

```markdown
## Process

// turbo-all  ← 全ステップ自動実行許可（オプション）

### Step 0: Precondition (事前条件)
[Gate Check, 入力検証, 文脈確認]

### Step 1: Input (入力収集)
[データ収集、ファイル読込]

### Step 2: Transform (変換処理)
[メイン処理ロジック]

### Step 3: Output (出力生成)
[結果生成、ファイル保存]

### Step 4: Confirm (確認)
[ユーザー確認、次ステップ提案]
```

**特別なステップ番号:**

- `Step 0.5` — メインステップの間に追加された処理
- `Step 3.5` — 後から追加された付随処理

---

### 4. 出力形式 (Output Format)

**Hegemonikón バナー:**

```markdown
┌─[Hegemonikón]──────────────────────┐
│ [Module ID]: [完了状態]            │
│ 入力: [入力情報]                   │
│ 出力: [出力情報]                   │
└────────────────────────────────────┘
```

**または簡略形式:**

```markdown
[Hegemonikon] [Module ID]
  [フィールド1]: [値]
  [フィールド2]: [値]
```

---

### 5. Hegemonikón 連携

**共通パターン:**

```markdown
## Hegemonikon Status

| Module | Workflow | Status |
|--------|----------|--------|
| [ID] | /[cmd] | v[X.Y] Ready |
```

**skill_ref による定理スキル参照:**

```yaml
skill_ref: ".agent/skills/akribeia/a2-krisis/SKILL.md"
```

---

### 6. Edge Cases / Error Handling

**共通テーブル:**

```markdown
## Edge Cases

| ケース | 症状 | 対処 |
|:-------|:-----|:-----|
| [条件1] | [症状] | [対処] |
| [条件2] | [症状] | [対処] |
```

---

### 7. 関連ワークフロー

**ペア関係:**

| ペア | 関係 |
|:-----|:-----|
| `/boot` ↔ `/bye` | セッション開始 ↔ 終了 |
| `/sop` ↔ `/vet` | SOP生成 ↔ 監査 |
| `/plan` ↔ `/dia` | 計画策定 ↔ 品質診断 |

**連鎖呼び出し:**

```
/boot → /hist → /rev → (ユーザー作業) → /bye
/sop → (Gemini/Jules) → /vet
/noe → /why → /plan
```

---

## 抽象化された共通基盤

### A. 必須構造

```markdown
---
description: [必須]
hegemonikon: [必須]
modules: [必須]
---

# /[cmd] ワークフロー

> **Hegemonikón Module**: [ID] ([名前])

## 発動条件

| トリガー | 説明 |
|----------|------|

## Process

### Step 1: [ステップ名]

## 出力形式

```

[Hegemonikon] [Module]
  ...

```

## Hegemonikon Status

| Module | Workflow | Status |
|--------|----------|--------|
```

### B. オプション構造

```markdown
skill_ref: [スキル参照]
pair: [ペアワークフロー]
version: [バージョン]

## Edge Cases
## 関連ワークフロー
## Configuration
```

---

## 推奨アクション

1. **テンプレートファイル作成** — `.agent/templates/workflow-template.md`
2. **自動検証スクリプト** — 必須フィールドの存在確認
3. **skill_ref の全ワークフロー追加** — 定理スキルへの参照を統一
