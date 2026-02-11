---
description: "[CCL Macro] 即実行 — @go = /s+_/ene+"
lcm_state: stable
version: "1.0.0"
---

# /ccl-go: 即実行マクロ

> **CCL**: `@go = /s+_/ene+`
> **用途**: 考えすぎず、すぐ動きたいとき

## 展開

1. `/s+` — 戦略を詳細化（計画）
2. `_/ene+` — 即座に詳細実行

## 使用例

```ccl
@go               # シンプルに実行へ
@plan _ @go       # 計画後に実行
```
