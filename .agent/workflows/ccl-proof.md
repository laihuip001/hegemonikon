---
description: "裁く — V:{/noe~/dia}_I:[pass]{/ene{PROOF.md}}_E:{/ene{_limbo/}}"
---

# /ccl-proof: 存在証明マクロ

> **CCL**: `@proof = V:{/noe~/dia}_I:[pass]{/ene{PROOF.md}}_E:{/ene{_limbo/}}`
> **用途**: ファイル/ディレクトリの存在理由を証明
> **暗黙**: FEP 公理を前提。confidence=1 → pass

## 展開

1. `V:{/noe~/dia}` — 認識→判定を検証
2. `I:[pass]{/ene{PROOF.md}}` — 通過すれば PROOF.md 出力
3. `E:{/ene{_limbo/}}` — 不通過なら _limbo/ に移動

## 使用例

```ccl
@proof                     # 標準存在証明
F:[dir1,dir2]{@proof}      # 複数ディレクトリに適用
```
