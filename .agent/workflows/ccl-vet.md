---
description: "確かめる — /kho{git_diff}_C:{V:{/dia+}_/ene+}_/pra{test}_/pis_/dox"
lcm_state: beta
version: 1.0
---

# /ccl-vet: 自己検証マクロ

> **CCL**: `@vet = /kho{git_diff}_C:{V:{/dia+}_/ene+}_/pra{test}_/pis_/dox`
> **用途**: 実装完了後の構造的自己検証

## 展開

1. `/kho{git_diff}` — git diff でスコープ特定
2. `C:{V:{/dia+}_/ene+}` — 検証→修正の収束ループ
3. `_/pra{test}` — テスト実行
4. `_/pis_/dox` — 確信度と発見パターンを記憶

## 使用例

```ccl
@vet                       # 標準検証
@vet _ /dia+               # 検証後に敵対的レビュー
```
