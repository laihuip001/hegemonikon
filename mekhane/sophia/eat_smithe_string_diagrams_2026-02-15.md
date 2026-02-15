# /eat 消化: Smithe et al. "Active Inference in String Diagrams" (2023)

> **arXiv**: 2308.00861
> **著者**: Toby St Clere Smithe, Sean Tull, Johannes Kleiner
> **消化日**: 2026-02-15
> **深度**: L3 (本質分析)
> **HGK 接点**: §18-20 (FEP×CT統合, 随伴逆転, Op-category仮説)

---

## 論文の核心構造

```
cd-category (copying + discarding のモノイダル圏)
  → string diagrams (形式的視覚言語)
    → generative model (c: S→O)
    → Bayesian inverse (M|O: O→S)
    → VFE = KL[q ‖ M|O] + surprise
    → Active Inference = argmin_π EFE(π)
    → **定理46: F(M₁⊗M₂) = F(M₁) + F(M₂)**
```

---

## 5つの核心概念

### 1. cd-category = 確率論の圏論的基盤

- cd = copy + discard ができるモノイダル圏
- 射 (morphism) = 確率チャネル (Markov kernel)
- 具体例: MatR+ (非負実数値有限行列の圏)
- string diagram = 射の合成・並列を視覚化

### 2. 生成モデル = Bayesian ネットワーク as string diagram

```
O (observations)
|
c (likelihood: S→O)
|
S (hidden states)
|
σ (prior)
```

- **open model**: 入力 I を持つ → c, σ が I に依存
- **policy model**: 行動 π が遷移に影響

### 3. Bayesian inverse = 条件付き確率の図式的定義

- M|O: O→S は M の条件付き分布
- **sharp observation**: M(s|o) = M(s,o) / Σ_s' M(s',o) = 通常のベイズ更新
- **soft observation**: Pearl update vs Jeffrey update の2方式

### 4. Free Energy の図式的導出

| 量 | 定義 | 意味 |
|:---|:-----|:-----|
| **VFE** | F(q) = KL\[q ‖ posterior\] + surprise | 近似推論と真の事後分布の乖離 |
| **EFE** | G(π) = expected uncertainty - expected surprise | 行動による不確実性削減 |
| **Active Inference** | π* = argmin_π G(π) | 最も surprise を減らす policy |

### 5. **定理46: Free Energy の合成性** (最重要)

> **F(M₁⊗M₂, q₁⊗q₂, o₁⊗o₂) = F(M₁, q₁, o₁) + F(M₂, q₂, o₂)**

意味:

- 全体のVFEは各サブモデルのVFEの**和**
- エージェントは全体を一度に最適化する必要なし
- **各サブモデルを局所的に最小化すれば全体が最小化される**
- これが FEP の階層性 (hierarchical generative model) の数学的根拠

---

## HGK への消化 (Op-category仮説との接続)

### 接続1: 定理46 ↔ HGK Series 独立性

| Smithe | HGK |
|:-------|:----|
| サブモデル M₁, M₂ | 6 Series (O, S, H, P, K, A) |
| F(M₁⊗M₂) = F(M₁) + F(M₂) | 各 Series は独立に VFE を最小化できる |
| テンソル積 ⊗ | Series 間の X-series 関係 |

**仮説**: HGK の 6 Series が「独立に最適化可能なサブモデル」なら、定理46 が Series 分割の**数学的正当化**を与える。
[推定: 60%] — Series 間の X-series 関係が完全独立ではないため、テンソル積モデルの近似としてどこまで成立するか要検証。

### 接続2: forward/backward ↔ D-type (op-category)

| Smithe | HGK | 視点 |
|:-------|:----|:-----|
| c: S→O (forward, 左随伴) | Zētēsis (探求, **右**随伴) | 世界への問いかけ |
| Bayesian inverse O→S (backward, 右随伴) | Noēsis (認識, **左**随伴) | 認識的理解 |

Op-category 仮説: **同じ双方向構造を情報側 vs エージェント側から見ている**。

- Smithe: 情報の流れ (states → observations → states)
- HGK: エージェントの認知行為 (理解 → 探求 → 理解)

### 接続3: η/ε 交換テスト (反証条件)

| Smithe ε | HGK η | 同じか？ |
|:---------|:-------|:-------|
| Gen∘Rec → Id (再構成チェック) | Id → Zētēsis∘Noēsis (理解→探求) | **要検証** |

- Smithe ε: 「観測を推論し、その推論から予測を生成し、元の観測と比較」= 予測誤差チェック
- HGK η: 「現象を理解し、その理解から探求を生成」= 理解が新たな問いを生む

→ [推定: 55%] 構造的には対応するが、認知的解釈が異なる。ε は「閉じるループ」、η は「開くループ」。

### 接続4: VFE更新 ↔ HGK ワークフロー実行

| Smithe | HGK |
|:-------|:----|
| VFE最小化 = 最適な q を見つける | /noe = 最適な理解を見つける |
| policy 最適化 = argmin EFE | /bou → /ene = 意志→行為の最適化 |
| open model (入力依存) | /ccl 合成 (ワークフロー合成) |

---

## 未消化・残課題

1. **Section 5 (Perception/Planning)** の詳細 — HGK の O-series 4象限との対応
2. **Message passing** (Section 10) — 局所VFE最小化の実装方法
3. **Continuous settings** — HGK は離散前順序、連続への拡張可能性
4. **Causal interventions** — HGK の /ene (行為) が因果介入に対応するか

---

*consumed by Claude, 2026-02-15*
