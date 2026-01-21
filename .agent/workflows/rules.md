---
description: 全ルールの一覧と概要を表示する
---

# /rules: ルール一覧表示

> **目的**: 現在有効な全ルールを一覧表示する

---

## 実行手順

1. `.agent/rules/` ディレクトリを読み込む
2. 各ファイルの概要を1行で表示する

---

## 現在のルール一覧

| ファイル | 概要 |
|----------|------|
| `protocol-g.md` | Git操作の直接実行禁止 |
| `protocol-d.md` | 外部サービス使用前のsearch_web強制 |
| `protocol-d-extended.md` | 存在系断言前のgrep+search強制 |
| `protocol-v.md` | バージョン番号出力前のsearch強制 |
| `error-prevention-protocols.md` | P1-P9エラー防止体系 |
| `safety-invariants.md` | 破壊的操作承認、機密保護、3原則 |
| `termux-constraints.md` | Termux環境固有の制約 |

---

## 出力形式

```
📋 Rules Overview

| # | ファイル | 概要 |
|---|----------|------|
| 1 | protocol-g.md | Git操作禁止 |
| 2 | protocol-d.md | 外部サービス検証 |
| ... | ... | ... |

合計: X ルール
```
