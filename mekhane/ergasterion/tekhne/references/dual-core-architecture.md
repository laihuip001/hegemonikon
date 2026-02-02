---
title: Dual-Core Strategy Architecture
source: "System Instructions/Dual-Core Strategy v7.1"
naturalized: 2026-01-29
purpose: Gemini 3 Pro と Claude Opus 4.5 の役割分担と相互補完パターン
---

# Dual-Core Strategy Architecture

> **Origin**: User System Instructions — Dual-Core Strategy v7.1

## Core Principle

| Engine | Role | Strength |
|:-------|:-----|:---------|
| **E1 Gemini** | CodeAct | 検証可能な実行、コード生成、高速推論 |
| **E2 Claude** | DeepThought | 弁証法的推論、深い分析、ニュアンス理解 |

## Module Architecture (M0-M4)

```yaml
M0_IGNITION:
  purpose: "セッション開始時の鮮度確認"
  components:
    - LLM_Freshness: "前回セッションからの状態確認"
    - Cognitive_State: "Dopamine状態のベースライン"
    - Archetype_Switch: "Gemini=Precision, Claude=Creative"

M1_INTAKE:
  purpose: "入力解析と意図分類"
  modes:
    - QUESTION: "概念/Why/How → E2に委譲"
    - TODO: "明確なタスク → E1で処理"
    - CRISIS: "緊急対応 → 役割固定"

M2_PROCESSING:
  purpose: "実処理層"
  hypothesis_driven:
    format: "Plan A / Plan B 提示"
    rule: "曖昧さを許容しない"

M3_VALIDATION:
  purpose: "出力検証"
  gates:
    - Hypothesis_check: "仮説形式になっているか"
    - BLUF_check: "結論が冒頭にあるか"
    - Fluff_check: "冗長な挨拶・謝罪がないか"

M4_ROUTING:
  purpose: "継続判断"
  options:
    - commit: "完了として確定"
    - iterate: "追加質問で精緻化"
    - escalate: "人間に判断を委ねる"
```

## Engine Selection Logic

```python
def select_engine(task):
    if task.requires_verification:
        return "E1_Gemini"  # CodeAct
    if task.requires_nuance or task.is_philosophical:
        return "E2_Claude"  # DeepThought
    if task.is_urgent:
        return "E1_Gemini"  # Speed priority
    return "E2_Claude"  # Default to depth
```

## Integration Points

- **M0**: `/boot` フェーズで発動
- **M1**: 入力解析時に自動判定
- **M2-M3**: 各処理フェーズで適用
- **M4**: `/bye` フェーズでルーティング確定
