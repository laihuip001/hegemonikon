---
description: "[CCL Macro] 確かめる — 実装後の構造的自己検証"
---

# /ccl-v: 自己検証マクロ

> **CCL**: `@v = @scoped{/kho{git_diff}}_@cycle{@validate{/dia+}_/ene+}_/pra{test}_@memoize{/pis_/dox}`
> **用途**: 実装完了後の構造的自己検証

## 展開

1. `@scoped{/kho{git_diff}}` — git diff でスコープを限定
2. `@cycle{@validate{/dia+}_/ene+}` — 検証→修正の収束ループ（dia+ を検証ゲートとして）
3. `_/pra{test}` — テスト実行
4. `_@memoize{/pis_/dox}` — 確信度と発見パターンをキャッシュ永続化

## 使用例

```ccl
@v                         # 標準検証
@v+                        # 全WFを+で詳細展開
F:[×3]{@v}                 # 3回ループ検証
@v _ /dia+                 # 検証後に敵対的レビュー
```

## CPL 構文

`@scoped`, `@cycle`, `@validate`, `@memoize`
