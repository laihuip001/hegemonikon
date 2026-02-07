---
description: Artifact保存ルール、SE原則強制、計算コスト試算、使用例。
hegemonikon: S2 Mekhanē
parent: ../mek.md
---

# Artifact と使用例 (Artifact Rules)

> S2 Mekhanē — 成果物の品質保証と保存ルール。

## Constraints

- Meso 以上の Scale では失敗シナリオを必須とする
- 出力テンプレートのフィールド欠落はブロックする
- チャットには最小限の出力のみ。詳細は全てファイルに保存する

---

## Artifact 自動保存

**標準参照**: [workflow_artifact_standard.md](file:///home/makaron8426/oikos/.agent/standards/workflow_artifact_standard.md)

### 必須フィールド (SE原則)

| フィールド | 必須条件 | 違反時 |
|:-----------|:---------|:-------|
| 失敗シナリオ | Meso 以上 | ブロック |
| 初版マーカー | 全 Scale | ブロック |
| 所要時間 | Meso 以上 | 警告 |

### 出力テンプレート

**参照**: [mek_output.md](file:///home/makaron8426/oikos/.agent/templates/mek_output.md)
フィールドが欠けているとブロック。

### 検証

```bash
python hegemonikon/mekhane/fep/se_principle_validator.py <output.md> --workflow mek
```

### 保存先

```text
~/oikos/mneme/.hegemonikon/workflows/mek_<purpose>_<date>.md
```

例: `mek_code_review_skill_20260129.md`

### チャット出力

```text
完了: /mek
保存: /mneme/.hegemonikon/workflows/mek_{purpose}_{date}.md
要約: {生成物タイプ} ({モード})
次: {推奨次ステップ}
```

### 保存する理由

1. **コンテキスト節約** — チャット履歴を汚さない
2. **参照可能** — 生成物を後から確認できる
3. **蓄積可能** — 生成パターンの分析に活用

---

## 計算コスト試算

| ステップ | トークン数 | 時間目安 |
|:---------|:-----------|:---------|
| STEP 1-2 | 200-400 | 1-2秒 |
| STEP 3 | 800-1,500 | 5-10秒 |
| STEP 4-5 | 500-1,000 | 3-5秒 |
| STEP 6 | 300-500 | 2-3秒 |
| **合計** | **1,800-3,400** | **11-20秒** |

---

## 使用例

### 例1: 新規スキル生成

```text
/tek 「Perplexity への調査依頼を高精度化するスキル」
→ 5 Diagnostic Questions → RECURSIVE_CORE → SKILL.md 出力
```

### 例2: 既存スキル診断

```text
/tek diagnose /path/to/SKILL.md
→ Quality Checklist 5項目スコア算出 → 改善案提示
```

### 例3: 既存スキル改善

```text
/tek improve /path/to/SKILL.md
→ Diagnose 実行 → 改善差分のみ提示
```

---

## Hegemonikon Status

| Module | Workflow | Skill (正本) | Status |
|:-------|:---------|:-------------|:-------|
| tekhne-maker | /tek | [SKILL.md](file:///home/makaron8426/oikos/hegemonikon/mekhane/ergasterion/tekhne/SKILL.md) | v5.0 Ready |

---

## Reminder

- チャットに詳細を出さない。ファイルに保存する
- 必須フィールド欠落はブロック

*Artifact Rules v2.0 — Functional Beauty Redesign*
