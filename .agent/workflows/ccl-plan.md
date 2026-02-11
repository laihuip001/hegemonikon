---
description: "[CCL Macro] 段取る — 目的→戦略→検証"
---

# /ccl-plan: 計画策定マクロ

> **CCL**: `@plan = /bou+_/s+~(/p*/k)_@validate{/dia}`
> **用途**: 何かを始める前に計画を練りたいとき

## 展開

1. `/bou+` — 意志を詳細化
2. `_/s+~(/p*/k)` — 戦略を環境×文脈と振動融合
3. `_@validate{/dia}` — 判定で事後検証ゲート

## 使用例

```ccl
@plan                      # 標準計画
@plan+                     # 全WFを+で展開
@plan _ @build             # 計画後に構築
```

## CPL 構文

`@validate`, `~`, `*`
