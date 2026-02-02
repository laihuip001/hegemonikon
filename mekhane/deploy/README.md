# Swarm Scheduler Deployment

Hegemonikon の 720 視点/日レビューをスケジュール実行するためのデプロイ設定。

## アーキテクチャ

```
┌─────────────────────────────────────────────────────┐
│ Primary: systemd timer (自宅 Linux PC)              │
│   └─ 毎日 4:00 AM JST に swarm_scheduler.py 実行    │
├─────────────────────────────────────────────────────┤
│ Backup: Cloudflare Workers (Edge)                   │
│   └─ Primary 障害時のフェイルオーバー               │
└─────────────────────────────────────────────────────┘
```

## systemd (Primary)

### インストール

```bash
cd deploy/systemd
sudo ./install.sh
```

### コマンド

```bash
# ステータス確認
systemctl status swarm-scheduler.timer

# 次回実行時刻
systemctl list-timers swarm-scheduler.timer

# ログ確認
journalctl -u swarm-scheduler.service -f

# 手動実行
systemctl start swarm-scheduler.service

# 無効化
systemctl disable swarm-scheduler.timer
```

## Cloudflare Workers (Backup)

### セットアップ

```bash
cd deploy/cloudflare-workers
npm install

# API キーを設定
wrangler secret put JULES_API_KEY_1 --env production
wrangler secret put JULES_API_KEY_2 --env production
# ... (9キー分)

# Slack Webhook (オプション)
wrangler secret put SLACK_WEBHOOK_URL --env production
```

### デプロイ

```bash
npm run deploy
```

### テスト

```bash
# ローカル開発
npm run dev

# ログ監視
npm run tail
```

## 予算設定

| 設定 | 値 |
|:-----|:---|
| 日次予算 | 720 セッション |
| キー数 | 9 |
| キーあたり | 80 セッション |
| 実行時刻 | 04:00 JST (19:00 UTC) |

## 配分戦略

| Phase | 比率 | セッション数 |
|:------|:----:|:------------:|
| Change-driven | 40% | 288 |
| Discovery | 40% | 288 |
| Weekly Focus | 20% | 144 |
