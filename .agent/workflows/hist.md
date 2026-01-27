---
description: チャット履歴をVault形式に変換して同期する。
hegemonikon: Anamnēsis-H
modules: [M8]
---

# /hist ワークフロー

> **Hegemonikón Module**: M8 Anamnēsis (Sync Phase)

## Step 1: AIDB Sync (Chat History KB)

Antigravity ChatHistory DBをベクトルインデックスと同期する。

```bash
python /home/laihuip001/oikos/hegemonikon/mekhane/peira/scripts/chat-history-kb.py sync --report
```

## Step 2: Takeout Import (Optional)

Google Takeoutデータが存在する場合、Vaultへインポートする。

```bash
# Takeout JSONパス (例)
JSON_PATH="$HOME/ダウンロード/Takeout/Gemini/Gemini.json"
VAULT_PATH="/home/laihuip001/oikos/hegemonikon/vault/chat-history"

if [ -f "$JSON_PATH" ]; then
    python /home/laihuip001/oikos/hegemonikon/forge/scripts/import_takeout.py convert "$JSON_PATH" "$VAULT_PATH"
fi
```

## 出力形式

```
[Hegemonikon] M8 Anamnēsis
  Sync Phase: Complete
  Index: Updated
  Takeout: Skipped (Not found) / Imported [N] files
```

## エラーハンドリング

- **Embedder Error**: モデル読み込み失敗時は Anamnēsis Error として報告。
- **DB Error**: LanceDB 接続/書き込み失敗時も同様に報告。
