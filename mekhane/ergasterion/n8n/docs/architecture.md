# Sympatheia Architecture — 中枢神経系設計

> **Project**: Sympatheia (συμπάθεια)
> **定義**: Hegemonikón の自律神経系 — n8n による感覚運動ループ

---

## 中枢神経メタファー

![Sympatheia CNS Architecture](/home/makaron8426/oikos/hegemonikon/mekhane/ergasterion/n8n/docs/sympatheia_cns_architecture.png)

### 経路設計

| 経路 | 方向 | 生体比喩 | 実装 |
|:-----|:-----|:---------|:-----|
| **遠心性** (Efferent) | n8n → 外界 | 運動神経 | HTTP Request → Slack/GitHub |
| **求心性** (Afferent) | 外界 → n8n | 感覚神経 | Webhook, Schedule, File Trigger |
| **反射弓** (Reflex Arc) | 求心→即遠心 | 膝蓋腱反射 | WF-09 白血球、WF-12 恒常性 |
| **上行路** (Ascending) | n8n → Claude | 脊髄→大脳 | Handoff 書き込み、タスク提案 |
| **下行路** (Descending) | Claude → n8n | 大脳→脊髄 | /boot, /bye webhook |

### 層構造

```
L3: 意識層    (Claude/LLM)     — 判断、計画、言語
L2: 前意識層  (n8n/Sympatheia)  — 監視、反射、恒常性
L1: 無意識層  (cron/systemd)    — 定期実行、基礎代謝
```

### 不可分性の定義

> Sympatheia 停止 → Hegemonikón は動くが **脆弱**
>
> - Health 監視停止 (感覚喪失)
> - セッション管理停止 (覚醒障害)
> - 自動学習停止 (認知劣化)
> - 異常検知停止 (免疫不全)

---

## 実装ロードマップ

| Phase | WF | 生体比喩 | 依存 |
|:------|:---|:---------|:-----|
| **α** 感覚 | WF-08 File Monitor, WF-15 Heartbeat | 触覚, 心拍 | なし |
| **β** 免疫 | WF-09 White Blood Cell | 白血球 | WF-08 |
| **γ** 記憶 | WF-10 Weekly Digest | 記憶圧縮 | WF-05 metrics |
| **δ** 反射 | WF-11 Attractor Dispatch | 反射弓 | TheoremAttractor |
| **ε** 恒常性 | WF-12 Feedback Loop | 体温調節 | WF-05 metrics |
| **ζ** 統合 | WF-14 Incoming Router | 視床 | 全 WF |

---

*Sympatheia Architecture v0.1.0 — 2026-02-08*
