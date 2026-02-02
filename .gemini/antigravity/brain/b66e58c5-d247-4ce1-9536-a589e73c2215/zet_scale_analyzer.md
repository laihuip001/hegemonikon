# Scale Analyzer 設計: Perplexity 調査結果

> **調査日**: 2026-01-28
> **統合報告書**: スケール判定フレームワーク

---

## 主要フレームワーク (Top 5)

| # | 手法 | Core概念 | 信頼度 |
|:--|:-----|:---------|:------:|
| 1 | **Interacting Timescales** | fast (egocentric) ↔ slow (allocentric) | ★★★★★ |
| 2 | **HALO** | 3層: Planning → Role-Design → Inference | ★★★★★ |
| 3 | **Abstraction-of-Thought (AoT)** | Knowledge Level ↔ Symbol Level | ★★★★★ |
| 4 | **Design Thinking** | Macro → Meso → Micro → Macro | ★★★★★ |
| 5 | **SEAR** | entity_type + table_struct + context で動的選択 | ★★★★ |

---

## 7段階アルゴリズム (SAGE 実装用)

```
STAGE 1: Feature Extraction
  → [deadline, impact_scope, change_scope, domain_novelty]

STAGE 2: Timescale Analysis
  → fast_timescale / slow_timescale / hybrid

STAGE 3: Hierarchy Depth
  → [Apex, Meso, Micro, Nano] レベル決定

STAGE 4: Cognitive Load Check
  → conflict_detected → temporal_decomposition

STAGE 5: Prompt Strategy Selection
  → Direct / CoT / AoT / Decomposed

STAGE 6: Reasoner Composition
  → DT (symbolic) + LLM (abstract) ハイブリッド

STAGE 7: Output Format Adaptation
  → Macro / Micro / Mixed 形式
```

---

## スケール切替信号

| 信号 | 推奨アクション |
|:-----|:---------------|
| 詳細な制約が急に出現 | Zoom-In: Micro へ |
| 複数ドメインの相互作用 | Zoom-Out: Macro へ |
| ユーザー要件修正 | Re-assess: 再評価 |
| 推論不確実性上昇 | Switch: 異スケールへ |

---

## 出力フォーマット

**Macro**: `{strategy, key_phases, alternatives, risks, timeline}`
**Micro**: `{steps, dependencies, error_cases, estimated_effort}`

---

*Source: Perplexity Deep Research 2026-01-28*
