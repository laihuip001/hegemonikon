---
description: Basanos L2 構造的差分スキャンを実行し、deficit を検出して問いに変換する。
hegemonikon: Basanos
modules: [A2]
triggers: ["basanos", "構造チェック", "deficit", "整合性"]
derivatives:
  "+": "全 deficit タイプスキャン + 問い生成 + 重要度ソート"
  "-": "epsilon のみクイックチェック"
  "~": "前回結果との差分比較"
lcm_state: beta
version: "1.0"
---

# /basanos — 構造的差分スキャン

> **定理**: A2 Krisis (判断) の τ層サブWF
> **目的**: kernel/ と mekhane/ の構造的整合性を検証し、deficit を検出する

## 事前条件

- `/boot` 済みのセッション、またはプロジェクトルートが `~/oikos/hegemonikon`

## 手順

### 1. スキャン実行

```bash
// turbo
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -m mekhane.basanos.l2.cli scan
```

### 2. 結果の評価

出力を確認し、deficit の種類と深刻度を評価する:

| 種類 | 意味 | 対応アクション |
|------|------|--------------|
| **η deficit** | 外部知識が未吸収 | `/eat` で消化 |
| **ε-impl** | 実装/WF がない | `/ene` で実装 |
| **ε-just** | 学術的根拠がない | `/sop` で調査 |
| **Δε/Δt** | 変更で整合性が崩れた | 差分を確認して修正 |

### 3. 問い生成 (派生 `+` のみ)

```bash
// turbo
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -m mekhane.basanos.l2.cli questions --limit 5
```

### 4. 対応判断

- deficit が 0 件: ✅ 構造的整合性が保たれている
- deficit が 1-3 件: 個別に対応を検討
- deficit が 4+ 件: `/plan` で対応計画を策定

## 派生

| 派生 | 動作 |
|------|------|
| `/basanos+` | 全タイプスキャン + 問い生成 + 優先度ソート |
| `/basanos-` | epsilon タイプのみ (高速チェック) |
| `/basanos~` | 前回結果との差分 (Δε/Δt のみ) |
