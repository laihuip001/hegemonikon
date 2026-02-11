---
description: "[CCL Macro] 直す — 診断→修正の収束ループ"
---

# /ccl-fix: 修正サイクルマクロ

> **CCL**: `@fix = @cycle{/dia+_/ene+}_I:[pass]{@memoize{/dox-}}`
> **用途**: 問題を見つけて直すサイクルを収束まで回す

## 展開

1. `@cycle{/dia+_/ene+}` — 診断→修正を収束するまでループ
2. `_I:[pass]{@memoize{/dox-}}` — 収束（PASS）したら Doxa に軽量記録

## 使用例

```ccl
@fix                       # 収束まで修正
@fix+                      # 全WFを+で詳細展開
@fix _ @v                  # 修正後に自己検証
```

## CPL 構文

`@cycle`, `I:`, `@memoize`
