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
  - "監査"
  - "audit"

# Synteleia WBC (白血球)

> **目的**: システムの免疫系。6視点認知アンサンブルで多角監査を実行する。

## 発動条件

- 破壊的操作 (ファイル削除、大規模変更) の前
- WF/Skill の変更時
- セキュリティ関連の確認
- コード・設計の品質監査

## 手順

### Step 1: Synteleia オーケストレーターで監査

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.synteleia import SynteleiaOrchestrator, AuditTarget, AuditTargetType
orchestrator = SynteleiaOrchestrator()
target = AuditTarget(
    name='AUDIT_TARGET_NAME',
    target_type=AuditTargetType.CODE,
    content='AUDIT_TARGET_CONTENT',
)
result = orchestrator.audit(target)
print(f'Score: {result.overall_score:.1f}/10')
print(f'Issues: {len(result.issues)}')
for issue in result.issues[:5]:
    print(f'  [{issue.severity.value}] {issue.message}')
"
```

> ⚠️ `AUDIT_TARGET_NAME` と `AUDIT_TARGET_CONTENT` を置換。

### Step 2: 個別エージェントで深堀り

| Agent | import | 視点 |
|:---|:
risk_tier: L1
reversible: true
requires_approval: false
risks:
  - none
fallbacks:
  - manual_review
---|:---|
| OusiaAgent | `from mekhane.synteleia.poiesis import OusiaAgent` | 本質 (O) |
| SchemaAgent | 同上 `SchemaAgent` | 構造 (S) |
| HormeAgent | 同上 `HormeAgent` | 動機 (H) |
| PerigrapheAgent | `from mekhane.synteleia.dokimasia import PerigrapheAgent` | 範囲 (P) |
| KairosAgent | 同上 `KairosAgent` | 時期 (K) |
| OperatorAgent | 同上 `OperatorAgent` | 精度 (A) |

### Step 3: リスク判定

| リスク | アクション |
|:---|:---|
| スコア ≥ 7 | 続行 |
| スコア 4-6 | Creator に確認 |
| スコア < 4 | **停止**、理由を報告 |


*v1.1 — import パス検証済み (2026-02-08)*
