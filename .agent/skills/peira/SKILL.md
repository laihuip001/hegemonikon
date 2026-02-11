---
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

risk_tier: "L1"
risks:
  - "ヘルスチェック偽陽性による不要な修正作業"

reversible: true
requires_approval: false
fallbacks:
  - "Manual intervention"
---

# Peira Health Check

> **目的**: Hegemonikón システム全体の健全性を確認する。

## Overview

Peira はシステムのヘルスチェックを実行し、全モジュールの稼働状態を一覧表示する。
セッション開始時の環境確認、CI/テスト実行前の事前チェック、障害切り分けに使用する。

## Core Behavior

- ヘルスチェックスクリプト (`hgk_health.py`) を実行し、全モジュールの状態を一覧表示
- テストスイートを実行し、PASS/FAIL を判定
- エラー発生時: 障害箇所を特定し、修復手順を提案
- Fallback: スクリプト自体が動かない場合は手動確認リストを提示

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

## Quality Standards

- 全モジュール状態が `operational` であること
- テストスイートが 0 failures であること
- 実行時間: < 30秒 で完了

## Edge Cases

- **モジュール未インストール**: エラーではなく `not_installed` として報告
- **DB接続失敗**: タイムアウト後に `unreachable` として報告
- **テスト flaky**: 2回リトライで再現性を確認

## Examples

**正常時の出力**:

```
✅ Hegemonikón: operational
✅ Hermēneus: operational
✅ Synergeia: operational
Tests: 42 passed, 0 failed
```

**異常時の出力**:

```
❌ Hermēneus: error — ImportError: hermeneus.src not found
⚠️ 修復手順: pip install -e hermeneus/
```

---

*v1.1 — Quality Scorer 対応セクション追加 (2026-02-11)*
