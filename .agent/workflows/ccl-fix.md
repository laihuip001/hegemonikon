---
description: "直す — /kho_/tel_C:{/dia+_/ene+}_I:[✓]{/pis_/dox-}"
---

# /ccl-fix: 修正サイクルマクロ

> **CCL**: `@fix = /kho_/tel_C:{/dia+_/ene+}_I:[✓]{/pis_/dox-}`
> **用途**: 問題を見つけて直すサイクルを収束まで回す
> **認知骨格**: Prior → Likelihood → Posterior

## 展開

| 相 | ステップ | 意味 |
|:---|:---------|:-----|
| Prior | `/kho` | 場の把握: 何が壊れているかの全体像 |
| Prior | `/tel` | 目標設定: どこに戻したいか |
| Likelihood | `C:{/dia+_/ene+}` | 診断→修正の収束ループ |
| Posterior | `I:[✓]{/pis_/dox-}` | 収束したら確信度を測定し記録 |

## 使用例

```ccl
@fix                       # 収束まで修正
@fix _ @vet                # 修正後に自己検証
```
