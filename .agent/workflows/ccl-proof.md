---
description: "裁く — V:{/noe{axiom:FEP}~/dia}_I:[confidence=1]{/ene{output:PROOF.md}}_E:{/ene{action:move, to:_limbo/}}"
---

# /ccl-proof: 存在証明マクロ

> **CCL**: `@proof = V:{/noe{axiom:FEP}~/dia}_I:[confidence=1]{/ene{output:PROOF.md}}_E:{/ene{action:move, to:_limbo/}}`
> **用途**: ファイル/ディレクトリの存在理由を証明

## 展開

1. `V:{/noe{axiom:FEP}~/dia}` — FEP公理から認識→判定を検証
2. `I:[confidence=1]{/ene{output:PROOF.md}}` — 確信あれば PROOF.md 出力
3. `E:{/ene{action:move, to:_limbo/}}` — なければ _limbo/ に移動

## 使用例

```ccl
@proof                     # 標準存在証明
F:[dir1,dir2]{@proof}      # 複数ディレクトリに適用
```
