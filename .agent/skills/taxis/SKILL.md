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
  - "morphism"

risk_tier: "L1"
risks:
  - "分類ミスによる優先順位の歪み"

reversible: true
requires_approval: false
fallbacks:
  - "Manual intervention"
---

# Taxis Classifier

> **目的**: ワークフロー間の関係 (morphism) を解析し、タスクの構造を可視化する。

## Overview

Taxis はワークフロー間の依存関係 (trigonon) を解析し、タスクの分類・優先順位付け・射の提案を行う。入力テキストやタスクリストから最適なルーティング先を判定する。

## Core Behavior

- WF ディレクトリから morphism (射) を自動解析
- trigonon (三角関係: bridge/anchor) からワークフロー間の接続を可視化
- タスク入力を O/S/H/P/K/A の6系統に分類してルーティング
- Fallback: 分類不能な場合は Creator に確認要求

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

## Quality Standards

- 全 WF の trigonon が正しくパースされること
- ルーティング精度: 分類結果が Creator の意図と一致すること
- 解析時間: < 5秒

## Edge Cases

- **WF にfrontmatter がない**: スキップして警告
- **trigonon が未定義**: bridge/anchor なしとして処理
- **循環依存**: 検出して警告を出力

## Examples

**入力**: `morphism_proposer.py mek`

**出力**:

```
WF: /mek (S2 Mekhanē)
  Bridge → H: /pro, /pis, /ore, /dox
  Bridge → K: /euk, /chr, /tel, /sop
  Anchor: O, P
```

---

*v1.2 — Quality Scorer 対応セクション追加 (2026-02-11)*
