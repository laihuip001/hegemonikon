---
name: "Pepsis (Πέψις)"
status: active
phase: "Operational — 多言語消化フレームワーク"
updated: 2026-02-14
next_action: "Rust 消化 Phase 1 (Ownership/Borrowing/Lifetime)"
---

# Pepsis — 設計哲学消化フレームワーク

> **CCL**: `/eat+ >> /fit`
> **前身**: Pythōsis (Python 専門 → 汎用化)
> **命名**: Πέψις = 消化。外部設計哲学を HGK に消化する場所。

## 概要

外部の設計哲学・言語思想を Hegemonikón に「消化」するための汎用フレームワーク。
消化テンプレート (T1-T4) を共通基盤とし、言語ごとにサブディレクトリで成果物を管理する。

## 消化済み / 進行中

| 対象 | Phase | 状態 | サブディレクトリ |
|:-----|:------|:-----|:---------------|
| **Python** | Phase 5 完了 | ✅ 完食 (骨髄まで) | `python/` |
| **Rust** | Phase 1 準備 | 🟡 開始 | `rust/` |

## 共通基盤

| ファイル | 内容 |
|:---------|:-----|
| `templates/digestion_templates.md` | T1-T4 消化テンプレート定義 |
| `sonae.md` | 備えマトリックス |

## Architecture

```
pepsis/
├── PROJECT.md          # この文書
├── PROOF.md            # 存在証明
├── README.md           # 概要
├── roadmap.md          # 汎用ロードマップ
├── sonae.md            # 備えマトリックス
├── templates/          # 共通消化テンプレート
│   └── digestion_templates.md
├── python/             # Python 消化成果物 (✅ 完了)
│   ├── STATUS.md
│   ├── designs/
│   ├── macros/
│   ├── mappings/
│   └── experiments/
└── rust/               # Rust 消化成果物 (🟡 進行中)
    ├── STATUS.md
    ├── designs/
    ├── macros/
    └── mappings/
```
