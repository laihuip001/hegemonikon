---
name: Poiema Generator
description: 構造化出力の生成 (Boot レポート, Handoff, 定型ドキュメント)
triggers:
  - "生成"
  - "レポート"
  - "Handoff"
  - "出力"
  - "poiema"
  - "テンプレート"
  - "ドキュメント生成"

# Safety Contract
risk_tier: L1
reversible: true
requires_approval: false
risks:
  - "意図しないアーティファクト生成"
fallbacks:
  - "manual-creation"
---

# Poiema Generator

> **目的**: 構造化された出力を生成する。Boot レポート、Handoff、定型ドキュメント等。

## 発動条件

- 構造化出力の生成が必要な時
- /bye での Handoff 生成時
- /boot での Boot レポート生成時

## 手順

### Step 1: テンプレートベース生成

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.poiema import generate
# テンプレート一覧
import os
templates = os.listdir('mekhane/poiema/') if os.path.isdir('mekhane/poiema/') else []
print('Available templates:', [t for t in templates if t.endswith('.md') or t.endswith('.yaml')])
"
```

### Step 2: Handoff 生成 (/bye 用)

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.symploke.boot_integration import get_boot_context
ctx = get_boot_context()
print(f'Boot context loaded: {len(ctx)} items')
"
```

---

*v1.0 — 全PJ IDE配線 (2026-02-08)*
