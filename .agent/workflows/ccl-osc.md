---
description: "[CCL Macro] 揺する — 全Series多角振動"
---

# /ccl-osc: 多角振動マクロ

> **CCL**: `@osc = @reduce{F:[/s,/dia,/noe]{L:[x]{x~x+}}, ~(/h*/k)}`
> **用途**: 複数の認知 Series を巡回し、結果を累積融合

## 展開

1. `F:[/s,/dia,/noe]{L:[x]{x~x+}}` — S, A, O の各WFに Lambda（振動+深化）を適用
2. `@reduce{..., ~(/h*/k)}` — 結果を累積融合し、H×K の振動と統合

## 使用例

```ccl
@osc                       # 標準振動 (S-A-O + H×K)
@osc+                      # 詳細振動
@osc _ /dia                # 振動後に判定
```

## CPL 構文

`@reduce`, `F:[A,B]{}`, `L:[x]{}`, `~`, `*`
