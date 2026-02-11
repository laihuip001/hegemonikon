---
description: "[CCL Macro] 計画策定 — @plan = /bou+_/s+_/dia"
version: "1.0"
lcm_state: stable
---

# /ccl-plan: 計画策定マクロ

> **CCL**: `@plan = /bou+_/s+_/dia`
> **用途**: 何かを始める前に計画を練りたいとき

## 展開

1. `/bou+` — 意志を詳細化（何がしたい？）
2. `_/s+` — 戦略を詳細化（どうやる？）
3. `_/dia` — 批判で妥当性チェック

## 使用例

```ccl
@plan             # 標準計画
@plan^            # 計画自体をメタ分析
```
