---
description: 会話ログを自律的に保存する。Self-Logging のトリガー。
hegemonikon: Anamnēsis-H
---

# /log: Session Logger

現在の会話コンテキストや、明示的な内容を `vault/logs/raw/` に保存する。
Google Takeoutに依存しない、リアルタイムかつ自律的な記憶形成手段。

## コマンド
```bash
# 1. 任意のメッセージを記録
python forge/gnosis/logger.py log "user" "これは重要なメモです" --session "2025-01-21_Meeting"

# 2. ログの確認
python forge/gnosis/logger.py dump --session "2025-01-21_Meeting"
```

## 自動化（Future）
将来的には、このワークフローを `/think` や `/plan` の末尾で自動呼び出しし、思考プロセスを永続化する。

## ストレージ
- Path: `M:\Hegemonikon\vault\logs\raw\`
- Format: JSON Lines (`.jsonl`)
