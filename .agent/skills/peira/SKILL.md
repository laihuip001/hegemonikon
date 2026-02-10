---
name: Peira Health Check
description: "\u30B7\u30B9\u30C6\u30E0\u5168\u4F53\u306E\u30D8\u30EB\u30B9\u30C1\u30A7\
  \u30C3\u30AF\u30FB\u5065\u5168\u6027\u78BA\u8A8D"
triggers:
- "\u30D8\u30EB\u30B9"
- "\u5065\u5168"
- health
- "\u72B6\u614B"
- peira
- "\u52D5\u4F5C\u78BA\u8A8D"
- "\u30C6\u30B9\u30C8"
risk_tier: L1
reversible: true
requires_approval: false
risks: []
fallbacks: []
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
