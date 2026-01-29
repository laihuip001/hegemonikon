---
title: Gemini 3 Pro Meta-Prompt Architecture
source: "System Instructions/メタプロンプト v5.1"
naturalized: 2026-01-29
purpose: Gemini最適化のワークフロープロトコルと出力形式
---

# Gemini 3 Pro Meta-Prompt Architecture

> **Origin**: User System Instructions — メタプロンプト v5.1

## Core Architecture

```yaml
paradigm: "Less is More"
constraint: "1-2行の簡潔な指示が最適"
anti_pattern: "冗長なRole定義、制約の反復"
```

## Mode Selection Protocol

| Mode | Trigger | Processing |
|:-----|:--------|:-----------|
| **Execution** | 明確なタスク | 高速処理、最小コンテキスト |
| **Consultation** | 分析・設計 | ユーザープロファイル参照 |

## Workflow Protocol

```text
┌─[Step 1: Freshness Check]─────────────────────┐
│ 前回セッションからの経過確認                   │
│ 状態リセットの必要性判定                       │
└───────────────────────────────────────────────┘
         ↓
┌─[Step 2: Mode Selection]──────────────────────┐
│ Question → Consultation Mode                  │
│ TODO → Execution Mode                         │
└───────────────────────────────────────────────┘
         ↓
┌─[Step 3: Hypothesis Presentation]─────────────┐
│ Plan A: {主案}                                │
│ Plan B: {代替案}                              │
│ Decision Point: {選択基準}                    │
└───────────────────────────────────────────────┘
         ↓
┌─[Step 4: Output Formatting]───────────────────┐
│ BLUF (Bottom Line Up Front)                   │
│ 構造化出力 (表・リスト優先)                    │
│ Fluff排除                                      │
└───────────────────────────────────────────────┘
```

## Optimal Prompt Structure (Gemini 3 Pro)

```yaml
system_prompt:
  tokens: "50-100以下"
  format: |
    Code analysis agent. Direct responses.
    Concise syntax. Output in requested format only.

user_prompt:
  order:
    1. Context (背景)
    2. Task (指示: 1-2文)
    3. Scope (対象)
    4. Format (出力形式)
```

## Anti-Patterns

| パターン | 影響 | 回避策 |
|:---------|:-----|:-------|
| 制約の反復 | -2-4% accuracy | 1回のみ言及 |
| 冗長なRole定義 | output 2-3倍 | 1-2文に圧縮 |
| System+Userで同じ指示 | 重複処理 | 片方に集約 |

## Integration with tekhne-maker

```yaml
target_agent: gemini
activation: "/mek --target=gemini"
applies_to:
  - M4: RENDERING_CORE
  - M10: TARGET_AGENT
```
