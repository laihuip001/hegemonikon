---
name: Dendron EPT Checker
description: "\u30B3\u30FC\u30C9\u54C1\u8CEA\u30FB\u5B58\u5728\u8A3C\u660E (PROOF.md)\
  \ \u306E\u691C\u8A3C\u3092\u5B9F\u884C\u3059\u308B"
triggers:
- "\u54C1\u8CEA"
- PROOF
- "\u5B58\u5728\u8A3C\u660E"
- EPT
- dendron
- checker
- "\u306A\u305C\u5B58\u5728\u3059\u308B"
risk_tier: L1
reversible: true
requires_approval: false
risks: []
fallbacks: []
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
