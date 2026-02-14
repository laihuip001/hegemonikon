# Rust 哲学抽出 — 所有権モデルから認知原則へ

> **CCL**: `/gno+{source=rust.philosophy}`
> **消化タイプ**: T2 (Extraction)
> **Date**: 2026-02-14
> **Purpose**: Rust の設計哲学を HGK の認知原則として再解釈

---

## 📋 概要

Rust は「安全性・速度・並行性」を掲げるシステム言語だが、その核心は**所有権モデル**にある。
GC (Garbage Collector) なしでメモリ安全性を保証する仕組みは、認知リソース管理の数学的モデルとして極めて示唆的。

Python Zen が「19 の格言」だったのに対し、Rust の哲学はより**構造的・型理論的**。
格言よりも**型システムの制約**が設計思想を体現する。

---

## 🎯 原則マッピング

| # | Rust 哲学 | Hegemonikón 解釈 | 対応公理/定理 |
|:-:|:----------|:-----------------|:-------------|
| 1 | **Ownership: 値は一つの所有者** | 認知リソースの単一責任。一つの思考は一つのWFが所有 | Flow (I↔A) |
| 2 | **Borrowing: 一時的に貸す** | 認知リソースの参照渡し。覗くだけなら所有権を移さない | P1 Khōra |
| 3 | **Lifetime: 参照は所有者より長く生きない** | 依存の寿命制約。参照先がなくなれば参照も無効 | K2 Chronos |
| 4 | **Fearless Concurrency** | 所有権が並行性を安全にする。データ競合はコンパイル時に排除 | Function (Explore↔Exploit) |
| 5 | **Zero-Cost Abstractions** | 抽象化にコストなし。環境設計は「税」ではなく「投資」 | 第零原則 |
| 6 | **Make illegal states unrepresentable** | 不正な状態を型で排除。「間違いを犯せない設計」 | S2 Mekhanē |
| 7 | **Explicit over implicit (unsafe)** | 安全保証を外すなら明示する。暗黙の危険は許さない | A2 Krisis + BC-5 |
| 8 | **Exhaustive matching** | すべてのケースを処理する。見落としはコンパイルエラー | A4 Epistēmē |
| 9 | **Composition over inheritance** | 継承より合成。Trait で振る舞いを合成する | X-series (関係層) |

---

## 📐 CCL 設計原則への翻訳

### 原則 1: 単一所有権 (Single Ownership)

> **Rust**: Every value has exactly one owner.
> **CCL**: 認知リソースは一つの WF が所有する

**適用**:

- WF の入力は明示的に受け渡す。「暗黙の共有状態」を禁止
- `>>` (シーケンス) = 所有権の移動 (move)
- `*` (合成) = 借用 (borrow) — 値は元の WF に戻る

**CCL 対応表**:

```ccl
# Rust の move = CCL の >>
/noe >> /dia >> /ene   # 所有権が noe → dia → ene に移動

# Rust の borrow = CCL の *
/noe * /dia            # noe と dia は互いを「借用」して合成
                       # どちらも消費されない
```

---

### 原則 2: 借用規則 (Borrowing Rules)

> **Rust**: Either one mutable reference, or any number of immutable references.
> **CCL**: 変更可能な参照は一つだけ。読み取りは複数可。

**適用**:

- `+` (詳細化) = `&mut` — WF の出力を変更する。一度に一つだけ
- `-` (縮約) = `&` — WF の出力を読み取る。複数可
- `~` (振動) = `&mut` の交互取得 — 二つの視点が交互に変更権を持つ

**原則**: 「同時に二つの WF が同じコンテキストを変更してはならない」

---

### 原則 3: 寿命制約 (Lifetime Constraints)

> **Rust**: References must not outlive their referents.
> **CCL**: 依存する WF は、依存先より先に完了してはならない

**適用**:

```ccl
# 良い: /dia は /noe の出力に依存。/noe が先に完了
/noe+ >> /dia+{input: $noe_output}

# 悪い: /dia が /noe なしに実行される（ダングリング参照）
/dia+{input: ???}  # 入力なし = コンパイルエラー相当
```

**HGK への教訓**: WF の実行順序は依存グラフが決める。循環依存 = デッドロック。

---

### 原則 4: 恐れなき並行性 (Fearless Concurrency)

> **Rust**: Ownership ensures data races are impossible at compile time.
> **CCL**: 所有権が明確なら並行実行は安全

**適用**:

```ccl
# 独立した WF は並行可能 (それぞれが異なるリソースを所有)
/noe{topic: A} || /noe{topic: B}

# 共有リソースには明示的なロック（借用規則）
@scoped(lock: shared_context) {
  /dia+{input: shared_context}
}
```

---

### 原則 5: ゼロコスト抽象 (Zero-Cost Abstractions)

> **Rust**: What you don't use, you don't pay for.
> **CCL**: 環境設計は実行時コストなし

**HGK 解釈**: BC/Rule は「実行時のオーバーヘッド」ではなく「コンパイル時の検証」。
WF 実行中にBCを参照するコストは、BCを守らないことで発生するバグ修復コストより遥かに小さい。

**原則**: 「構造を作るコスト < 構造がないコスト」= 第零原則の再表現

---

### 原則 6: 不正状態の型排除 (Type-Safe States)

> **Rust**: Make illegal states unrepresentable.
> **CCL**: 不正な WF の組み合わせを構文で禁止する

**適用**:

```ccl
# Rust: enum State { Ready, Running, Done }
# → 「Ready かつ Done」は型として存在しない

# CCL: 深度レベルで不正な組み合わせを排除
# L0 (Bypass) で BC-9 (UML) が発動する = 型エラー相当
# → 深度レベルが自動的に不正な BC 発動を排除
```

**Python Zen #8 との共鳴**: 「例外を作らない」の型理論的表現。Python は規約で、Rust は型で。

---

### 原則 7: 明示的な安全保証の解除 (Explicit Unsafe)

> **Rust**: `unsafe` blocks must be explicitly marked.
> **CCL**: 安全保証を外すなら `@unsafe` で明示

**対応**:

| Rust | CCL | 意味 |
|:-----|:----|:-----|
| `unsafe { ... }` | `@unsafe { /ene+ }` | BC バイパスの明示 |
| `unsafe fn` | turbo モード | BC-5 の EAFP 動作 |
| `unsafe trait` | — | 未対応 (契約の解除) |

**原則**: 安全を解除する権利と責任は、呼び出し側にある。

---

### 原則 8: 網羅的パターンマッチ (Exhaustive Matching)

> **Rust**: The compiler ensures all patterns are covered.
> **CCL**: 判定 (/dia) はすべてのケースを処理する

**適用**:

```ccl
# Rust の match = CCL の条件分岐
I:[condition]{
  /ene+          # ケース: 条件成立
}
E:{
  /bou.akra+     # ケース: 条件不成立 (else を必ず書く)
}
# else なしの I: は「非網羅的マッチ」= 潜在的バグ
```

**Python との違い**: Python は `if/elif/else` で網羅性を保証しない。Rust は漏れをコンパイルエラーにする。HGK は `/dia+` で判定の網羅性を要求すべき。

---

### 原則 9: 継承より合成 (Composition over Inheritance)

> **Rust**: No inheritance. Traits define shared behavior.
> **CCL**: X-series (関係層) が定理間の合成を定義する

**適用**:

```
Python:                    Rust:                     HGK:
class Dog(Animal):         impl Speak for Dog {}     X-OS: O→S (共有: Flow)
  pass                     impl Walk for Dog {}      X-OH: O→H (共有: Flow)
                                                     # 定理間の関係 = trait 実装
```

**HGK の Trait 相当**: 6 Series のそれぞれが「Trait」。各定理が `impl` で具体的な振る舞いを定義。X-series が Trait 間の相互参照を表現。

---

## 📊 原則遵守チェックリスト

| # | 原則 | CCL チェック |
|:-:|:-----|:------------|
| 1 | 単一所有権 | 入力の出所が明示されているか |
| 2 | 借用規則 | 同時変更がないか |
| 3 | 寿命制約 | 依存先が先に完了するか |
| 4 | 恐れなき並行性 | 並行 WF が独立リソースを使うか |
| 5 | ゼロコスト抽象 | BC のコストが低いか |
| 6 | 型安全状態 | 不正な組み合わせが排除されているか |
| 7 | 明示的 unsafe | 安全保証の解除が明示されているか |
| 8 | 網羅的マッチ | 全ケースが処理されているか |
| 9 | 合成優先 | 継承ではなく合成を使っているか |

---

## 🔗 Python Zen との共鳴分析

| Rust 原則 | 対応する Python Zen | 共鳴の強さ | 差異 |
|:----------|:-------------------|:-------:|:-----|
| Explicit unsafe | Explicit > implicit (#2) | ★★★★★ | Rust は型で強制、Python は規約 |
| Exhaustive match | — | ★☆☆☆☆ | Python に相当なし。Rust 固有 |
| Composition > inheritance | — | ★★☆☆☆ | Python は多重継承を許容 |
| Zero-cost abstractions | Simple > complex (#3) | ★★★☆☆ | 同じ方向だがアプローチが異なる |
| Make illegal states unrepresentable | Special cases (#8) | ★★★★☆ | 規約 vs 型理論 |
| Single ownership | — | ★☆☆☆☆ | Python は GC で共有所有。本質的に異なる |

**発見**: Python と Rust は**方向的に一致**するが、**手段が根本的に異なる**。

- Python = **規約による安全性** (dynamic, duck typing)
- Rust = **型による安全性** (static, affine types)
- HGK = **両方**。BC は規約 (Python 的)、CCL 構文は型 (Rust 的)

---

*Pepsis Rust Phase 1 | `/gno+{rust.philosophy >> hegemonikon.principles}`*
