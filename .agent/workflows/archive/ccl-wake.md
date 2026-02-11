---
description: "[CCL Macro] セッション開始 — @wake = /boot+_@dig_@plan"
---

# /ccl-wake: セッション開始マクロ

> **CCL**: `@wake = /boot+_@dig_@plan`
> **用途**: セッション開始時の完全シーケンス

## 展開

1. `/boot+` — 詳細ブート
2. `_@dig` — 深掘り（状況把握）
3. `_@plan` — 計画策定

## 使用例

```ccl
@wake             # 朝の完全起動
/boot _ @plan     # 軽量版起動
```
