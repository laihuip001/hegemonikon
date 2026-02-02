# Research Automation Patterns (n8n/Zapier)

> **コンセプト**: リサーチの「手動コピペ」を根絶し、AIの自律神経系として繋ぎ込む

---

## 1. 調査依頼自動化 (Zapier + Perplexity)

- **Trigger**: Slack #research チャンネルへの投稿（または特定リアクション）。
- **Action**: Perplexity API (Sonar 3.1) を Hybrid Model プロンプトでコール。
- **Result**: 結果を GitHub / Mnēmē の `docs/research/perplexity/` に自動ファイル生成。

## 2. 知識ベース自動更新 (n8n + Gnōsis)

- **Trigger**: Cron (06:00 JST)。
- **Action**: Gnōsis 鮮度チェック → stale なら自動収集 (`gnosis-cli collect --auto`)。
- **Benefit**: セッション開始時の `/boot` 工程を大幅短縮。

## 3. インボックス監視と通知 (n8n)

- **Trigger**: 特定ディレクトリ（Perplexity Inbox）への新規ファイル追加。
- **Action**: 内容を短縮要約し、Slack に「新しい知識を吸収可能です」と通知。
- **Integraton**: `/boot` の Phase 5 に接続。

---
*Created: 2026-01-30 | n8n / Zapier Integration Phase*
