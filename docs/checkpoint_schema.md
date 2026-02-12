# Checkpoint スキーマ定義

> **起源**: 2026-02-12 /eat 消化 — E5 Checkpoint永続化 (Entire) パターン
> **用途**: `/dia`, `/vet`, `/noe+` などの認知WF実行結果をエピソード単位で永続化
> **保存先**: `~/oikos/mneme/.hegemonikon/checkpoints/`

---

## スキーマ (YAML)

```yaml
# checkpoint_<workflow>_<date>_<short-id>.yaml

id: <UUID>
timestamp: <ISO8601>

# 実行コンテキスト
workflow: <WF名>       # e.g. /dia+, /vet, /noe+
ccl: <CCL式>            # パース前の原文
session: <セッションID>  # Handoff 番号に対応
trigger: <発動トリガー>  # e.g. "Creator指示", "CCLマクロ", "自動発動"

# 入力
input:
  context: <入力コンテキスト 1-3文>
  target: <判定/検証対象>
  source_files: []      # 関連ファイルパス

# 実行トレース (最小限)
trace:
  phases_executed: []   # e.g. ["STEP0", "STEP0.5", "CONFLICT", "VERDICT"]
  tools_called: <int>   # ツール呼び出し回数
  duration_sec: <float> # 概算実行時間

# 出力
output:
  verdict: <PASS|FAIL|HOLD|ABSORBED|NATURALIZED>
  confidence: <0-100>
  confidence_label: <確信|推定|仮説>
  summary: <1-3文の要約>
  key_findings: []      # 主要発見リスト

# メタ
tags: []                # 自由タグ
drift: <0.0-1.0>        # η/ε から算出
linked_handoff: <handoff_ファイル名>
```

---

## 書き出しタイミング

| WF | タイミング | 条件 |
|:---|:----------|:-----|
| `/dia+` | VERDICT 確定後 | 常時 |
| `/dia` | VERDICT 確定後 | 任意 (Creator指定時) |
| `/dia-` | — | スキップ |
| `/vet` | 検証完了後 | 常時 |
| `/noe+` | Phase 6 完了後 | 常時 |
| `/eat+` | 消化レポート書き出し後 | 常時 |

---

## 命名規則

```
checkpoint_<wf>_<YYYY-MM-DD>_<4桁hex>.yaml

例:
checkpoint_dia+_2026-02-12_a3f1.yaml
checkpoint_vet_2026-02-12_b7c2.yaml
```

---

## 参照方法

```bash
# 直近のチェックポイントを確認
ls -lt ~/oikos/mneme/.hegemonikon/checkpoints/ | head -5

# 特定WFのチェックポイントを検索
grep -l "workflow: /dia+" ~/oikos/mneme/.hegemonikon/checkpoints/*.yaml
```

---

*Checkpoint Schema v1.0 — 2026-02-12*
