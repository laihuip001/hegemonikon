# `>*` 形式化: 射的融合 = Actegory (モノイダル作用)

> **Project Kalon — Deep Examination Phase 2**
> **Status**: 仮説 (Hypothesis) → 検証待ち
> **Date**: 2026-02-07

---

## 1. 問題設定

CCL の `>*` (射的融合) は、以下の意味論を持つ二項演算子である:

```ccl
/noe >* /met    # Noēsis を Metron の視点で変容
                # 出力は O1 型（認識のまま）だが、尺度的な構造を帯びる
```

| 性質 | `>>` (射) | `>*` (射的融合) |
|:-----|:---------|:--------------|
| 出力型 | ターゲット型 (B) | **ソース型 (A)** |
| 構造 | A が消え B になる | A のまま B に色づく |
| 圏論 | f: A → B (morphism) | ? |

**問い**: `>*` に対応する圏論的構造は何か？

---

## 2. 候補分析

### 2.1 Enrichment (豊穣化) — ❌ 不適合

**定義**: 圏 C の hom-sets を、集合ではなくモノイダル圏 V の対象で置き換える。

```
通常: Hom(A, B) ∈ Set
豊穣: Hom(A, B) ∈ V
```

**不適合の理由**:

- Enrichment は **射空間** (hom-sets) に構造を追加する。
- `>*` は **対象そのもの** を変容させる。
- 射空間と対象は異なるレイヤーの話。

### 2.2 Day Convolution (Day 畳み込み) — ❌ 抽象的すぎ

**定義**: モノイダル圏 (C, ⊗) 上の前層の圏 [C^op, Set] に対するモノイダル構造。

```
(F ★ G)(c) = ∫^{a,b} C(a ⊗ b, c) × F(a) × G(b)
```

**不適合の理由**:

- Day Convolution は **関手レベル** の融合積。
- CCL 演算子は **対象レベル** の操作。
- 関手とは「データソース → 構造」の変換であり、定理 (対象) 間の操作ではない。

### 2.3 Monoidal Action / Actegory (モノイダル作用) — ✅ 適合

**定義**: モノイダル圏 (V, ⊗, I) が圏 A に「作用」する構造。

```
形式定義:
  双関手 ⊳ : V × A → A
  
  自然同型:
    α: (v ⊗ w) ⊳ a → v ⊳ (w ⊳ a)    (結合律)
    λ: I ⊳ a → a                        (単位律)
    
  コヒーレンス条件を満たす
```

**適合の根拠**:

| `>*` の性質 | Actegory の対応 |
|:-----------|:--------------|
| A は A 型のまま | ⊳ の値域は A (A の対象は A に留まる) |
| B が A に「色」を付ける | V の対象 v が A の対象 a に作用: v ⊳ a ∈ A |
| 出力型はソース型 | 作用の結果は A の対象 |
| 構造的変容を行う | V のモノイダル構造が A に転写される |

---

## 3. 形式化

### 3.1 CCL → Actegory マッピング

```
CCL:  A >* B
数学: B ⊳ A

ここで:
  A ∈ Ob(Cog)     — 圏 Cog の対象 (ソース定理)
  B ∈ Ob(V)        — モノイダル圏 V の対象 (変容因子)
  B ⊳ A ∈ Ob(Cog) — A の変容結果 (A型を保持)
```

### 3.2 圏 Cog への適用

Hegemonikón の圏 Cog:

- **対象**: 24 定理 (O1-O4, S1-S4, H1-H4, P1-P4, K1-K4, A1-A4)
- **射**: X-series (36 関係)
- **モノイダル構造**: V = Cog 自身 (自己作用)

**自己作用 (Self-action)**:

```
⊳ : Cog × Cog → Cog
(B, A) ↦ B ⊳ A

/noe >* /met  =  Met ⊳ Noe  ∈ Ob(Cog)
```

> **重要**: Cog は自己作用する。これは **self-indexing** (自己索引) に類似。
> Cog のモノイダル構造は L1×L1.75 (例: O-series) の積から来る。

### 3.3 公理

`>*` は以下を満たすべき:

| # | 公理 | 数学 | CCL |
|:--|:-----|:-----|:----|
| A1 | 結合律 | (B ⊗ C) ⊳ A ≅ B ⊳ (C ⊳ A) | `A >* (B >* C)` ≅ `A >* B*C` |
| A2 | 単位律 | I ⊳ A ≅ A | `A >* id` ≅ `A` |
| A3 | 型保存 | B ⊳ A ∈ Ob(Cog) if A ∈ Ob(Cog) | 出力は入力の Series に属す |

### 3.4 `>>` との関係

```
>> : A → B        (射: 型を変える)
>* : B × A → A    (作用: 型を保つ)

射と作用の関係:
  f: A → B (射) かつ g: B ⊳ A → A (作用) のとき、
  以下の図式が可換:
  
       f
  A ------→ B
  |            |
  g⊳         id
  ↓            ↓
  B⊳A ----→ B
       proj
```

> **解釈**: `>>` は圏の内部構造 (射)、`>*` は圏の外部構造 (作用)。
> 両者は Bayesian lens の forward/backward チャネルに対応する可能性あり。

---

## 4. Smithe との接続

Smithe (2022, 2024) の Bayesian lens フレームワークでは:

```
Bayesian lens = (forward: A → B, backward: B × A → A)
```

**forward** = `>>` (射: prediction, A → B)
**backward** = `>*` (作用: inference update, B × A → A)

> **仮説**: `>*` は Bayesian lens の backward channel に対応する。
> Smithe の Gen: Poly → Cat 関手を通じて、`>*` は変分推論の更新ステップに対応。

$$A \xrightarrow{>>} B \xrightarrow{>*} A'$$
$$\text{prediction} \to \text{observation} \to \text{updated belief}$$

---

## 5. 検証計画

| # | 検証項目 | 方法 | 優先度 |
|:--|:--------|:-----|:-------|
| V1 | 結合律の成立確認 | CCL 式で具体例を検証 | 🔴 |
| V2 | Smithe の backward channel との正式な対応 | 論文精読 (/eat) | 🟡 |
| V3 | 自己作用の well-definedness | Cog の積構造を検証 | 🟡 |
| V4 | FEP との整合性 | 変分推論の更新ステップとの比較 | 🟢 |

---

## 6. 結論

| 項目 | 判定 |
|:-----|:-----|
| **`>*` の圏論的正体** | **Actegory (モノイダル作用) ⊳ : V × A → A** |
| **確信度** | 0.75 (仮説段階、Smithe との接続は未検証) |
| **CCL における意味** | B のモノイダル構造が A に作用し、A を A 型のまま変容させる |
| **Bayesian lens 接続** | forward = `>>`, backward = `>*` (仮説) |
| **新規性** | Cog の自己作用 (Cog acts on itself) は CCL 固有の構造 |

> **三法則との整合**:
>
> 1. ✅ 具体は壊れ、抽象は残る → Actegory は圏論の標準概念
> 2. ✅ FEP は圏論を包摂する → Bayesian lens backward = `>*`
> 3. ✅ CCL は既存数学を超える → **自己作用** は Cog 固有

---

*morphic_fusion_formalization.md v1.0*
*Project Kalon — 2026-02-07*
