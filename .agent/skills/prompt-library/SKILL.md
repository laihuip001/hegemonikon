---
name: Prompt Library
description: Library (112プロンプト) への動的ルーティングとコンテキスト注入
activation: auto
triggers:
  - 思考モジュール
  - プロンプト参照
  - Library
  - テンプレート
  - Forge
  - /lib
hegemonikon: S2 Mekhanē
risk_tier: L1
reversible: true
requires_approval: false
risks:
  - "誤ったモジュール推薦による認知的誤誘導"
fallbacks:
  - "Creator に候補を提示し選択させる"
---

# Prompt Library Skill

> **目的**: Library の112プロンプトモジュールを WF 実行時に動的に検索・注入する
> **発動**: WF 実行時（暗黙）、`/lib` コマンド（明示）

---

## アーキテクチャ

```
Creator → /lib "品質"
              ↓
     YAML frontmatter の
     activation_triggers を走査
              ↓
     マッチしたモジュールの
     essence を抽出・注入
              ↓
     [Library Injected: 敵対的レビュー凸]
     > 直前の出力に対し、一切の慈悲を持たない
     > 「敵対的レビュー」を実行してください。
```

---

## 発動ロジック

### 1. 暗黙発動 (WF 実行時)

WF の `hegemonikon` フィールドから関連 Series を特定し、Library 内で同じ `hegemonikon_mapping` を持つモジュールの `essence` を注入する。

```yaml
# 例: /dia 実行時
dia.hegemonikon → A2 Krisis
Library scan → hegemonikon_mapping に "A2 Krisis" を含むモジュール:
  - 敵対的レビュー凸.md
  - おべっかの無い評価.md
  - エレガンススマート監査.md
→ essence を 3行ずつ注入

出力: [Library Injected: 敵対的レビュー凸, おべっかの無い評価]
```

### 2. 明示発動 (`/lib`)

Creator が `/lib [キーワード]` を実行すると、`activation_triggers` をキーワード検索し、マッチしたモジュールを一覧表示。

```yaml
/lib 品質
→ activation_triggers に "品質" を含むモジュール:
  - 敵対的レビュー凸 (品質, 批判, review, dia)
  - おべっかの無い評価 (評価, 正直, honest_review, dia)
  - エレガンススマート監査 (品質, 監査, audit)
  - Module 04: TDD (テスト, TDD, 品質, testing)
  - Forge/品質を確かめる (振り返る, 評価, review)
→ 一覧表示 + 詳細参照可能
```

### 3. WF @complete 連携

WF 完了時に「次に参照すべき Library モジュール」を提案する。

```yaml
/zet 完了 → @complete
  Library 提案: "問いの爆撃" モジュールが関連しています
  → view_file で参照しますか？
```

---

## Library 構造

```
~/Sync/10_📚_ライブラリ｜Library/prompts/
├── modules/           (31個 — 思考・学習・評価・対話・分析・計画)
├── modules/dev/       (25個 — DMZ/TDD/Commit/RedTeam 等)
├── system-instructions/ (12個 — SI, メタプロンプト 等)
└── templates/forge/   (44個 — 見つける/考える/働きかける/振り返る)
```

### frontmatter 構造

各ファイルは以下の YAML frontmatter を持つ:

```yaml
name: "モジュール名"
origin: "Brain Vault (pre-FEP)"
category: "カテゴリ"
hegemonikon_mapping: "HGK WF/Skill 対応"
model_target: "universal"
activation_triggers: ["キーワード1", "キーワード2", ...]
essence: |
  モジュールの核心 3-5行
  (コンテキスト注入用)
```

---

## 使用方法

### 自動発動 (Claude)

WF 実行時に `hegemonikon_mapping` ベースで関連モジュールを自動検出・注入。通知ではなく**コンテキスト注入**で、Claude の処理に直接組み込む。

### 手動発動 (Creator)

`/lib [キーワード]` で activation_triggers ベースの Library 検索。

---

## 関連 Skill/WF

| 関連 | パス |
|:-----|:-----|
| Code Protocols | `.agent/skills/code-protocols/SKILL.md` |
| `/lib` WF | `.agent/workflows/lib.md` |
| Gnōsis (将来) | `mekhane/anamnesis/` — prompts テーブル追加予定 |
