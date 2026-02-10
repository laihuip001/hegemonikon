---
risk_tier: L1
risks: []
reversible: true
requires_approval: false
fallbacks: []
name: Peira Health Check
description: システム全体のヘルスチェック・健全性確認
triggers:
  - "ヘルス"
  - "健全"
  - "health"
  - "状態"
  - "peira"
  - "動作確認"
  - "テスト"
---

# Peira Health Check

> **目的**: Hegemonikón システム全体の健全性を確認する。

## 発動条件

- セッション開始時の環境確認
- 「動いてるか」「壊れてないか」の確認
- CI/テスト実行前の事前チェック

## 手順

### Step 1: ヘルスチェックスクリプト実行

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/peira/hgk_health.py 2>&1 | tail -30
```

### Step 2: テストスイート実行

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -m pytest --tb=short -q 2>&1 | tail -10
```

---

*v1.0 — 全PJ IDE配線 (2026-02-08)*
