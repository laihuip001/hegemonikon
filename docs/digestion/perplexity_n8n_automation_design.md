# Perplexity → Hegemonikón 自動消化フロー設計

> **設計日**: 2026-02-01
> **対象**: n8n ワークフロー WF-04
> **目的**: Perplexity の日次調査結果を自動で Hegemonikón に消化する

---

## 1. 現状分析

### 既存の Perplexity タスク（設定済み）

| Task | 実行時刻 | 目的 |
|:-----|:---------|:-----|
| Task 1: デイリーブリーフ | 20:00 | 日次統合ポイント |
| Task 2: MCP エコシステム監視 | 08:00 | 技術層更新追跡 |
| Task 3: LLM API 変更監視 | 12:00 | 廃止・新機能検出 |
| Task 4: プロンプト技法 | 22:00 | tekhne パターン更新 |
| Task 5: AI ツール発見 | 06:00 | ワークフロー示唆 |

### 現在の課題

1. **手動保存**: Perplexity 結果をダウンロードフォルダに手動保存
2. **手動消化**: `/boot` 時に手動で `/eat` を実行
3. **腐敗リスク**: 未処理レポートが蓄積

---

## 2. 自動化フロー設計

```text
┌─────────────────────────────────────────────────────────────┐
│               WF-04: Perplexity Auto-Digestion              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [Perplexity Daily Task]                                    │
│         ↓                                                   │
│  [n8n HTTP Request Node]                                    │
│    - Perplexity API: GET /tasks/{task_id}/result            │
│         ↓                                                   │
│  [n8n File Node]                                            │
│    - Save to: /oikos/mneme/.hegemonikon/incoming/           │
│    - Filename: perplexity_{task}_{date}.md                  │
│         ↓                                                   │
│  [n8n Code Node: Digest Generator]                          │
│    - Extract key findings                                   │
│    - Map to Hegemonikón theorems                            │
│    - Generate digest format                                 │
│         ↓                                                   │
│  [n8n Slack Node: Notification]                             │
│    - Summary: "📥 Task {n} 消化完了: {insights} 件"         │
│         ↓                                                   │
│  [n8n Gnosis Node: KI Candidate]                            │
│    - If priority >= ⭐⭐⭐, create KI stub                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. n8n ワークフロー仕様

### WF-04-A: Perplexity Result Fetcher

```json
{
  "name": "WF-04-A: Perplexity Fetch",
  "trigger": {
    "type": "cron",
    "schedule": {
      "task1": "0 21 * * *",
      "task2": "0 9 * * *",
      "task3": "0 13 * * *",
      "task4": "0 23 * * *",
      "task5": "0 7 * * *"
    },
    "note": "1時間遅延で結果が確定してから取得"
  },
  "nodes": [
    {
      "name": "Perplexity API",
      "type": "HTTP Request",
      "method": "GET",
      "url": "https://api.perplexity.ai/tasks/{{$task_id}}/latest",
      "headers": {
        "Authorization": "Bearer {{$credentials.perplexity.apiKey}}"
      }
    },
    {
      "name": "Save Report",
      "type": "Write Binary File",
      "path": "/oikos/mneme/.hegemonikon/incoming/perplexity_{{$task}}_{{$date}}.md"
    }
  ]
}
```

### WF-04-B: Auto Digest

```json
{
  "name": "WF-04-B: Auto Digest",
  "trigger": {
    "type": "webhook",
    "path": "/digest-perplexity"
  },
  "nodes": [
    {
      "name": "Read Incoming",
      "type": "Read Binary Files",
      "path": "/oikos/mneme/.hegemonikon/incoming/*.md"
    },
    {
      "name": "Digest Generator",
      "type": "Code",
      "language": "python",
      "code": "# Extract key sections, map to theorems"
    },
    {
      "name": "Write Digest",
      "type": "Write Binary File",
      "path": "/oikos/hegemonikon/docs/digestion/perplexity_daily_{{$date}}.md"
    },
    {
      "name": "Notify Slack",
      "type": "Slack",
      "channel": "#hegemonikon",
      "message": "📥 Perplexity 消化完了: {{$insight_count}} 件の示唆抽出"
    }
  ]
}
```

---

## 4. ディレクトリ構造

```text
/oikos/mneme/.hegemonikon/
├── incoming/                  # NEW: Perplexity 生データ受信
│   ├── perplexity_task1_2026-02-01.md
│   ├── perplexity_task2_2026-02-01.md
│   └── ...
├── processed/                 # NEW: 処理済みアーカイブ
│   └── 2026-02/
│       └── ...
└── sessions/
    └── handoff_*.md

/oikos/hegemonikon/docs/digestion/
├── perplexity_daily_digest_2026-02-01.md  # 統合消化レポート
└── ...
```

---

## 5. 実装ロードマップ

| Phase | 内容 | 期限 | 状態 |
|:------|:-----|:-----|:-----|
| **0** | ディレクトリ作成 (`incoming/`, `processed/`) | 今日 | 🔲 |
| **1** | n8n Perplexity API 接続テスト | 今週 | 🔲 |
| **2** | WF-04-A 実装（Fetch & Save） | 来週 | 🔲 |
| **3** | WF-04-B 実装（Auto Digest） | 2月中旬 | 🔲 |
| **4** | Slack 通知・KI 候補自動生成 | 2月末 | 🔲 |

---

## 6. Perplexity API 確認事項

> **⚠️ 要確認**: Perplexity の API で Tasks 結果を取得できるか

### 確認が必要な項目

1. **Tasks API エンドポイント**: `/tasks/{id}/result` は存在するか？
2. **認証方式**: API Key / OAuth？
3. **レート制限**: 日次クエリ上限は？

### 代替案（API 非対応の場合）

| 方法 | 概要 | 難易度 |
|:-----|:-----|:-------|
| **A) メール転送** | Perplexity → メール → n8n IMAP | 低 |
| **B) ブラウザ自動化** | Playwright で結果取得 | 中 |
| **C) 手動 + Webhook** | 手動保存後に n8n がディレクトリ監視 | 低 |

---

## 7. 次のアクション

1. [ ] `/oikos/mneme/.hegemonikon/incoming/` ディレクトリ作成
2. [ ] Perplexity API ドキュメント確認
3. [ ] n8n Docker 稼働状況確認
4. [ ] WF-04-A 実装開始

---

*この設計は `/mek` ワークフローに基づき、S2 Mekhanē の自動化戦略に沿っています。*
