---
description: "[CCL Macro] 問いの深化 — @nous = @reduce{F:[×2]{/u+*^/u^}}_@memoize{/dox-}"
---

# /ccl-nous: 問いの深化マクロ (νοῦς)

> **CCL**: `@nous = @reduce{F:[×2]{/u+*^/u^}}_@memoize{/dox-}`
> **用途**: 再帰的に深く問いたいとき

## 展開

1. `F:[×2]{/u+*^/u^}` — 「主観→メタ融合→メタ主観」を2回反復
2. `@reduce{...}` — 各反復の結果を累積融合（問いの蓄積）
3. `_@memoize{/dox-}` — 問いの深化結果を Doxa に軽量キャッシュ

## 使用例

```ccl
@nous                      # 標準問い（2回再帰）
@nous+                     # 詳細問い
@nous _ @learn             # 問い直し後に永続化
```

## CPL 構文

`@reduce`, `F:[×N]{}`, `@memoize`, `*^`
