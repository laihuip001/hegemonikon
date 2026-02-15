# Affine Types / FnOnce — 不可逆操作の再発見

> **CCL**: `/gno+{source=rust.affine_types}`
> **消化タイプ**: T2 (再発見) — ~~T4 (概念輸入) から降格~~
> **Date**: 2026-02-15
> **Kalon テスト**: ✅ 「不可逆操作」は Rust を知らなくても理解できる

---

## 結論 (先行)

**Affine Types は HGK に既に存在していた。**

| Rust | HGK 既存対応 | 関係 |
|:-----|:------------|:-----|
| Affine Type (最大1回使用) | **BC-5 LBYL** (不可逆 → 事前確認) + **I-4 Undo** | 構造的同型 |
| FnOnce (環境を消費するクロージャ) | **`>>`** (構造的変換 — A は B に変わり消費) | 意味の一部 |
| Fn (何度でも呼べる) | 通常の WF | そのまま |
| FnMut (コンテキスト変更可能) | `+` 付き WF | そのまま |

**新構文ゼロ。新マクロゼロ。** 既存概念の再発見。

---

## 1. Affine Type とは何か

```rust
// Affine: 最大1回使う。使ったら消費。使わなくてもいい。
let file = File::open("data.txt").unwrap();
let content = read_to_string(file); // file は消費された
// file はもう使えない — これが Affine

// Linear: 正確に1回使う。使わなければエラー。
// Rust は Linear を強制しない (drop で暗黙消費)
```

核心: **一度使ったら元に戻せない操作がある**。

---

## 2. HGK にはすでに存在していた

### BC-5 の EAFP/LBYL 表

| 条件 | I-4 (Undo) | 方針 | Affine 相当 |
|:-----|:-----------|:-----|:------------|
| kernel/, SACRED_TRUTH | 不可逆 | **LBYL** | ✅ Affine |
| experiments/, sandbox | 可逆 (git) | **EAFP** | ❌ Non-Affine |
| pepsis/, designs/ | 可逆 (git) | **EAFP** | ❌ Non-Affine |
| 外部操作 (API, deploy) | 不可逆 | **LBYL** | ✅ Affine |
| 破壊的操作 (rm, DELETE) | 条件次第 | **LBYL** | ✅ Affine |

**この表は Affine Type の分類表そのもの。**

- LBYL 操作 = Affine (一度実行したら戻せない → 事前チェック必須)
- EAFP 操作 = Non-Affine (何度でもやり直せる → 失敗OK)

### I-4 の 3 原則

| 原則 | Affine との対応 |
|:-----|:---------------|
| Guard (大事なものには触らせない) | Affine 値の保護 |
| Prove (テストで示せ) | Affine 操作の事前検証 |
| **Undo (元に戻せる状態を保て)** | **Non-Affine を最大化せよ** |

I-4 は「Affine をなるべく減らせ」と言っている。
Rust の所有権モデルは「Affine を型で管理せよ」と言っている。
**同じ問題の異なるアプローチ。**

---

## 3. FnOnce — 一度だけ呼べるクロージャ

```rust
fn consume<F: FnOnce()>(f: F) {
    f();    // f を消費
    // f();  // ❌ 二度目は呼べない
}

fn reuse<F: Fn()>(f: &F) {
    f();    // OK
    f();    // OK — 何度でも呼べる
}
```

### CCL の対応

| Rust | CCL | 意味 |
|:-----|:----|:-----|
| `FnOnce` | `>>` | 構造的変換。A >> B: A は B に変わり消費される |
| `FnMut` | `+` | コンテキストを変更する WF |
| `Fn` | `-` or 無印 | コンテキストを変更しない WF |

`>>` が FnOnce 的な理由:

```ccl
# A >> B: A は B に変わる。A のコンテキストは消費される
/noe+{question} >> /bou+{will}
# 問い (A) が意志 (B) に変換された。問いのコンテキストは消費された。
```

### 具体例: FnOnce 的な WF

| WF | なぜ FnOnce 的か |
|:---|:----------------|
| `/bye` | セッションコンテキストを消費して Handoff を出力 |
| `/boot` | Handoff を消費してセッションを開始 |
| I-1 破壊的操作 | ファイル/DB の状態を不可逆的に消費 |

しかし: CCL では `/bye` を 2 回呼ぶことを**禁止できない**。
型チェッカーがないから。

### Hermēneus による FnOnce 検証 (将来)

並行モデル v1.1 で発見した通り、Hermēneus = CCL コンパイラ。
`>>` で変換された WF のコンテキストが再利用されていないかを
dispatch() でチェックすることは理論的に可能。

**優先度: 低**。現時点では設計メモとして記録。

---

## 4. 消化の質 — 丸呑みにしなかった理由

| 丸呑み (❌) | 消化 (✅) |
|:-----------|:---------|
| `@affine` マクロを追加 | BC-5 + I-4 が既に同じ概念 |
| `FnOnce` 型注釈を CCL に追加 | `>>` が既に FnOnce 的 |
| `Linear` 制約を WF に追加 | HGK は Linear を必要としない |

**消化 ≠ 丸呑み**。「既にあった」と気づくことが消化。

---

## 5. 教訓

> **Rust の Affine Types は、HGK が暗黙に持っていた
> 「可逆/不可逆」の区別を型システムで形式化したものだった。**
>
> HGK は BC-5 + I-4 で同じことを規約で実現している。
> Rust は型で強制する。HGK は環境 (BC) + コンパイラ (Hermēneus) で強制する。
>
> 三者は同じ問題の異なる解法:
>
> - **Rust**: 型チェッカー (コンパイル時)
> - **HGK**: BC (規約) + Hermēneus (パース時)
> - **人間**: 慎重さ (ランタイム) — これが一番弱い

---

*Pepsis Rust T2 | Affine Types / FnOnce — 不可逆操作の再発見 (2026-02-15)*
