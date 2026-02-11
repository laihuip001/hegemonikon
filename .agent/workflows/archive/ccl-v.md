---
description: "[CCL Macro] 自己検証 — @v = /kho{git_diff}_@fix_/pra{test}_/pis_/dox"
---

# /ccl-v: 自己検証マクロ

> **CCL**: `@v = /kho{git_diff} _ @fix _ /pra{test} _ /pis _ /dox`
> **用途**: 実装完了後の構造的自己検証

## 展開

1. `/kho{git_diff}` — スコープ検出 (P1 Khōra)
2. `@fix` — 5角度スキャン→修正→再批判
3. `/pra{test}` — テスト実行 (S4 Praxis)
4. `/pis` — 確信度検証 (H2 Pistis)
5. `/dox` — 発見パターンの永続化 (H4 Doxa)

## 使用例

```ccl
@v               # 標準検証
@v+              # 詳細検証
F:3{@v}          # 3回ループ検証
```
