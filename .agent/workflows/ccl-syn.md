---
description: "監る — /dia+{synteleia}_V:{/pis+}"
lcm_state: "configured"
version: "1.0.0"
---

# /ccl-syn: Synteleia 監査マクロ

> **CCL**: `@syn = /dia+{synteleia}_V:{/pis+}`
> **用途**: Synteleia 監査 (L1+L2) を発動し、確信度を検証する
> **圏論**: 免疫系 = 恒等的自然変換 (同一性の検証)

## 展開

1. `/dia+{synteleia}` — Synteleia 多角監査を発動 (L1静的 + L2セマンティック)
2. `_V:{/pis+}` — 確信度を検証ゲートで評価

## 使用例

```ccl
@syn                       # 標準監査 (最後の出力を監査)
@syn _ /ene+               # 監査後に修正実行
@build _ @syn              # 構築後にセマンティック監査
C:{@build _ @syn}          # 監査合格まで収束ループ
```

## 統合先

| WF | 接続 | 発動条件 |
|:---|:-----|:---------|
| `/dia+` | 自動発動 | `{synteleia}` パラメータ指定時 |
| `@vet` | 手動接続 | `@vet _ @syn` で検証強化 |
| `@build` | 手動接続 | `@build _ @syn` で品質保証 |
