# 運用ログ収集機構（Phase B移行判定用）

> **Hegemonikón T8 Anamnēsis**: 運用実績の定量的記録

## 目的

Dispatch Protocol Phase B への移行判定に必要な統計情報を収集する。

## 収集対象

| メトリクス | 説明 | Phase B閾値 |
|------------|------|-------------|
| `dispatch_count` | 総ディスパッチ回数 | ≥ 50 |
| `failure_rate` | 失敗率 | < 10% |
| `exception_patterns` | 例外パターン種類 | ≥ 3 |

## ログスキーマ

```yaml
# dispatch_log.yaml

entries:
  - timestamp: "2026-01-26T12:15:00+09:00"
    t_series: T5
    target_agent: perplexity
    status: success | failure
    duration_ms: 1500
    exception: null | "pattern_name"
    notes: "optional"
```

## 保存先

| ファイル | パス | 説明 |
|----------|------|------|
| dispatch_log.yaml | `M:\Brain\.hegemonikon\logs\dispatch_log.yaml` | 生ログ |
| dispatch_stats.json | `M:\Brain\.hegemonikon\logs\dispatch_stats.json` | 集計結果 |

## 記録タイミング

| トリガー | 説明 |
|----------|------|
| **Handoff作成時** | `/bye` 実行時に自動集計 |
| **ディスパッチ発生時** | 手動記録（Phase A） |

## Phase A 運用

Phase A（静的ルール）では**手動記録**:

1. エージェント委譲発生時、Claude/Creator がログに追記
2. `/bye` でセッション終了時に `dispatch_stats.json` を更新

## 統計更新スクリプト（将来）

```powershell
# .agent/scripts/update-dispatch-stats.ps1
# dispatch_log.yaml から dispatch_stats.json を生成
```

## Phase B 移行チェックリスト

- [ ] dispatch_count ≥ 50
- [ ] failure_rate < 10%
- [ ] exception_patterns ≥ 3
- [ ] 動的判定ロジック設計完了

---
*Source: Claude.ai設計協議 (2026-01-26)*
