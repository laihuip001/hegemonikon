---
id: C-6-7
modes: [audit, fix]
enforcement_level: L1
---

# C-6/C-7: Prompt Engineering (プロンプトエンジニアリング)

---

## Mode: Audit

### Objective

プロンプト案に対し、LLM挙動制御観点から構造監査を行い脆弱性を特定。

### Auditor Mindset

- **Code, Not Text:** プロンプトを「プログラムコード」としてデバッグ
- **Murphy's Law:** 曖昧な指示は最悪の形で解釈される
- **Deterministic:** 100回実行して100回同じ結果が出なければ欠陥

### Attack Vectors

**1. Structural Integrity**

- 入力 (`{{INPUT}}`) と命令の境界がタグで物理分離されているか
- 出力フォーマットがスキーマで型定義されているか

**2. Semantic Ambiguity**

- 禁止語彙: 「適切に」「いい感じに」「自然な」「簡潔に」「必要に応じて」
- 定量的制約 (「200文字以内」) に置換されているか

**3. Logic Orchestration**

- 複雑な推論でいきなり回答を出力させていないか
- `<thinking_process>` で中間状態を出力させているか

### Failure Simulation

最も意地の悪いAIになりきり、このプロンプトをどう曲解・サボれるか？

### Output

```markdown
## Failure Simulation
- **Scenario:** ...

## Structural Flaws
| Location | Risk |
|---|---|
| L42 | Injection Risk |

## Ambiguity Detection
| Word | Fix Suggestion |
|---|---|
| 「適切に」 | 「3段落以内で」 |

## Missing Components
- [ ] CoT
- [ ] Few-Shot
- [ ] Negative Constraints

## Metrics
- Determinism: 0-100
- Isolation: 0-100
```

---

## Mode: Fix

### Objective

直前の監査結果に基づき、プロンプトを再構築しプロダクション品質へ最適化。

### Refactoring Steps

1. **Structural Hardening:** XMLタグで構造化、入力と命令を物理分離
2. **Semantic Disambiguation:** 曖昧語彙を定量的制約に置換
3. **Component Injection:** CoT (`<thinking_process>`) を実装

### Strict Constraints

- **NO_TRUNCATION:** `# ...` や「中略」は禁止
- **NO_META_COMMENTARY:** 解説不要。最適化プロンプトのみ出力

### Output

```xml
<optimized_prompt>
(修正済みの完全なプロンプト)
</optimized_prompt>
```
