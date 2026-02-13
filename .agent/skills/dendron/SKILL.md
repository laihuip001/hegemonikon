---
name: Dendron EPT Checker
description: コード品質・存在証明 (PROOF.md) の検証を実行する
triggers:
  - "品質"
  - "PROOF"
  - "存在証明"
  - "EPT"
  - "dendron"
  - "checker"
  - "なぜ存在する"

risk_tier: "L1"
risks:
  - "検証漏れによる品質ゲート形骸化"
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
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -m mekhane.dendron check TARGET_DIR --coverage
```

> ⚠️ `TARGET_DIR` を実際のディレクトリに置換。例: `mekhane/`, `hermeneus/`, `kernel/`

### Step 2: 結果を解釈

| スコア | 意味 | アクション |
|:---|:---|:---|
| ≥ 80% | 健全 | OK |
| 50-79% | 要改善 | PROOF.md 追加を提案 |
| < 50% | 危険 | 即時対応 |

### Step 3: PROOF.md が不足している場合

// turbo

```bash
# PROOF.md スキャン (不足一覧)
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.dendron.proof_skeleton import scan_missing
for p in scan_missing('TARGET_DIR'):
    print(p)
"
```

```bash
# PROOF.md 自動生成 (dry-run)
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.dendron.proof_skeleton import scan_missing, generate_proof
for p in scan_missing('TARGET_DIR'):
    print(f'--- {p} ---')
    print(generate_proof(p))
"
```

---

*v1.0 — 全PJ IDE配線 (2026-02-08)*
*v1.1 — コマンド修正 + proof_skeleton 連携 (2026-02-13)*
