---
description: "揺する — R:{F:[/s,/dia,/noe]{L:[x]{x~x+}}, ~(/h*/k)}"
lcm_state: "beta"
version: "1.0.0"
---

# /ccl-osc: 多角振動マクロ

> **CCL**: `@osc = R:{F:[/s,/dia,/noe]{L:[x]{x~x+}}, ~(/h*/k)}`
> **用途**: 複数の認知 Series を巡回し、結果を累積融合

## 展開

1. `F:[/s,/dia,/noe]{L:[x]{x~x+}}` — S, A, O の各WFに振動+深化を適用
2. `R:{..., ~(/h*/k)}` — 結果を累積融合し、H×K と振動統合

## 使用例

```ccl
@osc                       # 標準振動 (S-A-O + H×K)
@osc _ /dia                # 振動後に判定
```
