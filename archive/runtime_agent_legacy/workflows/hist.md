---
description: チャット履歴をVault形式に変換して同期する。
hegemonikon: Anamnēsis-H
modules: [M8]
---

# /hist ワークフロー

> **Hegemonikón Module**: M8 Anamnēsis (Sync Phase)

Google Takeout からエクスポートされたチャット履歴を Obsidian Vault 形式に変換する。

## 前提条件

- Google Takeout からの履歴 JSON が `/Google Drive/Takeout/` に配置されていること
- 初回実行時は `.sync-state.json` が自動作成される

## 実行手順

1. **同期状態確認**: `.sync-state.json` を読み込み、前回同期時刻を取得

2. **新規ファイル検出**: Takeout ディレクトリ内の未処理 JSON を検出
   - 処理済みファイルはハッシュで管理

3. **JSON解析**: 各ファイルから以下を抽出
   - 日時
   - 参加者（Gemini/Claude/ChatGPT）
   - メッセージ内容
   - **タスクシグナル**: "ToDo", "やります", "確認", "期限"

4. **Vault形式変換**: 以下の形式で Markdown を生成
   ```markdown
   ---
   date: YYYY-MM-DD
   source: gemini|claude|chatgpt
   topic: [自動生成スラッグ]
   tasks_extracted: [タスク数]
   ---
   
   # [トピック]
   
   ## 抽出タスク
   - [ ] [タスク1]
   - [ ] [タスク2]
   
   ## 会話内容
   [会話ログ]
   ```

5. **保存**: `/vault/chat-history/{source}/{date}_{topic}.md` に保存

6. **同期状態更新**: `.sync-state.json` を更新

## 制約

- 1回の実行で最大50ファイル処理
- 重複ファイルはスキップ
- エラー時は部分的に処理を継続

## 出力

```
┌─[Hegemonikón]──────────────────────┐
│ M8 Anamnēsis: Sync Phase 完了     │
│ 処理: [N]件                        │
│ タスク抽出: [M]件                  │
│ パターン更新: [P]件                │
│ Vault保存: 完了                    │
└────────────────────────────────────┘

📥 履歴同期完了
- 処理: [N]件
- タスク抽出: [M]件
- スキップ: [S]件
```
