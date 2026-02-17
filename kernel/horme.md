---
doc_id: HORME_SERIES
version: 1.1.0
tier: KERNEL
status: CANONICAL
created: '2026-01-27'
updated: '2026-02-01'
extends:
  axioms:
  - L0.FEP
  - L1.Flow
  - L1.Value
  - L1.75.Valence
  - L1.75.Precision
  generation: L1 × L1.75
depends_on:
- doc_id: AXIOM_HIERARCHY
  min_version: 7.0.0
---

> **Kernel Doc Index**: [axiom_hierarchy](axiom_hierarchy.md) | [schema](schema.md) | [horme](horme.md) ← 📍 | [perigraphe](perigraphe.md)

# Ὁρμή (Hormē): 傾向定理群

> **「本質がどちらへ向かうか」**

---

## 概要

| 項目 | 内容 |
|------|------|
| **シリーズ記号** | H |
| **定理数** | 4 |
| **生成規則** | L1 (核心) × L1.75 (Tier2) |
| **役割** | 方向性・傾向の表現 |

---

## 生成原理

```
L1 核心公理: Flow (I/A), Value (E/P)
    ×
L1.75 Tier2選択: Valence (+/-), Precision (C/U)
    ↓
H-series: 2 × 2 = 4 定理
```

---

## 定理一覧

| ID | 名称 | 生成 | 意味 |
|----|------|------|------|
| H1 | **Propatheia** (Προπάθεια) | Flow × Valence | 流動傾向 — 前感情的反応 |
| H2 | **Pistis** (Πίστις) | Flow × Precision | 流動確信 — 信念レベル |
| H3 | **Orexis** (Ὄρεξις) | Value × Valence | 価値傾向 — 欲求・志向 |
| H4 | **Doxa** (Δόξα) | Value × Precision | 価値確信 — 見解・判断 |

---

## 各定理の詳細

### H1: Propatheia (前感情)

> **「理性以前の自動的傾向」**

- Flow が Valence と交差
- 認知の「初動反応」を決定
- **ストア派心理学**: 理性的判断に先立つ生理的反応
- 例: 危険に対する自動的な回避反応

### H2: Pistis (確信)

> **「推論/行為に対する信念レベル」**

- Flow が Precision と交差
- 認知への「確信度」を決定
- 例: 高い確信での行動 vs 不確実性を認めた探索

> **時間スケール注記** (B2 波及, 2026-02-15): BC-6 の確信度ラベル ([確信]/[推定]/[仮説]) は
> 推論中の一時的判定である (WM 相当)。H4 Doxa に統合されることで初めてセッション間で永続化される。
> すなわち H2 → H4 への射は「一時的確信 → 永続的信念」への情報蒸留であり、全ての確信が信念になるわけではない。

### H3: Orexis (欲求)

> **「価値に対する志向性」**

- Value が Valence と交差
- 価値への「引力」を決定
- 例: ある目標への積極的追求 vs 回避

### H4: Doxa (見解)

> **「価値判断の認識的基盤」**

- Value が Precision と交差
- 価値判断の「確実性」を決定
- 例: 確信された価値判断 vs 暫定的な見解

> **時間スケール注記 (v1.1 — UniT 消化由来)**:
> H4 Doxa は**セッション間**に永続する信念 (Handoff, KI, patterns.yaml)。
> 推論中の作業記憶 ($goal, $constraints, $decision) = WM は H4 とは異なる時間スケール。
> 外部類似概念 (例: UniT content memory) との射は、この時間差により**埋込ではなく射影**となる。

---

## 段階的展開

H-series は、ストア派心理学のプロセスモデルを体現:

```
H1: Propatheia (生理的反応)
    ↓
H2: Pistis (確信・同意)
    ↓
H3: Orexis (価値的志向)
    ↓
H4: Doxa (認識的判断)
```

この段階性は、「衝動」(Hormē) がいかにして形成されるかを示す。

---

## X-series 接続

| X | 接続 | 意味 |
|---|------|------|
| X-OH | ← O-series | 本質から傾向へ |
| X-SH | ← S-series | 様態から傾向へ |
| X-HA | → A-series | 傾向から精密へ |
| X-HK | → K-series | 傾向から文脈へ |

---

## 関連ドキュメント

- [schema.md](schema.md) — S-series（上流）
- [akribeia.md](akribeia.md) — A-series（下流）

---

*Hormē: ストア派における「理性的推進力」*
