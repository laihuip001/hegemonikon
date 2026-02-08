---
name: Synteleia WBC
description: 安全性チェック・白血球 (WBC) による不正操作検知
triggers:
  - "安全"
  - "安全性"
  - "リスク"
  - "白血球"
  - "WBC"
  - "synteleia"
  - "免疫"
  - "検証"
risk_tier: L2
risks:
  - security_bypass
  - false_positive
reversible: true
requires_approval: true
fallbacks:
  - manual_check
---

# Synteleia WBC (白血球)

> **目的**: システムの免疫系。操作の安全性を検証し、不正操作を検知する。

## 発動条件

- 破壊的操作 (ファイル削除、大規模変更) の前
- WF/Skill の変更時
- セキュリティ関連の確認

## 手順

### Step 1: 安全性チェック

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.synteleia.wbc import WhiteBloodCell
wbc = WhiteBloodCell()
result = wbc.check('OPERATION_DESCRIPTION')
print(result)
"
```

> ⚠️ `OPERATION_DESCRIPTION` を実際の操作内容に置換。

### Step 2: リスク判定

| リスク | アクション |
|:---|:---|
| LOW | 続行 |
| MEDIUM | Creator に確認 |
| HIGH | **停止**、理由を報告 |

---

*v1.0 — 全PJ IDE配線 (2026-02-08)*
