---
description: Library (112プロンプト) をキーワード検索し、関連モジュールを表示。
hegemonikon: S2 Mekhanē
modules: [S2]
version: "1.0"
lcm_state: beta
triggers:
  - "Library"
  - "プロンプト検索"
  - "モジュール検索"
  - "テンプレート"
cognitive_algebra:
  "+": "詳細検索 — 全マッチ + essence + 原文リンク"
  "-": "簡易検索 — ファイル名リストのみ"
sel_enforcement:
  "+":
    minimum_requirements:
      - "全マッチを表示（数制限なし）"
      - "各モジュールの essence を引用"
      - "原文への view_file リンクを付与"
  "-":
    minimum_requirements:
      - "ファイル名リストのみ"
---

# /lib: Library 検索ワークフロー

> **目的**: Library の112プロンプトモジュールを検索・参照する
> **Skill**: [prompt-library/SKILL.md](file:///home/makaron8426/oikos/hegemonikon/.agent/skills/prompt-library/SKILL.md)

---

## 発動条件

| トリガー | 動作 |
|:---------|:-----|
| `/lib` | 全カテゴリ概要を表示 |
| `/lib [キーワード]` | activation_triggers でキーワード検索 |
| `/lib+ [キーワード]` | 詳細検索（essence + 原文リンク付き） |
| `/lib- [キーワード]` | 簡易検索（ファイル名リストのみ） |

---

## 処理フロー

// turbo-all

### STEP 1: Library パス解決

```
LIBRARY_BASE=~/Sync/10_📚_ライブラリ｜Library/prompts
```

### STEP 2: YAML frontmatter 走査

キーワードが指定された場合:

1. Library 内の全 `.md` ファイルの YAML frontmatter を解析
2. `activation_triggers` フィールドにキーワードを含むファイルを抽出
3. `hegemonikon_mapping` でグルーピング

キーワード未指定の場合:

1. 全カテゴリの概要を表示

### STEP 3: 結果表示

```
📚 Library 検索結果: "{キーワード}"

| # | モジュール | カテゴリ | HGK対応 |
|:--|:---------|:--------|:--------|
| 1 | 敵対的レビュー凸 | 品質 | A2 Krisis (/dia) |
| 2 | Module 11: Red Teaming | 安全 | A2 Krisis (/dia) |

→ 番号で選択すると essence を表示
→ `view_file` で原文を開く
```

### STEP 4: 注入 (Optional)

Creator が番号を選択すると、そのモジュールの essence をコンテキストに注入。

---

## カテゴリ一覧 (`/lib` 引数なし時)

| カテゴリ | ファイル数 | 説明 |
|:---------|:---------:|:-----|
| `modules/` | 31 | 思考・学習・評価・対話・分析・計画 |
| `modules/dev/` | 25 | 開発プロトコル (DMZ/TDD/Commit等) |
| `system-instructions/` | 12 | System Instructions |
| `templates/forge/` | 44 | Forge 思考モジュール (見つける/考える/働きかける/振り返る) |

---

## Artifact 自動保存

**保存先**: なし（検索結果はチャット内で完結）

---
