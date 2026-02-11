---
description: "[CCL Macro] 回す — OODAライクな認知サイクル"
---

# /ccl-kyc: 認知循環マクロ (κύκλος)

> **CCL**: `@kyc = @cycle{/sop_/noe_/ene_/dia-}`
> **用途**: OODA ライクな認知サイクルを収束まで回す

## 展開

1. `@cycle{/sop_/noe_/ene_/dia-}` — 観察→認識→行動→判定を収束ループ

## 使用例

```ccl
@kyc                       # 標準循環
@kyc+                      # 詳細循環（全WFを+）
@kyc _ /dox                # 循環後に信念記録
```

## CPL 構文

`@cycle`
