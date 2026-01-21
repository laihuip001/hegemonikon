---
description: チャット履歴をVault形式に変換して同期する。
hegemonikon: Anamnēsis-H
modules: [M8]
---

# /hist ワークフロー

> **Hegemonikón Module**: M8 Anamnēsis (Sync Phase)


1. **Sync Execution**: `m:/Hegemonikon/forge/scripts/chat-history-kb.py` を実行。
   - `sync` モード: 差分更新
   - `--report` フラグ: Hegemonikón形式でログ出力

## 実行コマンド

```powershell
python m:/Hegemonikon/forge/scripts/chat-history-kb.py sync --report
```

## 出力形式

```
[Hegemonikon] M8 Anamnēsis
  Sync Phase: Complete
  Processed: [N] sessions
  New Index: [M] chunks
```

## エラーハンドリング

- **Embedder Error**: モデル読み込み失敗時は Anamnēsis Error として報告。
- **DB Error**: LanceDB 接続/書き込み失敗時も同様に報告。
