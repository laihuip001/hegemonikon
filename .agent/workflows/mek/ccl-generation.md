---
description: CCL生成モード。自然言語をCCL v2.0に変換する4層フォールバック実装。
hegemonikon: S2 Mekhanē
parent: ../mek.md
---

# CCL 生成モード (CCL Generation)

> S2 Mekhanē — 自然言語の意図を CCL v2.0 式に変換する。4層フォールバックで確実に生成。

## Constraints

- 生成した CCL は必ず構文検証を行う
- フォールバック の Source (llm/doxa/heuristic/user) を明示する
- 実行前に Creator の確認を取る

---

## Trigger

```text
/mek ccl "ブログ記事を分析して改善案を出す"
```

---

## Process

1. **Layer 1: LLM Parser** — Gemini API で CCL v2.0 構文を直接生成
2. **Layer 2: Doxa Patterns** — 過去に学習したパターンから検索 (H4 連携)
3. **Layer 3: Heuristic** — キーワードマッチング、ループ検出 (N回 → `F:×N{}`)
4. **Layer 4: User Inquiry** — `/u` で Creator に問い合わせ

各レイヤーは前レイヤーが失敗した場合のみ実行される。

1. **Validation** — CCL v2.0 準拠チェック
2. **Output** — CCL 式 + 解釈を提示。成功時は Doxa に学習記録

---

## Output Format

**[S2 Mekhanē: CCL Generated]**

| フィールド | 内容 |
|:-----------|:-----|
| 意図 | {入力された自然言語} |
| CCL式 | {生成された CCL} |
| Source | {llm / doxa / heuristic / user} |
| 解釈 | Step 1: {演算子説明}, Step 2: {演算子説明} |
| 確認 | 実行しますか？ [y/n/edit] |

---

## 実装参照

```python
from mekhane.ccl import CCLGenerator

gen = CCLGenerator()
result = gen.generate("3回分析して実行")
# result.ccl   -> "F:×3{ /s_/ene }"
# result.source -> "heuristic" or "llm" or "doxa"
```

---

## 質問フロー

Hegemonikón Mode (`/tek`) で定理体系に馴染む生成物を作る際の選択フロー:

| Step | 質問 | 選択肢 |
|:-----|:-----|:-------|
| Q1 | カテゴリ選択 | A: Ousia, B: Schema, C: Akribeia, D: Hormē, E: Perigraphē, F: Kairos |
| Q2 | 定理選択 | Q1に応じた4定理を表示 |
| Q3 | X-series 連携 | 関係定理の選択 |
| Q4 | 生成意図 | なぜこの定理か |
| Q5 | Skill or Workflow? | A: Skill (知識/ルール), B: Workflow (手順/フロー) |

### 俗モード (/tek vulg)

例外的に体系外の生成が必要な場合のみ: Q1: Skill or Workflow? → Q2: 要件

---

## Reminder

- CCL 式の Source を必ず明示する
- 実行前に Creator 確認を取る

*CCL Generation v2.0 — Functional Beauty Redesign*
