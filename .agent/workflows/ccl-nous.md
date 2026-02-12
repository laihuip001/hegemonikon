---
lcm_state: "beta"
version: "1.0"
description: "問う — R:{F:[×2]{/u+*^/u^}}_/dox-"
---
lcm_state: "beta"
version: "1.0"

# /ccl-nous: 問いの深化マクロ (νοῦς)

> **CCL**: `@nous = R:{F:[×2]{/u+*^/u^}}_/dox-`
> **用途**: 再帰的に深く問いたいとき

## 展開

1. `F:[×2]{/u+*^/u^}` — 主観→メタ融合→メタ主観を2回反復
2. `R:{...}` — 各反復の結果を累積融合
3. `_/dox-` — 結果を Doxa に記憶

## 使用例

```ccl
@nous                      # 標準問い（2回再帰）
@nous _ @learn             # 問い直し後に永続化
```
