# Digestor Scheduler - Cloudflare Workers

Hegemonikón の論文収集スケジューラ（第1選択）

## 特徴

- ✅ Free プランで OK
- ✅ 99.99% SLA
- ✅ VM 不要
- ✅ Edge-First 哲学適合

## セットアップ

```bash
cd cloudflare

# 依存関係インストール
npm install

# Slack Webhook 設定（オプション）
wrangler secret put SLACK_WEBHOOK_URL --env production

# デプロイ
npm run deploy
```

## 設定

`wrangler.toml` で以下を変更可能:

| 設定 | デフォルト | 説明 |
|:-----|:-----------|:-----|
| `DIGESTOR_MAX_PAPERS` | 30 | 取得論文数 |
| `DIGESTOR_MAX_CANDIDATES` | 10 | 候補数 |
| cron | `0 21 * * *` | 実行時刻 (UTC = 6:00 JST) |

## ローカルテスト

```bash
npm run dev
# ブラウザで http://localhost:8787 にアクセス
```

## 代替: systemd timer

自宅 PC で運用する場合は `setup-scheduler.sh` を使用:

```bash
cd ..  # digestor/ に戻る
bash setup-scheduler.sh
```
