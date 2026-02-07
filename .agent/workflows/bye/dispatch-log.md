---
description: Dispatch Log 自動集計。スキル発動の可視化。
parent: /bye
---

# Dispatch Log

> セッション中の活動を記録し、スキル発動を可視化する。
>
> **制約**: skill_activations と workflow_executions を区別すること。

---

## 記録対象

| 項目 | 説明 | 記録基準 |
|:-----|:-----|:---------|
| skill_activations | スキル発動 | Antigravity が description マッチで自動発動 |
| workflow_executions | ワークフロー実行 | /noe, /s 等のコマンド実行 |
| ki_reads | KI 読み込み | view_file で KI artifact を参照 |
| exception_patterns | 例外パターン | 想定外の状況と対処 |
| epoche_events | 判断停止 | /epo 発動時の Epochē イベント |

---

## 集計手順

1. 振り返り: 「このセッションで発動したスキルは何か？」を自問
2. スキル発動判定:
   - Antigravity サジェスト → スキル読み込み → 使用 = 真の自動発動
   - ワークフロー内で手動参照 = workflow_executions に記録
3. Epochē 判定: 確信度 LOW で判断停止した場合は epoche_events に記録
4. 追記: dispatch_log.yaml の各セクションに追記
5. 統計更新: stats セクションのカウントを更新

---

## 記録形式

```yaml
skill_activations:
  - timestamp: "{ISO8601}"
    skill: "O1 Noēsis"
    trigger: "user_query:深く考えて"
    outcome: "success"
    session_id: "{conversation_id}"

ki_reads:
  - timestamp: "{ISO8601}"
    ki_name: "Hegemonikón Integrated System"
    artifacts_read: ["overview.md"]
    purpose: "設計確認"

exception_patterns:
  - timestamp: "{ISO8601}"
    situation: "想定外の依存関係"
    action_taken: "手動で解決"
    learned: "事前チェックを追加"

epoche_events:
  - timestamp: "{ISO8601}"
    trigger: "確信度 LOW"
    cause: "訓練データ外のドメイン"
    recommendation: "専門家に確認を推奨"
    hollow: false
```

---

## 出力先

`~/oikos/mneme/.hegemonikon/logs/dispatch_log.yaml`

---

## Phase B 移行判定

| 指標 | 閾値 |
|:-----|:-----|
| skill_activations | >= 50 |
| failure_rate | < 10% |
| exception_patterns | >= 3 |

---

> **制約リマインダ**: skill_activations(自動) と workflow_executions(手動) を区別すること。

*/bye サブモジュール — v2.0 FBR*
