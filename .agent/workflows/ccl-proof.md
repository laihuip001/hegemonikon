---
description: "[CCL Macro] 裁く — FEPからの存在証明"
---

# /ccl-proof: 存在証明マクロ

> **CCL**: `@proof = @validate{/noe{axiom:FEP}~/dia}_I:[confidence=1]{/ene{output:PROOF.md}}_E:{/ene{action:move, to:_limbo/}}`
> **用途**: ファイル/ディレクトリの存在理由を証明

## 展開

1. `@validate{/noe{axiom:FEP}~/dia}` — FEP公理から認識し、判定と振動を検証ゲートにかける
2. `I:[confidence=1]{/ene{output:PROOF.md}}` — 確信あれば PROOF.md を出力
3. `E:{/ene{action:move, to:_limbo/}}` — なければ _limbo/ に移動

## 使用例

```ccl
@proof                     # 標準存在証明
@proof+                    # 詳細証明（全WFを+）
F:[dir1,dir2]{@proof}      # 複数ディレクトリに適用
```

## CPL 構文

`@validate`, `I:`, `E:`, `~`
