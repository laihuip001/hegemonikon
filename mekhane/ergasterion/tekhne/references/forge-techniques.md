---
title: Forge Techniques
source: "Forge Prompt Structure v2.0"
naturalized: 2026-01-29
purpose: Forge から吸収した high-value テクニック
---

# Forge Techniques

> **Origin**: Forge Prompt Structure v2.0 (44 modules)
> **消化方式**: Derivative Enrichment — 必要なものだけを吸収

---

## 🎲 Randomize (揺らぎを与える)

**追加先**: `/zet --mode=randomize`

### 本質

```yaml
role: "Agent of Chaos"
purpose: "思考膠着を強制的に打破する"
method: "文脈と無関係なランダム刺激を投入"
inspiration: "Brian Eno's Oblique Strategies"
```

### プロセス

1. **Inject Noise**: 論理的文脈とは無関係な単語/制約/問いを提示
2. **Force Connection**: ノイズと課題を無理やり結びつける（強制結合法）
3. **Break Pattern**: 既存パターンを破壊

### 出力形式

```text
┌─[O3 Zētēsis: Randomize Mode]────────────────────────┐
│                                                      │
│ 🃏 Card 1: [ランダムな概念]                          │
│   → 「もし [課題] が [概念] だったら？」              │
│                                                      │
│ 🃏 Card 2: [ランダムな制約]                          │
│   → 「[制約] の下でやり直すとしたら？」               │
│                                                      │
│ 🃏 Card 3: [Oblique Strategy]                        │
│   → "[格言]"                                         │
│                                                      │
│ 🔗 強制結合ヒント: {突飛なアイデア}                  │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## ⛓️ TOC (制約理論)

**追加先**: `/met --mode=toc`

### 本質

```yaml
role: "TOC Consultant"
purpose: "システム全体を制限するボトルネックを特定"
method: "制約理論の5段階集中プロセス"
principle: "鎖の強さは最も弱い輪で決まる"
```

### 5段階プロセス

| Step | 名称 | 内容 |
|:-----|:-----|:-----|
| 1 | Identify | 制約（ボトルネック）を特定 |
| 2 | Exploit | 制約を徹底活用（無駄をゼロに） |
| 3 | Subordinate | 他の全工程を制約に合わせる |
| 4 | Elevate | 制約の能力を強化（投資） |
| 5 | Repeat | 新しい制約が現れたら1に戻る |

### 出力形式

```text
┌─[S1 Metron: TOC Mode]───────────────────────────────┐
│                                                      │
│ ⛓️ ボトルネック特定: {ステップ名}                    │
│   理由: {なぜこれが全体を制限しているか}             │
│                                                      │
│ 📋 対策:                                             │
│   [Exploit] {無駄を削る方法}                         │
│   [Subordinate] {他工程の調整}                       │
│   [Elevate] {投資案}                                 │
│                                                      │
│ ⚠️ 警告: 局所最適の罠に注意                         │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## 統合状況

| Forge モジュール | 吸収先 | 状態 |
|:-----------------|:-------|:-----|
| 🎲 揺らぎを与える | `/zet --mode=randomize` | ✅ |
| ⛓️ ボトルネックを突く | `/met --mode=toc` | ✅ |
| 🚀 テコを見つける | (toc に統合) | — |
| 🏟️ 環境をデザインする | (検討中) | △ |
| 🎮 クエスト化する | (検討中) | △ |
| 🤝 任せる | (検討中) | △ |
| 🔪 本質だけ残す | (S3 で既対応) | ❌ |

---

*Naturalized from Forge v2.0 — 2026-01-29*
