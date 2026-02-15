# Pin<T> — 認知的不変性の消化

> **CCL**: `/gno+{source=rust.pin}`
> **消化タイプ**: T2 (再発見) — ~~T4 (概念輸入) から降格~~
> **Date**: 2026-02-15
> **Kalon テスト**: ✅ 「不変」「固定」は Rust を知らなくても理解できる

---

## 結論 (先行)

**Pin<T> は HGK に既に存在していた。**

| Rust | HGK 既存対応 | 関係 |
|:-----|:------------|:-----|
| `Pin<T>` (移動禁止) | **SACRED_TRUTH.md** (不変真理) | 構造的同型 |
| `Pin<T>` (自己参照保護) | **I-4 Guard** (大事なものには触らせない) | 同じ意図 |
| `Unpin` (移動OK) | 通常の WF / 通常のドキュメント | デフォルト |

**新構文ゼロ**。

---

## 1. Pin<T> とは何か

```rust
use std::pin::Pin;

// Pin: この値はメモリ上で動かない。
// 自己参照型 (async Future 等) の安全性に必要。
let pinned: Pin<Box<MyFuture>> = Box::pin(my_future);
// pinned は move できない。内部の自己参照が壊れるから。
```

核心: **ある値を「その場所に固定」し、移動を禁止する。**

なぜ必要か: 自己参照 (自分の一部が自分を指している) がある場合、
移動するとポインタが壊れる。

---

## 2. HGK にはすでに存在していた

### SACRED_TRUTH.md = Pin された公理

kernel/SACRED_TRUTH.md は「不変真理」= **移動も変更も禁止**。

| Rust | HGK |
|:-----|:----|
| `Pin<T>` | `kernel/SACRED_TRUTH.md` — 移動も変更も禁止 |
| なぜ Pin するか | 体系全体がこのドキュメントを参照している (自己参照) |
| Pin を外したら | 参照が壊れる = 体系が崩壊する |

**SACRED_TRUTH は Pin されている**。明示的に `Pin` と呼ばなくても。

### I-4 Guard = Pin の操作的定義

| I-4 原則 | Pin との対応 |
|:---------|:------------|
| **Guard**: 大事なものには触らせない | Pin<T>: 移動を禁止 |
| **Prove**: テストで示せ | Pin を外す前に unsafe であることを証明 |
| **Undo**: 元に戻せる状態を保て | Unpin: 移動しても安全なものは Pin 不要 |

### BC-5 EAFP/LBYL 表との対応

| BC-5 分類 | Pin 対応 | 理由 |
|:----------|:---------|:-----|
| kernel/, SACRED_TRUTH → LBYL | **Pin<T>** | 不可逆。移動禁止 |
| experiments/ → EAFP | **Unpin** | 可逆。自由に移動可能 |

**同じ分類表が 3 つの Rust 概念にマッピングされる**:

| BC-5 LBYL 対象 | Affine? | Pin? |
|:--------------|:----:|:----:|
| kernel/ | ✅ 不可逆 | ✅ 移動禁止 |
| 破壊的操作 | ✅ 不可逆 | — |
| SACRED_TRUTH | ✅ 不可逆 | ✅ 移動禁止 |

---

## 3. なぜ T4 → T2 に降格したか

「Pin を CCL に追加する」とは:

| 丸呑み (❌) | 消化 (✅) |
|:-----------|:---------|
| `@pin(WF)` マクロを追加 | SACRED_TRUTH + I-4 Guard が既に Pin |
| `Pin` 型注釈を CCL に追加 | kernel/ は暗黙に Pin されている |
| `Unpin` trait を CCL に追加 | Unpin = デフォルト (ほぼ全ての WF は移動可能) |

**HGK の固定構造**:

| 固定されたもの (Pin) | 理由 |
|:-------------------|:-----|
| 公理 (FEP) | 体系全体がこれに依存 |
| SACRED_TRUTH | 公理の具体的表現 |
| CONSTITUTION.md | アイデンティティ定義 |
| BC (Behavioral Constraints) | 認知プロテーゼ |
| 6 座標 (Flow/Value/Function/Scale/Valence/Precision) | 体系の座標軸 |

これらは全て**自己参照的**: 他の全てがこれらを参照しているから、動かせない。

**固定されていないもの (Unpin)**:

| 自由なもの (Unpin) | 理由 |
|:------------------|:-----|
| WF 定義 | 常に改善可能 |
| pepsis/ designs | 実験的 |
| τ層 WF | タスク固有 |
| experiments/ | sandbox |

---

## 4. 教訓

> **Pin は「大事なものは動かすな」という常識の型システム的表現。**
>
> HGK は SACRED_TRUTH + I-4 + BC でこれを実現している。
> Rust は型で強制する。HGK は環境 (ルール) で強制する。
>
> 構造が同じ。表現が違う。

---

*Pepsis Rust T2 | Pin<T> — 認知的不変性の再発見 (2026-02-15)*
