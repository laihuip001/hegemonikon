---
name: Taxis Classifier
description: タスク/入力の自動分類・優先順位付け
triggers:
  - "分類"
  - "優先"
  - "タスク"
  - "taxis"
  - "振り分け"
  - "TODO"
  - "整理"
risk_tier: L1
risks:
  - misclassification
  - low_confidence
reversible: true
requires_approval: false
fallbacks:
  - manual_triage
---

# Taxis Classifier

> **目的**: タスク・入力を自動分類し、最適な処理パイプラインに振り分ける。

## 発動条件

- 曖昧な入力の分類が必要な時
- タスクの優先順位付け
- /tak ワークフロー実行時

## 手順

### Step 1: 入力を分類

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.taxis.morphism_proposer import propose_morphisms
result = propose_morphisms('INPUT_TEXT')
for m in result:
    print(f'{m[\"source\"]} → {m[\"target\"]}: {m[\"type\"]}')
"
```

> ⚠️ `INPUT_TEXT` を実際の入力に置換。

### Step 2: 分類結果に基づいてルーティング

| 分類 | ルーティング先 |
|:---|:---|
| 認知系 (O/S/H) | /noe, /dia 等 |
| 環境系 (P/K) | /sop, /chr 等 |
| 精密系 (A) | /dia+, /epi 等 |

---

*v1.0 — 全PJ IDE配線 (2026-02-08)*
