---
description: "[CCL Macro] 組む — 設計→実装→検証→記録の一気通貫"
---

# /ccl-build: 構築マクロ

> **CCL**: `@build = @partial{/bou-, goal:define}_/s+_@scoped{/ene+}_@validate{/dia-}_I:[pass]{@memoize{/dox-}}`
> **用途**: 0から作る。設計→実装→検証→記録の一気通貫
> **圏論**: @eat (外→内: 消化) の随伴。内→外の具現化 = 自然関手

## 展開

1. `@partial{/bou-, goal:define}` — 目的に goal:define を部分適用して軽量定義
2. `_/s+` — 戦略を詳細化
3. `_@scoped{/ene+}` — 実装スコープを限定して詳細実行
4. `_@validate{/dia-}` — 軽量判定で事後検証
5. `_I:[pass]{@memoize{/dox-}}` — 成功時のみ Doxa を軽量記録

## 使用例

```ccl
@build                     # 標準構築
@build+                    # 全WFを+で詳細展開
@build _ @v                # 構築後に自己検証
F:[api,ui,db]{@build}      # 3コンポーネントそれぞれに構築
```

## CPL 構文

`@partial`, `@scoped`, `@validate`, `I:`, `@memoize`
