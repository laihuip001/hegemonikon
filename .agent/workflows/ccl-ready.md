---
description: "見渡す — /bou-_/pat_/pro_/kho_/chr_/euk_/tak-_~(/h*/k)_/pis_/dox-"
lcm_state: beta
version: "1.0"
---

# /ccl-ready: 見渡しマクロ

> **CCL**: `@ready = /bou-_/pat_/pro_/kho_/chr_/euk_/tak-_~(/h*/k)_/pis`
> **用途**: タスク着手前に「場・資源・タイミング・順序」を整理する
> **起源**: DX-008 hub-only 9定理統合 — P1/P2/P3/S3 を一括活用
> **認知骨格**: Prior → Likelihood → Posterior

## 展開

| 相 | ステップ | 意味 |
|:---|:---------|:-----|
| Prior | `/bou-` | なぜ見渡すのか、軽く目的を確認 |
| Prior | `/pat` (A1 Pathos) | 知覚: いま何が見えているか、生の入力を受け取る |
| Prior | `/pro` | 全体の直感的印象を感じ取る (前感情) |
| Likelihood | `/kho` (P1 Khōra) | 場の分析: いまどこにいるか、何が見えるか |
| Likelihood | `/chr` (K2 Chronos) | 資源確認: 手持ちで使えるものは何か |
| Likelihood | `/euk` (K1 Eukairia) | 好機判断: 今やるべきタイミングか |
| Likelihood | `/tak-` | 軽量配列: ざっくり順序を決める |
| Posterior | `~(/h*/k)` | 動機×文脈の全体像に統合 |
| Posterior | `/pis` | 準備完了度の確信度を測定 |

## いつ使うか

- 新しいタスクに取りかかる前
- 「何から手をつけるか」迷ったとき
- 複数タスクが並行しているとき

## 設計メモ

hub-only 定理 4つ (/kho, /chr, /euk, /tak) を1つのマクロに自然にまとめた。
「見渡す」は実装・分析の "前" に来る行為。@plan が「戦略を練る」なら @ready は「地形を把握する」。
A1 /pat は「見渡す前にまず目を開く」— 知覚は前感情 (/pro) の入力層。
