---
description: "[CCL Macro] 刻む — 学びを次のセッションに残す"
---

# /ccl-learn: 学習永続化マクロ

> **CCL**: `@learn = /dox+_*^/u+_@memoize{/bye+}`
> **用途**: 今の学びを次のセッションに残したいとき

## 展開

1. `/dox+` — 信念を詳細化
2. `_*^/u+` — 対話のメタ融合
3. `_@memoize{/bye+}` — 詳細ハンドオフで永続化（キャッシュ/セッション横断）

## 使用例

```ccl
@learn                     # 標準学習永続化
@learn+                    # 全WFを+で展開
@learn _ @v                # 永続化した内容を自己検証
```

## CPL 構文

`@memoize`, `*^`
