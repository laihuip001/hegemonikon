# Scheduler Hosting 最適化レポート

> **調査日**: 2026-01-29
> **目的**: Digestor/Swarm Scheduler (毎日定時 API 呼び出し) の最適ホスティング選定

---

## Executive Summary

**結論**: Cloudflare Workers Cron Triggers が第1選択。理由は Free プラン対応、99.99% SLA、Edge-First 哲学適合。

---

## 比較表

| プラットフォーム | 信頼性 | コスト | 適合度 |
|:----------------|:-------|:-------|:-------|
| **Cloudflare Workers** | ⭐⭐⭐⭐⭐ | $0 | 🏆 第1選択 |
| **systemd timer** | ⭐⭐⭐⭐ | $0 | 🥈 第2選択 |
| **GitHub Actions** | ⭐⭐ | $0 | ❌ 非推奨 |
| **Deno Deploy** | ⭐⭐⭐ | $0 | ⚠️ Cron 削除予定 |
| **n8n / Temporal** | ⭐⭐⭐⭐ | $5-25/月 | ❌ 過剰 |

---

## GitHub Actions の問題

- 5-10分の遅延が常態
- 高負荷時にスキップ
- 「実行保証なし」が公式見解

---

## 実装済み

**現在**: systemd timer (第2選択)

- `digestor-scheduler@.service`
- `setup-scheduler.sh`

**将来**: Cloudflare Workers (第1選択)

- 自宅 PC 故障リスク軽減時に検討

---

## 参考

- Cloudflare Workers Limits: <https://developers.cloudflare.com/workers/platform/limits/>
- Cloudflare Pricing: <https://developers.cloudflare.com/workers/platform/pricing/>
