# Cog Topos 検証: PSh(Cog) は Elementary Topos

> **Project Kalon — L0.5 Verification**
> **Date**: 2026-02-07
> **Status**: ✅ 確認済

---

## 1. 問い

> Cog は topos か？ あるいは少なくとも presheaf category か？

## 2. 回答

### Cog 自体は topos **ではない**

| 条件 | Cog | 判定 |
|:-----|:----|:-----|
| 有限完備 (finite limits) | ❌ — 24対象・78射の有限圏で任意の pullback が存在しない | 不成立 |
| Cartesian closed | ❌ — 指数対象が定義できない | 不成立 |
| Subobject classifier | ❌ — Ω が存在しない | 不成立 |

> **Cog = 有限圏** (finite category)。topos ではない。

### PSh(Cog) は elementary topos **である** ✅

**定理**: 任意の小圏 C に対して、前層圏 PSh(C) = Set^{C^op} は elementary topos。

Cog は有限圏 ⊂ 小圏。したがって:

```
PSh(Cog) = Set^{Cog^op}  は  elementary topos
```

**PSh(Cog) が満たす性質**:

| 性質 | 構成 | CCL での意味 |
|:-----|:-----|:-------------|
| 有限完備 | 対象ごとに計算 | CCL 式の Limit/Colimit が well-defined |
| Cartesian closed | 指数対象 B^A が存在 | 「A → B の全ての方法」を対象として扱える |
| Subobject classifier Ω | Ω(U) = U 上の全篩 (sieve) | CCL 式の「部分的真理」を表現可能 |
| 内部論理 | 直観主義論理 | 排中律が成り立たない → ε-不確実性と整合 |

---

## 3. CCL への帰結

### 3.1 PSh(Cog) の対象 = CCL 式の解釈

CCL 式 `/noe+ >> /met` の結果は、Cog の対象そのものではなく、
**Cog 上の前層** (presheaf) = PSh(Cog) の対象として解釈される:

```
CCL式の結果 ∈ Ob(PSh(Cog))
         = 関手 F: Cog^op → Set
```

前層 F は「各定理 T に対して、F(T) = T の視点から見た情報の集合」を割り当てる。

**例**:

```
/noe+ の結果 = 前層 F where
  F(O1) = {Noēsis の深層認識の全出力}
  F(S1) = {Noēsis の結果を Metron の視点で見た集合}  ← X-OS による制限
  F(H1) = {Noēsis の結果を Propatheia の視点で見た集合}  ← X-OH による制限
  ...
```

### 3.2 内部論理 = 直観主義

PSh(Cog) の内部論理は**直観主義論理** (intuitionistic logic)。

| 古典論理 | 直観主義論理 (PSh(Cog)) | CCL での意味 |
|:---------|:----------------------|:-------------|
| P ∨ ¬P (排中律) | **成り立たない** | 全てが真か偽ではない |
| ¬¬P → P (二重否定除去) | **成り立たない** | 否定の否定は肯定ではない |
| 証明 = 構成 | **成り立つ** | 「存在する」= 構成できる |

> **FEP との整合**: 排中律の不在は、FEP の ε-不確実性（確信度が 0 or 1 でない）と自然に整合する。
> `V[] > 0` は PSh(Cog) の内部論理で「まだ確定していない」を表現。

### 3.3 Kalon の帰結

| 発見 | 意味 |
|:-----|:-----|
| PSh(Cog) は topos | CCL に内部論理が存在する |
| 内部論理は直観主義 | FEP の不確実性と整合 |
| Ω = 篩の集合 | 「部分的真理」が定式化可能 |
| 指数対象が存在 | 高階認知操作 (`^`) が well-defined |

---

## 4. 確信度

| 項目 | 確信度 | 根拠 |
|:-----|:-------|:-----|
| PSh(Cog) は topos | **0.95** | 数学的定理（証明不要、標準結果） |
| CCL 式 = PSh(Cog) の対象 | **0.70** | 解釈は自然だが、全演算子の形式的対応は未完 |
| 直観主義論理 ↔ FEP | **0.75** | 概念的整合は明確、形式的証明は未完 |

---

## 5. 次のステップ

これは **L1 (Cog の内部論理) への入口** であり、今の Kalon のスコープ (L0+L0.5) を超える。

L1 で必要な作業:

- [ ] PSh(Cog) の Ω (subobject classifier) の具体的構成
- [ ] CCL 演算子の PSh(Cog) 内部での形式的定義
- [ ] 内部論理からの CCL 構文の導出

> **判定**: L1 は Kalon の次フェーズとして正当。今は L0.5 の完了に集中。

---

*cog_topos_verification.md v1.0*
*Project Kalon — 2026-02-07*
