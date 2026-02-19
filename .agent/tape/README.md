# .agent/tape/ — WF 実行トレースログ

> **Origin**: TapeAgents (arXiv 2602.12430, 2026-02) — WF 実行を不変テープとして記録
> **連携**: Canvas-CoT ノード操作 (tekhne/SKILL.md M2) + Dispatch Log (bye.md Step 3.6)

## 目的

WF 実行中の思考ノード操作を JSONL 形式で記録し、以下を可能にする:

1. **再現性**: どの WF がどのノードを生成・修正・削除したか
2. **デバッグ**: 判断の根拠を遡って確認
3. **学習**: パターンの蓄積 (patterns.yaml との連携)

## ファイル形式

```
tape_YYYY-MM-DD_HHMM.jsonl
```

各行が独立した JSON オブジェクト:

```jsonl
{"ts":"2026-02-19T00:30:00Z","wf":"/noe+","step":"EXPANSION","nodes_created":["H1","H2","H3"]}
{"ts":"2026-02-19T00:31:00Z","wf":"/noe+","step":"CONFLICT","crud":{"action":"modify","target":"H2","reason":"反証あり"}}
{"ts":"2026-02-19T00:32:00Z","wf":"/noe+","step":"CONVERGENCE","active_nodes":["H1","H3"],"confidence":85}
```

## エントリスキーマ

| フィールド | 型 | 必須 | 説明 |
|:-----------|:---|:-----|:-----|
| `ts` | ISO 8601 | ✅ | タイムスタンプ |
| `wf` | string | ✅ | WF 名 (例: `/noe+`) |
| `step` | string | ✅ | フェーズ名 (EXPANSION/CONFLICT/CONVERGENCE) |
| `nodes_created` | string[] | — | 生成されたノード ID |
| `crud` | object | — | ノード操作 (`action`, `target`, `reason`) |
| `active_nodes` | string[] | — | 生存ノード一覧 |
| `confidence` | int | — | 確信度 (0-100) |
| `meta` | object | — | 自由形式の追加情報 |

## ライフサイクル

- **生成**: WF 実行中に Canvas-CoT ノード操作をログ
- **参照**: `/bye` Step 3.6 で Dispatch Log に統合
- **保持**: 7日間 (古いものは自動削除可)
- **分析**: パターン抽出 → patterns.yaml に反映

---

*v1.0 — TapeAgents 消化 (2026-02-19)*
