---
lcm_state: stable
version: "1.0.0"
description: "[CCL Macro] 存在証明 — @proof = /noe{axiom:FEP}~/dia_I:confidence=1{/ene{output:PROOF.md}}"
---

# /ccl-proof: 存在証明マクロ

> **CCL**: `@proof = /noe{axiom:FEP}~/dia _ I:confidence=1{/ene{output:PROOF.md}} _ E:{/ene{action:move, to:_limbo/}}`
> **用途**: ファイル/ディレクトリの存在理由を証明

## 展開

1. `/noe{axiom:FEP}~/dia` — FEP公理から認識し批判と振動
2. `I:confidence=1{/ene{output:PROOF.md}}` — 確信あれば PROOF.md 出力
3. `E:{/ene{action:move, to:_limbo/}}` — なければ _limbo/ に移動
