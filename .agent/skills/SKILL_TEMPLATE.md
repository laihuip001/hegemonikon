---
name: "<skill-name>"
description: "<1行で目的を記述>"
activation: auto | manual
triggers: []
hegemonikon: "<関連定理 (例: O1 Noēsis)>"

# Safety Contract (v1.0)
# Anti-Confidence 原則: リスクを宣言しないスキルは信頼できない
risk_tier: L0             # L0(安全) | L1(低) | L2(中) | L3(高)
reversible: true           # 出力が可逆か (true/false)
requires_approval: false   # 実行前に Creator 承認が必要か
risks:                     # 想定リスクのリスト (最低1つ記載)
  - "<リスク1>"
fallbacks:                 # 失敗時の代替 Skill
  - "<代替skill名 or 空>"
---

# <Skill Name>

> **目的**: ...
> **発動**: ...

---

## 手順

1. ...
2. ...
3. ...

---

## 失敗しやすい点

- ...

---

## 例

- ...
