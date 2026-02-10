---
description: K-series（文脈定理 K1-K12）を駆動し、状況に応じた文脈フィルターを適用する。
hegemonikon: Kairos
modules:
- K1
- K2
- K3
- K4
- K5
- K6
- K7
- K8
- K9
- K10
- K11
- K12
risk_tier: L1
risks:
- none
reversible: true
requires_approval: false
fallbacks: []
---

# /k: 文脈定理ワークフロー

> **Hegemonikón Layer**: Level 2c K-series (Kairos)
> **目的**: 選択公理の組み合わせで「どの状況でどう判断するか」を導出
> **参照**: [kairos.md](../../kernel/kairos.md)

---

## 本質

K-series は「文脈フィルター」として機能する。

| シリーズ | 性質 | 問い |
|----------|------|------|
| O-series | 本質的 | 「何であるか」 |
| T-series | 様態的 | 「どのように在るか」 |
| **K-series** | **文脈的** | **「どの状況で在るか」** |

---

## 発動条件

| トリガー | 説明 |
|----------|------|
| `/k` | 文脈定理ワークフローを起動 |
| 状況依存判断 | 時間・レベル・主体・動機の文脈が重要な場合 |
| `/plan` 内 | 計画時に文脈を明示化したい場合 |

---

## Process

### Step 1: 選択公理の特定

現在の状況で支配的な選択公理を特定する：

| 選択公理 | ID | 問い |
|----------|-----|------|
| **Tempo** | F/S | 短期か長期か？ |
| **Stratum** | L/H | 低次か高次か？ |
| **Agency** | S/E | 自己か環境か？ |
| **Valence** | +/- | 接近か回避か？ |

### Step 2: Kairos マトリクス選択

2つの選択公理の組み合わせから、12個の Kairos を選択：

| 軸 A → 軸 B | K-ID |
|-------------|------|
| Tempo → Stratum | K1 |
| Tempo → Agency | K2 |
| Tempo → Valence | K3 |
| Stratum → Tempo | K4 |
| Stratum → Agency | K5 |
| Stratum → Valence | K6 |
| Agency → Tempo | K7 |
| Agency → Stratum | K8 |
| Agency → Valence | K9 |
| Valence → Tempo | K10 |
| Valence → Stratum | K11 |
| Valence → Agency | K12 |

### Step 3: 文脈適用

選択された Kairos のマトリクスを参照し、具体的な行動指針を導出。

---

## 出力形式

```
┌─[Hegemonikón]──────────────────────┐
│ K{N} {Axis A}→{Axis B}: 文脈適用   │
│ 状況: {現在の状況記述}             │
│ 選択: K{N}-{XX} ({意味})           │
│ 指針: {具体的行動指針}             │
└────────────────────────────────────┘
```

---

## 使用例

**例1: 緊急タスク**
```
/k
状況: 期限が1時間以内のバグ修正
→ K1 (Tempo→Stratum): K1-FL（即時パターン認識）
→ 指針: 考えずに直感で動く、最小限の修正
```

**例2: キャリア計画**
```
/k
状況: 3年後のキャリアを考える
→ K2 (Tempo→Agency): K2-SS（自己成長戦略）
→ 指針: 長期的な自己スキル習得に投資
```

---

## T-series との統合

```
[T-series 機能] + [Kairos] = 文脈化された行動

例: T1 Aisthēsis + K7-SF = 「自己の即時反応として知覚する」
例: T6 Praxis + K3-S+ = 「長期目標に向けた行動を実行する」
```

---

## Hegemonikon Status

| Module | Workflow | Status |
|--------|----------|--------|
| K1-K12 | /k | Ready |
