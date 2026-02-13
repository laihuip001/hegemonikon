# マルコフ圏と Kalon 正則化

> **Status**: RESEARCH — 検証中の概念メモ
> **Origin**: Gemini メタ評価 (2026-02-12) の改善提案 + Creator の `/noe+!` 精査
> **Dependencies**: [axiom_hierarchy.md](axiom_hierarchy.md), [ccl/operators.md](../ccl/operators.md)

---

## 1. HGK の二軸構造

### 生成軸 (正本: axiom_hierarchy.md)

```
L0 (FEP) → L1 (Flow, Value) → L1.5 (Scale, Function) → L1.75 (Valence, Precision)
```

公理 × 公理 → 定理を生成する**座標空間**。

### 実行軸 (Gemini メタ評価からの射影)

```
存在 (FEP) → 構造 (圏論) → 認知 (推論) → 統覚 (CCL) → 審美 (Kalon)
```

認知処理の**抽象度**を表す層。生成軸と**直交**する。

> **圏論的解釈**: 生成軸 = 圏の内部構造 (対象と射の配置)。
> 実行軸 = 米田埋込からの外部観察 (関手圏 [C^op, Set] からの記述)。
> 両軸の presheaf が HGK の完全な像。

---

## 2. マルコフ圏 (Fritz, 2020)

### 定義

対称モノイダル圏 (C, ⊗, I) に copy/discard を追加:

- **copy**: X → X ⊗ X (情報の複製)
- **discard**: X → I (情報の破棄)
- 各射がマルコフ核の公理 (確率の保存) を満たす

### CCL との対応

| マルコフ圏 | CCL 演算子 | 認知的意味 |
|:-----------|:-----------|:-----------|
| ⊗ (モノイダル積) | `*` (内積) | 精度加重された融合 |
| copy (複製) | `%` (外積) | 全次元テンソル展開 |
| discard (破棄) | `-` (縮約) | 情報の必要十分化 |
| composition (合成) | `_` (シーケンス) | 射の合成 = 思考の連鎖 |
| id (恒等) | 無操作 | 変化なし |
| 条件付き独立 | `~` (振動) | 独立した視点間の往復 |

> **発見 (2026-02-12)**: `*` = 内積 と `%` = 外積 はマルコフ圏の ⊗ と copy に自然対応する。
> 本日の演算子改訂 (`*` の内積化、`%` の新設) が、意図せずマルコフ圏との整合性を実現した。

### L0-L1 接続の厳密化

FEP (連続的確率論) → 圏論的構造 (離散的代数) の変換を、マルコフ圏が橋渡し:

```
FEP: P(z|o) ∝ P(o|z)P(z)    [ベイズ更新]
      ↓ マルコフ圏のストリングダイアグラム
CCL: /noe~*dia               [収束振動 = variational inference]
```

**TODO**: Fritz 2020 の形式的定義を kernel/ に正式導入するか検討。

---

## 3. Kalon 正則化項

### 数学的定義

標準 VFE:

$$F = E_q[\ln q(z) - \ln p(o,z)] = \underbrace{D_{KL}[q \| p(z|o)]}_{\text{Complexity}} - \underbrace{\ln p(o)}_{\text{Accuracy}}$$

Kalon 正則化付き VFE:

$$F_{\text{kalon}} = F + \lambda \cdot K(q)$$

where:

$$K(q) = \frac{\text{useful information}}{\text{total information}} \times \frac{1}{\text{model complexity}}$$

### 操作的定義

| K(q) | 意味 | 例 |
|:-----|:-----|:---|
| 高い | 少ないパラメータで多くの有用情報を表現 | **美しい** |
| 低い | 冗長、不必要に複雑、情報密度が低い | **醜い** |

### CCL での表現

```
lim[K]{/noe~*dia}   = Kalon に収束するまで認識と判定を振動
V[/noe] < ε ∧ K > κ = 予測誤差が小さく、かつ情報密度が高い
```

### Fix(G∘F) との関係

Kalon = Fix(G∘F) where:

- F: 生成 (表現を生む)
- G: 判定 (表現を評価する)
- Fix: 不動点 (これ以上変わらない)

K(q) は Fix(G∘F) への**距離関数**:

$$d_{\text{Kalon}}(q) = \|q - \text{Fix}(G \circ F)\|$$

$K(q)$ が最大化されるとき $q = \text{Fix}(G \circ F)$ (Kalon に到達)。

---

## 参考文献

- Fritz, T. (2020). "A synthetic approach to Markov kernels, conditional independence and theorems of sufficient statistics." *Advances in Mathematics*, 370.
- Spisak, T. & Friston, K. (2025). FEP and self-orthogonalizing attractor networks.
- Kirchhoff, M. et al. (2018). "The Markov blankets of life." *JRSI*.

---

*v0.1 — Research memo (2026-02-12)*
