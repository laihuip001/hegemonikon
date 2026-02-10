---
name: Synedrion Council
description: 偉人評議会 (Synedrion) による多角的レビュー・監査
triggers:
  - "評議会"
  - "レビュー"
  - "監査"
  - "synedrion"
  - "偉人"
  - "多角"
  - "批評"
  - "/syn"

risk_tier: "L1"
risks:
  - "評議会の意見が合意バイアスに陥る"
---

# Synedrion Council

> **目的**: 偉人評議会を召喚し、多角的批評を実行する。

## Overview

Synedrion は6視点 (O/S/H/P/K/A) のAI監査エージェントを召喚し、設計・方針・コードに対する多角的レビューを実行する。合意バイアスに陥らないよう、各エージェントは独立に評価を行い、異論を明示的に記録する。

## Core Behavior

- AI 監査モードで多角的批評を実行
- 6視点 (本質/構造/動機/範囲/時期/精度) から独立評価
- 合意バイアス回避: 全エージェントの異論を明示的に記録
- Fallback: モジュール不在時は /dia+ による手動レビューにエスカレーション

## 発動条件

- 設計・方針の多角的レビューが必要な時
- /syn ワークフロー実行時
- AI 監査が必要な時

## 手順

### Step 1: 評議会を召喚

AI 監査モードを使用:

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.synedrion.ai_auditor import AIAuditor
auditor = AIAuditor()
result = auditor.audit('TOPIC_OR_CODE')
print(result)
"
```

> ⚠️ `TOPIC_OR_CODE` を監査対象に置換。

### Step 2: /syn ワークフローを参照

大規模レビューには `/syn` WF を実行すること。

## Quality Standards

- 全6視点からの評価を含むこと
- 各視点のスコアが 1-10 で定量化されていること
- 異論が0件の場合は「合意バイアス警告」を出力

## Edge Cases

- **監査対象が空**: エラーメッセージで対象の指定を促す
- **エージェント実行エラー**: 失敗した視点を明示し、残りの視点で結果を返す
- **スコアが極端に割れる場合** (分散 > 3.0): Creator に追加確認を要求

## Examples

**入力**: `/syn "新しいCCLマクロの設計レビュー"`

**出力**:

```
📊 Synedrion Council Results
  O (本質): 8/10 — 表現力が高く一貫性がある
  S (構造): 7/10 — パーサーとの整合性に注意
  H (動機): 9/10 — ユーザーニーズに合致
  P (範囲): 6/10 — 影響範囲が広い、段階的導入を推奨
  K (時期): 7/10 — 現時点で導入可能
  A (精度): 5/10 — テストケースが不足
  異論: P, A — "範囲が広すぎる、テスト先行すべき"
```

---

*v1.1 — Quality Scorer 対応セクション追加 (2026-02-11)*
