---
description: "[CCL Macro] 修正サイクル — @fix = /dia+_/ene+_/dia"
version: 1.0.0
lcm_state: beta
---

version: 1.0.0
lcm_state: beta
# /ccl-fix: 修正サイクルマクロ

> **CCL**: `@fix = /dia+_/ene+_/dia`
> **用途**: 問題を見つけて直すサイクル

## 展開

1. `/dia+` — 詳細な批判（問題発見）
2. `_/ene+` — 詳細な修正実行
3. `_/dia` — 再批判（修正確認）

## 使用例

```ccl
@fix              # 1回修正
F:3{@fix}         # 3回繰り返し修正
```
