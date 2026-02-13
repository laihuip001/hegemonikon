---
description: "監る — /kho_/s-_/pro_/dia+{synteleia}_~(/noe*/dia)_V:{/pis+}_/dox-"
---

# /ccl-syn: Synteleia 監査マクロ

> **CCL**: `@syn = /kho_/s-_/pro_/dia+{synteleia}_~(/noe*/dia)_V:{/pis+}_/dox-`
> **用途**: Synteleia 監査 (L1+L2) を発動し、確信度を検証する
> **圏論**: 免疫系 = 恒等的自然変換 (同一性の検証)
> **認知骨格**: Prior → Likelihood → Posterior

## 展開

| 相 | ステップ | 意味 |
|:---|:---------|:-----|
| Prior | `/kho` | 監視対象の場を把握する |
| Prior | `/s-` | 何を監視するかの焦点を定める (方向性) |
| Prior | `/pro` | 「何かおかしい」直感を感じ取る (前感情) |
| Likelihood | `/dia+{synteleia}` | Synteleia 多角監査を発動 (L1静的 + L2セマンティック) |
| Posterior | `~(/noe*/dia)` | 監査結果を直観×判定で振動検証 |
| Posterior | `V:{/pis+}` | 確信度を検証ゲートで評価 |
| Posterior | `/dox-` | 監査結果を軽量記録 |

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
