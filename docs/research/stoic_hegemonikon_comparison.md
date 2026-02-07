# STOIC Architecture vs Hegemonikón: 比較分析

> **調査日付**: 2026-01-28
> **調査元**: Perplexity Zētēsis (stoic_architecture_comparison_2026-01-28.md)

---

## Executive Summary

STOIC（Jeff Borneman, RELCOG Labs）と Hegemonikón は、異なる出発点から「統治された認知」という同一の設計原則に収斂する**独立した収斂進化**である。

- **STOIC**: 実装完成度と計算効率で優れる（Production稼働中）
- **Hegemonikón**: 理論的厳密性と文脈適応性で優位（96要素体系）

---

## 比較表

| 観点 | STOIC | Hegemonikón | 優位性 |
|:-----|:------|:------------|:------:|
| **哲学的基盤** | ストア派メタファー（比喩的活用） | FEP × ストア派（技術翻訳） | **H** |
| **認知エンジン** | Dual-Engine（Sequential） | M-series Cascade（Parallel） | 同等 |
| **マイクロエージェンシー** | 4-5個（推定） | 866スペシャリスト | **H** |
| **意思決定軸** | 4次元 | 12次元（4公理 × 3組み合わせ） | **H** |
| **文脈フィルター** | なし（通用型） | 12の Kairos（時間×階層×主体×方向） | **H** |
| **実装進度** | Production稼働（医療・ロボティクス） | 理論完成、部分実装 | **S** |
| **計算効率** | ⭐⭐⭐⭐⭐（20M ≈ 50B） | ⭐⭐⭐（複雑性tradeoff） | **S** |
| **拡張容易性** | ⭐⭐⭐（LLM Selection） | ⭐⭐⭐⭐⭐（Skill/Kairos追加） | **H** |
| **理論的完全性** | 不完全（比喩レベル） | 完全（1→2→4→8→12の必然的導出） | **H** |

---

## Hegemonikón の5つの独自性

### 1. 数学的必然性（Mathematical Inevitability）

Hegemonikón の公理系は**完全に導出的**である：

```
FEP (1)
→ Core Axioms (2: Flow, Value)
→ Choice Axioms (4: Tempo, Stratum, Agency, Valence)
→ P-series (4: 2×2 = Pure Theorems)
→ M-series (8: 2×4 = Extended Theorems)
→ Kairos (12: 4×3 = Contextual Modifiers)
→ 合計: 60要素
```

各レイヤーが前段から**必然的に導出**され、任意性がない。STOICにはこの数学的厳密性がない。

### 2. Kairos の12次元文脈判定

12の Kairos 構造により、**同一の入力でも文脈に応じた異なる応答**が自動的に選択される。

| 組み合わせ | 例 |
|:---------|:---|
| Tempo × {Stratum, Agency, Valence} | 時間制約が判定を変える |
| Stratum × {Tempo, Agency, Valence} | 処理レベルが判定を変える |
| Agency × Valence × Tempo | 主体と方向の相互作用 |

STOICには明示的な文脈フィルター機構がない。

### 3. 866スペシャリスト評価体系

| 利点 | 説明 |
|:-----|:-----|
| 独立性 | 各スペシャリストが独立して判定 |
| 冗長性 | 相互チェックによる誤謬検出 |
| 多様性 | 単一の視点に依存しない結論 |

### 4. Anti-Skip Protocol

形式的な曖昧さ排除メカニズム。STOICは「曖昧さを評価する」のに対し、Hegemonikónは「曖昧さを殲滅する」。

### 5. Pure Theorems（P-series）によるメタ認知層

| 定理 | 問い |
|:-----|:-----|
| P1 Noēsis | 何を知っているか（認識） |
| P2 Boulēsis | 何を望むか（意志） |
| P3 Zētēsis | 何を問うか（探求） |
| P4 Energeia | 何をするか（行為） |

AIが「自分は何をしているのか」を常に問い直す構造。STOICにはメタ認知層がない。

---

## STOIC の強み（学ぶべき点）

| 強み | 詳細 |
|:-----|:-----|
| **実装完成度** | Production環境での稼働実績（医療、ロボティクス） |
| **計算効率** | 20Mモデルで50Bモデル相当の出力品質 |
| **再現可能性** | 決定論的な動作（同一promptで同一結果） |
| **シンプルさ** | マイクロエージェンシーの透明性 |

---

## 推奨アクション

| 短期 | 中期 |
|:-----|:-----|
| STOIC Dual-Engine の設計パターンを `/ene` に参照 | Production-grade 実装を目指す |
| 計算効率向上のためのプロンプト最適化 | 医療・ロボティクス領域での pilot 検討 |

---

## 参考文献

- [STOIC Architecture: A High-Level Introduction to Governed Cognition](https://philarchive.org/archive/BORAHI) - Jeff Borneman, 2026-01-18
- RELCOG Labs LinkedIn (2025-12-17, 2026-01-23)

---

*Generated from Perplexity Zētēsis research (2026-01-28)*
