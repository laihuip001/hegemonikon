---
name: Dendron EPT Checker
description: コード品質・存在証明 (PROOF.md) の検証を実行する
risk_tier: L1
reversible: true
requires_approval: false
risks: []
fallbacks: []
triggers:
  - "品質"
  - "PROOF"
  - "存在証明"
  - "EPT"
  - "dendron"
  - "checker"
  - "なぜ存在する"
---

# Dendron EPT Checker

> **目的**: コードの「存在理由」を検証する。PROOF.md の有無・質を自動チェック。

## 発動条件

- コード品質・存在証明の検証が必要な時
- 新しいモジュール/ファイル追加後の検証
- `/dev` ワークフロー内での品質ゲート

## 手順

### Step 1: ターゲットの EPT スコアを確認

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python mekhane/dendron/checker.py TARGET_DIR
```

> ⚠️ `TARGET_DIR` を実際のディレクトリに置換。例: `mekhane/fep/`, `hermeneus/`

### Step 2: 結果を解釈

| スコア | 意味 | アクション |
|:---|:---|:---|
| ≥ 80% | 健全 | OK |
| 50-79% | 要改善 | PROOF.md 追加を提案 |
| < 50% | 危険 | 即時対応 |

### Step 3: PROOF.md が不足している場合

```bash
# PROOF.md 自動生成
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python scripts/generate_proofs.py TARGET_DIR
```

---

*v1.0 — 全PJ IDE配線 (2026-02-08)*
