# Sympatheia (συμπάθεια) — n8n 自律神経系

> **語源**: ストア哲学の「共感・万物の相互接続」
> **概念**: 全ての部位が感じ合い、一つが痛めば全体が痛む
> **位置**: mekhane/ergasterion/n8n/
> **FEP 的位置**: Active Inference ループの感覚運動経路

---

## 中枢神経メタファー

```
         Attractor (FEP) ← 小脳
            ↓ Π(o) = 予測
         n8n (求心性経路) ← Sympatheia ⬆️
            ↓ フィードバック
         Python (行動変更)
            ↓ 新しい観察
         n8n (遠心性経路) ← Sympatheia ⬇️
            ↓ 通知
         Slack (知覚)
```

---

## WF 一覧

### 稼働中

| WF | 生体比喩 | 役割 | Version |
|:---|:---------|:-----|:--------|
| WF-02 | 手紙 | /bye Handoff → Slack | v3 |
| WF-03 | 消化 | Incoming Digest → Slack | v5 |
| WF-05 | 感覚 | Health Alert → Severity Classification | v9 |
| WF-06 | 覚醒/睡眠 | Session State Machine | v4 |
| WF-07 | シナプス | FEP Daily Training | v1 |

### ロードマップ

| WF | 生体比喩 | 役割 | Phase |
|:---|:---------|:-----|:------|
| WF-08 | 触覚 | File Monitor | α |
| WF-09 | 白血球 | Anomaly → Auto Response | β |
| WF-10 | 記憶圧縮 | Weekly Digest (sparkline) | γ |
| WF-11 | 反射弓 | Attractor → WF Dispatch | δ |
| WF-12 | 体温調節 | Feedback Loop (恒常性) | ε |
| WF-13 | DNA修復 | Git Sentinel | α |
| WF-14 | 視床 | Incoming Router (統一) | ζ |
| WF-15 | 心拍 | Heartbeat (自己生存証明) | α |

---

## アーキテクチャ原則

1. **不可分性**: Sympatheia 停止 → Hegemonikón の機能が有意に劣化
2. **双方向性**: 遠心性 (通知) + 求心性 (監視) の両経路
3. **自律性**: Claude 不在時こそ活動する
4. **Native Design**: Code=ロジック、IF=分岐、HTTP Request=IO
5. **staticData 優先**: ファイル I/O よりn8n内部永続化

---

## ディレクトリ構成

```
mekhane/ergasterion/n8n/
├── README.md          ← このファイル
├── docs/              ← 設計ドキュメント
│   └── architecture.md
├── wf02_bye_handoff.json
├── wf03_incoming_digest.json
├── wf05_health_alert.json
├── wf06_session_state.json
├── wf07_fep_daily_train.json
├── deploy.sh
├── docker-compose.yml
└── data/              ← n8n DB (gitignore)
```

---

*Sympatheia v0.1.0 — 2026-02-08*
