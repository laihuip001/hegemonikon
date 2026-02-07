---
name: Code Protocols
description: 開発プロトコル（旧資産Module 01-25）への自動参照
activation: auto
triggers:
  - /do
  - /plan (implementation phase)
hegemonikon: M6-Praxis
# Safety Contract (v1.0 — /eat 消化洞察 2026-02-07)
risk_tier: L1
reversible: true
requires_approval: false
risks:
  - "古いプロトコルの適用による設計判断の誤誘導"
  - "原典パスが Windows 依存（移植時に破損）"
fallbacks: []
---

# Code Protocols Skill

> **目的**: 実装フェーズで開発プロトコルを自動参照
> **発動**: `/do` 実行時、または実装計画作成時

---

## 自動参照ロジック

タスクの種類に応じて、該当するプロトコルを提示する:

| タスク種別 | 参照プロトコル | 原典パス |
|:---|:---|:---|
| 設定ファイル編集 | **DMZ Protocol** | Module 01 |
| 新機能実装 | **TDD Protocol** | Module 04 |
| コミット作成 | **Narrative Commit** | Module 14 |
| 複雑度が高い | **Complexity Budget** | Module 06 |
| セキュリティ関連 | **Red Teaming** | Module 11 |

---

## 原典参照パス

```
~/Sync/10_📚_ライブラリ｜Library/prompts/modules/dev/
├── module_01_dmz_protocol.md
├── module_04_tdd_enforcement.md
├── module_06_complexity_budget.md
├── module_07_devils_advocate.md
├── module_10_ripple_effect_analysis.md
├── module_11_red_teaming.md
├── module_13_chestertons_fence.md
├── module_14_narrative_commit.md
└── ... (全25モジュール)
```

---

## 発動時の出力形式

```
[Hegemonikon] M6 Praxis → Code Protocols
  タスク: {タスク種別}
  該当プロトコル: {プロトコル名}
  原典: view_file "{パス}" で詳細参照可能
```

---

## 使用方法

### 自動発動（Claude）

`/do` 実行時に M6 Praxis が自動でこの Skill を参照し、該当プロトコルを提示。

### 手動発動（Creator）

`/dev` ワークフローで明示的にプロトコル一覧を表示。

---

## モジュール一覧インデックス

詳細は `~/Sync/10_📚_ライブラリ｜Library/prompts/modules/dev/` 内の各ファイルを参照。
