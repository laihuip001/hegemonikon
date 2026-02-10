---
name: Taxis Classifier
description: "\u30BF\u30B9\u30AF/\u5165\u529B\u306E\u81EA\u52D5\u5206\u985E\u30FB\u512A\
  \u5148\u9806\u4F4D\u4ED8\u3051"
triggers:
- "\u5206\u985E"
- "\u512A\u5148"
- "\u30BF\u30B9\u30AF"
- taxis
- "\u632F\u308A\u5206\u3051"
- TODO
- "\u6574\u7406"
- morphism
risk_tier: L1
reversible: true
requires_approval: false
risks: []
fallbacks: []
---

# Taxis Classifier

> **目的**: ワークフロー間の関係 (morphism) を解析し、タスクの構造を可視化する。

## 発動条件

- タスク間の依存関係を知りたい時
- WF の分類・優先順位付け
- /tak ワークフロー実行時

## 手順

### Step 1: WF ディレクトリから morphism を解析

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/taxis/morphism_proposer.py
```

### Step 2: 特定 WF の trigonon (三角関係) を解析

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.taxis.morphism_proposer import parse_trigonon
from pathlib import Path
result = parse_trigonon(Path('.agent/workflows/WF_NAME.md'))
if result:
    print(f'WF: {result[\"name\"]}')
    print(f'Modules: {result.get(\"modules\", [])}')
    print(f'Derivatives: {result.get(\"derivatives\", [])}')
"
```

> ⚠️ `WF_NAME` を実際の WF ファイル名に置換。

### Step 3: 分類結果に基づいてルーティング

| 分類 | ルーティング先 |
|:---|:---|
| 認知系 (O/S/H) | /noe, /dia 等 |
| 環境系 (P/K) | /sop, /chr 等 |
| 精密系 (A) | /dia+, /epi 等 |

---

*v1.1 — import パス検証済み (2026-02-08)*
