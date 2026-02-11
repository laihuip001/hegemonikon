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

reversible: true
requires_approval: false
fallbacks:
  - "Manual intervention"
---

# Synteleia WBC (白血球)

> **目的**: システムの免疫系。6視点認知アンサンブルで多角監査を実行する。

## Overview

Synteleia はシステムの安全性を担保する「白血球」。破壊的操作やセキュリティに関わる変更に対して、6つの認知エージェント (O/S/H/P/K/A) による多角監査を実行し、リスクを定量化する。

## Core Behavior

- 6視点監査エージェントで多角的リスク評価を実行
- 破壊的操作の前に自動発動し、Go/No-Go 判定
- リスク判定に基づくアクション: 続行 / 確認要求 / 停止
- Fallback: エージェント不在時は手動リスクチェックリストを提示
- エスカレーション: CRITICAL 検出で即座に停止・Creator に報告

## 発動条件

- 破壊的操作 (ファイル削除、大規模変更) の前
- WF/Skill の変更時
- セキュリティ関連の確認
- コード・設計の品質監査
- `/dia` ワークフロー実行時 (auto-hook)

## 手順

### Step 1: Synteleia オーケストレーターで監査

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.synteleia import SynteleiaOrchestrator, AuditTarget, AuditTargetType
orchestrator = SynteleiaOrchestrator()
target = AuditTarget(
    content='''AUDIT_TARGET_CONTENT''',
    target_type=AuditTargetType.CODE,
    source='AUDIT_TARGET_SOURCE',
)
result = orchestrator.audit(target)
print(orchestrator.format_report(result))
"
```

> ⚠️ `AUDIT_TARGET_CONTENT` と `AUDIT_TARGET_SOURCE` を置換。

### Step 2: 結果の解釈

| フィールド | 意味 |
|:----------|:-----|
| `result.passed` | bool — 全エージェント合格か |
| `result.summary` | 要約テキスト (✅ PASS / ❌ FAIL) |
| `result.all_issues` | 検出された全問題のリスト |
| `result.critical_count` | CRITICAL 件数 |
| `result.high_count` | HIGH 件数 |
| `result.agent_results` | 各エージェントの個別結果 |

### Step 3: 個別エージェントで深堀り

| Layer | Agent | import | 視点 |
|:------|:------|:-------|:-----|
| Poiēsis | OusiaAgent | `from mekhane.synteleia.poiesis import OusiaAgent` | O: 本質 |
| Poiēsis | SchemaAgent | 同上 `SchemaAgent` | S: 構造 |
| Poiēsis | HormeAgent | 同上 `HormeAgent` | H: 動機 |
| Dokimasia | PerigrapheAgent | `from mekhane.synteleia.dokimasia import PerigrapheAgent` | P: 範囲 |
| Dokimasia | KairosAgent | 同上 `KairosAgent` | K: 時期 |
| Dokimasia | OperatorAgent | 同上 `OperatorAgent` | A: 精度 |
| Dokimasia | LogicAgent | 同上 `LogicAgent` | A: 論理 |
| Dokimasia | CompletenessAgent | 同上 `CompletenessAgent` | A: 完全性 |

### Step 4: リスク判定

| 状態 | アクション |
|:-----|:----------|
| `result.passed == True` && critical == 0 | 続行 ✅ |
| `result.passed == False` && critical == 0 | Creator に確認 ⚠️ |
| `result.critical_count > 0` | **停止** 🛑、理由を報告 |

### Step 5: 高速監査モード (LogicAgent のみ)

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.synteleia import SynteleiaOrchestrator, AuditTarget, AuditTargetType
orchestrator = SynteleiaOrchestrator()
target = AuditTarget(content='''CONTENT''', target_type=AuditTargetType.CODE)
result = orchestrator.audit_quick(target)
print(orchestrator.format_report(result))
"
```

### Step 6: API 経由での監査

```bash
curl -X POST http://localhost:21517/api/synteleia/audit \
  -H "Content-Type: application/json" \
  -d '{"content": "AUDIT_CONTENT", "target_type": "code"}'
```

## /dia 連携 (auto-hook)

`/dia` ワークフロー実行時、以下の条件で Synteleia が自動発動:

- `/dia+` (詳細レビュー) → 全8エージェント実行
- `/dia` (標準レビュー) → LogicAgent + OperatorAgent のみ
- `/dia-` (簡易レビュー) → LogicAgent のみ (`audit_quick`)

## Sympatheia WBC 連携

Sympatheia の `sympatheia_wbc` ツールと連携:

1. Synteleia で監査結果を取得
2. `result.critical_count > 0` の場合、WBC アラートを送信
3. アラート頻度が高い場合、Sympatheia feedback で閾値を動的調整

## Quality Standards

- 全6視点からの評価を含むこと (8エージェント)
- 偽陽性率: < 15% (アラート疲れ防止)
- 偽陰性率: < 5% (脅威見逃し防止)
- 監査実行時間: < 1秒 (39テスト 0.07秒達成済み)

## Edge Cases

- **監査対象が空文字列**: content が空の場合は INFO で報告
- **WBC 偽陽性多発**: 閾値を動的調整 (Sympatheia feedback 連携)
- **SACRED_TRUTH.md 変更検出**: threatScore=15 で即座にエスカレーション
- **エージェント実行エラー**: 最低3視点が成功すれば結果を返す

## Examples

**入力**:

```python
target = AuditTarget(
    content="rm -rf logs/ && echo done",
    target_type=AuditTargetType.CODE,
    source="user_command"
)
result = orchestrator.audit(target)
```

**出力**:

```
============================================================
Hegemonikón Audit Report
============================================================

Target: code
Status: ❌ FAIL — 1 critical, 2 high issues

--- OusiaAgent ---
Passed: ✅
Confidence: 75%

--- LogicAgent ---
Passed: ❌
Confidence: 80%
Issues (1):
  🔴 [LOG-030] 破壊的操作: ディレクトリ削除
      💡 dry-run で事前確認を推奨

→ アクション: 停止。Creator に確認要求。
```

---

*v2.0 — API 例を実コードに修正、/dia 連携・WBC 連携追加 (2026-02-11)*
