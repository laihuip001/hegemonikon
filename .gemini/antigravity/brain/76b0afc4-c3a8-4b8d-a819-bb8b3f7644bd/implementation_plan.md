# Implementation Plan: /tek Workflow Generation Mode

> **目的**: /tek でスキルだけでなくワークフローも生成可能にする
> **設計**: Interactive Mode で質問を通じて成果物種類を判定

---

## 変更の本質

| Before | After |
|:-------|:------|
| `/tek [要件]` → スキル生成のみ | `/tek` → 質問フロー → スキル or ワークフロー |
| 明示的なモード指定が必要 | 質問で自動判定 |

---

## Proposed Changes

### tekhne-maker SKILL.md

#### [MODIFY] [SKILL.md](file:///home/laihuip001/oikos/hegemonikon/mekhane/ergasterion/tekhne/SKILL.md)

**追加内容**:

1. **Interactive Mode (新規)**: `/tek` 単体で質問フロー開始
2. **Output Type Detection Questions**: スキル vs ワークフロー判定
3. **Workflow Template**: zet.md ベースの構造

**判定質問**:

```yaml
Q1: 何を作りたいですか？
  A: 「知識・ルール・行動指針」を定義したい → Skill
  B: 「手順・フロー・ステップ」を定義したい → Workflow

Q2: 他のスキルを呼び出しますか？
  A: はい → Workflow (skill_ref が必要)
  B: いいえ → Skill
```

---

### /tek.md ワークフロー

#### [MODIFY] [tek.md](file:///home/laihuip001/oikos/.agent/workflows/tek.md)

**追加内容**:

1. Interactive Mode トリガー
2. 質問フローの手順
3. Workflow Template セクション

---

## Workflow Template (zet.md ベース)

```yaml
---
description: [1行説明]
hegemonikon: [層]
modules: [モジュールリスト]
skill_ref: "[参照するSKILL.mdパス]"
version: "1.0"
lineage: "[生成経緯]"
anti_skip: enabled
---

# /[name]: [タイトル]

> **正本参照**: [SKILL.md へのリンク]
> **目的**: [1文]
> **出力**: [成果物の説明]

---

## 発動条件

| トリガー | 説明 |
|:---------|:-----|
| `/[name]` | デフォルト動作 |
| `/[name] [variant]` | バリアント |

---

## ⚠️ 実行前必須: 正本読み込み

> **このステップは省略禁止。必ず実行すること。**

```text
実行手順:
1. view_file ツールで SKILL.md を読み込む
   パス: [skill_ref]
2. [確認事項]
3. [確認事項]
4. 確認後、処理を開始
```

---

## 処理フロー

[フローの詳細]

---

## エラー対処

| エラー | 原因 | 対処 |
|:-------|:-----|:-----|
| ... | ... | ... |

---

## Hegemonikon Status

| Module | Workflow | Skill (正本) | Status |
|:-------|:---------|:-------------|:-------|
| [module] | /[name] | [SKILL.md] | v1.0 Ready |

```

---

## Verification Plan

1. `/tek` を実行し、質問フローが開始されるか確認
2. 「Workflow を作成」と回答し、Workflow Template が適用されるか確認
3. 生成された Workflow が zet.md と同等の品質か確認

---

## 次のステップ

1. [ ] この計画を承認
2. [ ] tekhne-maker SKILL.md に Interactive Mode を追加
3. [ ] /tek.md に Workflow Template を追加
4. [ ] テスト実行

---

*Implementation Plan created: 2026-01-28*
