---
description: "[CCL Macro] タスク整理 — @tak = /s1_F:[×3]{/sta~/chr}_F:[×3]{/kho~/zet}_I:[gap]{/sop}_/euk_/bou"
---

# /ccl-tak: タスク整理マクロ

> **CCL**: `@tak = /s1_F:[×3]{/sta~/chr}_F:[×3]{/kho~/zet}_I:[gap]{/sop}_/euk_/bou`
> **用途**: TODO/タスク/アイデアを整理・分類・見積もり

## 展開

1. `/s1` — スケール設定
2. `F:[×3]{/sta~/chr}` — 基準×時間を3回振動
3. `F:[×3]{/kho~/zet}` — 空間×探求を3回振動
4. `I:[gap]{/sop}` — ギャップあれば調査
5. `/euk_/bou` — 好機判定→意志確認

## 使用例

```ccl
@tak                       # 標準整理
@tak-                      # 高速分類（Must/Shouldのみ）
@tak _ @plan               # 整理後に計画策定
```

## CPL 構文

`F:[×N]{}`, `I:[]{}`, `~`, `_`
