---
description: "直す — C:{/dia+_/ene+}_I:[pass]{M:{/dox-}}"
---

# /ccl-fix: 修正サイクルマクロ

> **CCL**: `@fix = C:{/dia+_/ene+}_I:[pass]{M:{/dox-}}`
> **用途**: 問題を見つけて直すサイクルを収束まで回す

## 展開

1. `C:{/dia+_/ene+}` — 診断→修正を収束ループ
2. `_I:[pass]{M:{/dox-}}` — 収束したら Doxa に記憶

## 使用例

```ccl
@fix                       # 収束まで修正
@fix _ @vet                # 修正後に自己検証
```
