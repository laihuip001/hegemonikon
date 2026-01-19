# Phase 5: KB化設計（最小仕様）

## 目的
収集したAIDB記事（Raw）を、AIが検索・引用しやすい「カード」形式に変換する。
Forgeの既存構造（`library/`）と統合し、TPO別ルーティングを可能にする。

---

## 1. カードスキーマ

### 1.1 Frontmatter（必須フィールド）

```yaml
---
# 識別情報
id: "aidb-2026-01-18-001"
source_url: "https://ai-data-base.com/articles/..."
source_type: "AIDB"
created_at: "2026-01-18T10:00:00+09:00"
last_verified: "2026-01-18T10:00:00+09:00"

# 分類（TPOルーティング用）
task_tags:
  - "prompt_engineering"
  - "reasoning"
category: "technique"  # technique | framework | case_study | benchmark | tool
difficulty: "intermediate"  # beginner | intermediate | advanced

# 適用条件（When/When Not）
when_to_use:
  - "複雑な推論タスクで精度を上げたいとき"
  - "Chain-of-Thoughtの改善を検討しているとき"
when_not_to_use:
  - "単純な分類タスク"
  - "レイテンシが最優先の場合"

# 検証情報
verified_models:
  - "GPT-4"
  - "Claude-3"
status: "active"  # active | deprecated | experimental
---
```

### 1.2 本文構造

```markdown
## 概要
[1-2文での要約]

## 核心メカニズム
[この技法/フレームワークが「なぜ効くのか」の説明]

## 適用手順
1. [ステップ1]
2. [ステップ2]
3. [ステップ3]

## プロンプト雛形
\`\`\`xml
<system>
[そのまま使えるプロンプトテンプレート]
</system>
\`\`\`

## 失敗パターン
- **過剰適用**: [どうなるか]
- **前提無視**: [どうなるか]

## 関連カード
- [[card-xxx]]: [関係性]
- [[card-yyy]]: [関係性]

## 出典
- 元記事: [AIDB URL]
- 論文: [arXiv URL等]
```

---

## 2. ディレクトリ構造

```
Refined/
└── aidb/
    ├── _schema/
    │   ├── card_template.md      # カードテンプレート
    │   └── taxonomy.yaml         # タスク分類定義
    ├── cards/
    │   ├── technique/            # 技法カード
    │   ├── framework/            # フレームワークカード
    │   ├── case_study/           # 事例カード
    │   └── benchmark/            # ベンチマークカード
    └── index/
        ├── by_task.json          # タスク別インデックス
        ├── by_model.json         # モデル別インデックス
        └── by_date.json          # 日付別インデックス
```

---

## 3. 抽出ルール

### 3.1 自動抽出（LLM使用）

| フィールド | 抽出方法 |
|------------|----------|
| `概要` | 記事冒頭3段落を要約 |
| `task_tags` | 本文からキーワード抽出→taxonomy.yamlにマッピング |
| `when_to_use` | 「〜のとき」「〜の場合」パターン抽出 |
| `プロンプト雛形` | コードブロック内のプロンプト例を抽出 |

### 3.2 手動レビュー必須

| フィールド | 理由 |
|------------|------|
| `when_not_to_use` | 否定条件は誤抽出リスクが高い |
| `失敗パターン` | 経験知が必要 |
| `verified_models` | 実際に検証しないと不明 |

---

## 4. ルーティング設計（概念）

```
User Query
    ↓
[1] Intent Classification (LLM)
    → task_type: "prompt_engineering"
    → sub_task: "reasoning_improvement"
    ↓
[2] Metadata Filter
    → task_tags CONTAINS "reasoning"
    → status = "active"
    ↓
[3] Vector Search (Top-K)
    → 類似度上位5件のカードを取得
    ↓
[4] Context Injection
    → 取得カードをプロンプトに挿入
```

---

## 5. 評価基準

| 指標 | 目標値 | 測定方法 |
|------|--------|----------|
| カード生成成功率 | 80%以上 | 成功カード数 / Raw記事数 |
| タスク分類精度 | 90%以上 | 手動サンプル100件レビュー |
| 検索Hit率 | 70%以上 | テストクエリ50件での正解カード取得率 |

---

## 6. 実装優先順位

1. **taxonomy.yaml作成**: タスク分類の定義（10-15カテゴリ）
2. **card_template.md作成**: コピペ用テンプレート
3. **抽出スクリプト（phase5-extract-cards.js）**: LLM APIを使用した自動抽出
4. **インデックス生成スクリプト**: JSON形式のインデックス生成
5. **Forge統合**: `library/`へのシンボリックリンクまたはマージ
