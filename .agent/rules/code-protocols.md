---
description: コード開発・実装時に参照する開発プロトコル（旧 /dev WF）。コーディング、テスト、コミット、リファクタリング等の作業時に発動。
---

# 🔧 Code Protocols — 開発プロトコル

> **導出**: 旧 `/dev` WF を Rules 化 (2026-02-11)
> **原典**: `.agent/skills/code-protocols/SKILL.md`

---

## Core（コーディング時に常に意識）

| # | Protocol | 核心ルール |
|:--|:---------|:-----------|
| 01 | **DMZ** | 設定ファイル (.env, config) は保護領域。変更前に必ず確認 |
| 04 | **TDD** | テストを先に書く。テストなしの実装は実装ではない |
| 14 | **Narrative Commit** | コミットメッセージは物語。何をなぜ変えたかを伝える |

## Recommended（意識的に適用）

| # | Protocol | 核心ルール |
|:--|:---------|:-----------|
| 06 | **Complexity Budget** | 関数は短く、ネストは浅く。複雑さには予算がある |
| 07 | **Devil's Advocate** | 自分のコードに反論してほしい。 `/dia` の実装版 |
| 10 | **Ripple Effect** | 変更の影響範囲を事前に特定。依存関係を追跡 |
| 11 | **Red Teaming** | セキュリティ視点でレビュー |
| 13 | **Code Archaeology** | 既存コードを消す前に「なぜそこにあるか」を問え (Chesterton's Fence) |

## 発動条件

- ファイルの作成・編集（コード）
- `run_command` でビルド・テスト実行
- コミット作成

## 原典参照

詳細が必要な場合: `view_file .agent/skills/code-protocols/SKILL.md`

---

*旧 /dev v1.4 → conditional Rule (2026-02-11)*
