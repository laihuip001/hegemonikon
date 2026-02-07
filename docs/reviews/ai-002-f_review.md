# 🛡 専門家レビュー: ハルシネーション検出者 (AI-002.F)

> **Archetype:** Safety
> **Category:** ai_risk

## Task

`mekhane/symploke/specialists_tier1.py` を以下の観点で分析し、結果を `docs/reviews/ai-002-f_review.md` に書き込んでください。

## Focus

存在しないAPIメソッド呼び出しを確認

## Output Format

# ハルシネーション検出者 (派生: Fix) レビュー

## 対象ファイル
`mekhane/symploke/specialists_tier1.py`

## 発見事項
- **Critical**: 対象ファイル `mekhane/symploke/specialists_tier1.py` が存在しません。
  - `mekhane/symploke/specialist_prompts.py` 内に `PHASE1_SPECIALISTS` (見落とし層) が定義されていますが、`specialists_tier1.py` というファイル名とは一致しません。
  - これはタスク指示自体がファイル名をハルシネーションしているか、ファイルが消失している状態です。

## 重大度
- Critical

## 沈黙判定
- 発言（要改善）

## 修正提案 (DIFF)
ファイルが存在しないため、DIFFは生成できません。
推奨されるアクション:
1. タスク指示のファイル名を `mekhane/symploke/specialist_prompts.py` に修正する。
2. または、`specialist_prompts.py` から Phase 1 の定義を `mekhane/symploke/phase1_specialists.py` (または `tier1`) に分離するリファクタリングを行う。
