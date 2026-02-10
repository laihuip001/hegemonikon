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
  - "監査"
  - "audit"

risk_tier: "L1"
risks:
  - "WBC 偽陽性によるアラート疲れ"
  - "偽陰性による脅威の見逃し"
---

# Synteleia WBC (白血球)

> **目的**: システムの免疫系。6視点認知アンサンブルで多角監査を実行する。

## Overview

Synteleia はシステムの安全性を担保する「白血球」。破壊的操作やセキュリティに関わる変更に対して、6つの認知エージェント (O/S/H/P/K/A) による多角監査を実行し、リスクを定量化する。

## Core Behavior

- 6視点監査エージェントで多角的リスク評価を実行
- 破壊的操作の前に自動発動し、スコアベースの Go/No-Go 判定
- リスク判定に基づくアクション: 続行 / 確認要求 / 停止
- Fallback: エージェント不在時は手動リスクチェックリストを提示
- エスカレーション: スコア < 4 で即座に停止・Creator に報告

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
|:---|:---|:---|
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

## Quality Standards

- 全6視点からの評価を含むこと
- 偽陽性率: < 15% (アラート疲れ防止)
- 偽陰性率: < 5% (脅威見逃し防止)
- 監査実行時間: < 10秒

## Edge Cases

- **監査対象が空文字列**: エラーメッセージで対象の指定を促す
- **WBC 偽陽性多発**: 閾値を動的調整 (Sympatheia feedback 連携)
- **SACRED_TRUTH.md 変更検出**: threatScore=15 で即座にエスカレーション
- **エージェント実行エラー**: 最低3視点が成功すれば結果を返す

## Examples

**入力**: `orchestrator.audit(AuditTarget(name='rm -rf logs/', type=CODE))`

**出力**:

```
Score: 3.2/10
Issues: 4
  [CRITICAL] 破壊的操作: ディレクトリ削除
  [HIGH] バックアップ未確認
  [MEDIUM] ログ保持ポリシー未参照
  [LOW] dry-run 未実行
→ アクション: 停止。Creator に確認要求。
```

---

*v1.2 — Quality Scorer 対応セクション追加 (2026-02-11)*
