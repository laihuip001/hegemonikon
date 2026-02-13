---
description: "段取る — /bou+_/chr_/s+~(/p*/k)_V:{/dia}_/pis_/dox-"
---

# /ccl-plan: 計画策定マクロ

> **CCL**: `@plan = /bou+_/chr_/s+~(/p*/k)_V:{/dia}_/pis_/dox-`
> **用途**: 何かを始める前に計画を練りたいとき
> **認知骨格**: Prior → Likelihood → Posterior

## 展開

| 相 | ステップ | 意味 |
|:---|:---------|:-----|
| Prior | `/bou+` | 意志を詳細化: 何を達成したいか |
| Prior | `/chr` | 資源確認: 手持ちで使えるものは何か |
| Likelihood | `/s+~(/p*/k)` | 戦略を環境×文脈と振動させて練る |
| Likelihood | `V:{/dia}` | 判定で検証ゲート: 計画は妥当か |
| Posterior | `/pis` | 計画の確信度を測定 |
| Posterior | `/dox-` | 計画を軽量記録 |

## 使用例

```ccl
@plan                      # 標準計画
@plan _ @build             # 計画後に構築
```
