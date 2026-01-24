---
description: 現在のセッションまたは過去会話を md 形式でエクスポート。M8 Anamnēsis のエピソード記憶構築。
hegemonikon: Anamnēsis-Sync
modules: [M8]
---

# /exp ワークフロー

> **Hegemonikón Module**: M8 Anamnēsis (Export Phase)
> **目的**: チャット履歴を md 形式で保存し、エピソード記憶として活用

---

## 実行モード

| モード | コマンド | 動作 |
|--------|----------|------|
| **auto** | セッション終了時 | Claude が会話内容を md 化して保存 |
| **manual** | `/exp` | 現在のセッションを即時エクスポート |
| **batch** | `/exp --batch` | Playwright で全会話を自動抽出 |
| **past** | `/exp @[conversation:"タイトル"]` | 過去会話を @conv 参照→記録 |

---

## 保存先

`M:\Brain\.hegemonikon\sessions\`

### ファイル名規則

```
{YYYY-MM-DD}_{session_id_prefix}_{sanitized_title}.md
```

例: `2026-01-24_c13c1315_prompt-lang-and-mention.md`

---

## Step 1: 現在のセッションをエクスポート (manual/auto)

Claude が以下の情報を収集し、md ファイルを生成:

1. セッション ID（会話 ID）
2. タイトル
3. 日時
4. サマリー
5. 主要な決定事項
6. 重要な対話のダイジェスト

### 出力形式

```markdown
# {タイトル}

- **日時**: {YYYY-MM-DD}
- **ID**: {session_id}

## サマリー
{セッション要約}

## 決定事項
- 決定1
- 決定2

## 主要な対話

### {トピック1}
{要約された対話内容}
```

---

## Step 2: 全会話を一括エクスポート (batch)

Playwright を使用して Agent Manager から全会話を自動抽出:

```powershell
# Playwright インストール（初回のみ）
pip install playwright
playwright install chromium

# 全会話エクスポート
python M:\Hegemonikon\mekhane\anamnesis\export_chats.py --format individual
```

### 前提条件

- Antigravity IDE が起動している
- CDP ポート 9222 でリッスンしている

---

## Step 3: 過去会話を個別エクスポート (past)

1. Creator が `/exp @[conversation:"重要な会話タイトル"]` を実行
2. Antigravity が会話メタデータを注入
3. Claude がサマリーと決定事項を md 化
4. `M:\Brain\.hegemonikon\sessions\` に保存

---

## 出力形式

```
[Hegemonikon] M8 Anamnēsis
  Export Phase: Complete
  Saved: M:\Brain\.hegemonikon\sessions\{filename}
  Messages: {count}
```

---

## エラーハンドリング

- **CDP 接続失敗**: Antigravity IDE が起動していることを確認
- **セレクタ不一致**: UI 更新時はセレクタを調整
- **空の会話**: スキップしてログに記録
