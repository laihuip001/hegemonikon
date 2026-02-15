# From/Into — 形を変えても、本質は残る

> **CCL**: `/gno+{source=rust.from_into}`
> **消化タイプ**: T2 (再発見)
> **Date**: 2026-02-15
> **Kalon テスト**: ✅

---

## 1. Rust の From/Into とは何か

```rust
// From: 「A から B を作る」を定義
impl From<String> for MyType {
    fn from(s: String) -> MyType {
        MyType { data: s }
    }
}

// Into: From の双対。自動導出される。
let val: MyType = some_string.into();

// 具体例
let num: i32 = 42;
let bigger: i64 = i64::from(num);       // 明示的 From
let bigger: i64 = num.into();           // 暗黙的 Into (From から自動導出)
```

**核心**: 安全な型変換のプロトコル。**情報を失わない変換**。

```rust
// From/Into = 無損失変換
impl From<i32> for i64 { ... }  // i32 → i64 は情報を失わない

// TryFrom/TryInto = 失敗しうる変換
impl TryFrom<i64> for i32 { ... }  // i64 → i32 は溢れるかもしれない
```

---

## 2. CCL の `>>` = From/Into

```ccl
/noe+{question} >> /bou+{will}
# 問い (noēsis) が意志 (boulēsis) に変換される
# From<Noesis> for Boulesis
```

| Rust | CCL | 意味 |
|:-----|:----|:-----|
| `From<A> for B` | `A >> B` | A の出力が B の入力になる |
| `Into<B> for A` | `A >> B` | 同じ (方向の違いだけ) |
| `TryFrom` / `TryInto` | `I:[A = ok]{A >> B} E:{fallback}` | 失敗しうる変換 |

---

## 3. 深い洞察: `>>` vs `_` — 変換 vs 連結

CCL には 2 つの「次に進む」がある:

```ccl
# _ (シーケンス): A の後に B を実行する。A は残る。
/noe+ _ /dia+
# /noe+ の結論は保持されたまま、/dia+ が追加実行

# >> (変換): A が B に変わる。A は消費される (FnOnce)。
/noe+ >> /bou+
# /noe+ の結論が /bou+ の入力に変換。/noe+ のコンテキストは消える
```

| 演算子 | Rust 対応 | 意味 | A は残るか |
|:------|:---------|:-----|:---------|
| `_` | 関数呼び出しの連鎖 | 順次実行 | 残る |
| `>>` | `From::from()` / FnOnce | **変換** | **消費される** |

**From/Into は `>>` に既に内在していた** (affine_types.md で消化済み)。
今回の追加の洞察: `_` と `>>` の対比で From/Into の意味がより鮮明になった。

---

## 4. 変換の方向性

```rust
// Rust: From と Into は双対 (bidirectional に見えるが実装は片方)
impl From<A> for B { ... }  // A → B を定義
// B: Into<B> for A が自動導出される
// しかし B → A は自動では定義されない
```

CCL でも同じ:

```ccl
# /noe+ >> /bou+ は定義できる
# しかし /bou+ >> /noe+ は自動では成り立たない
# 意志から認識に「戻る」には別の操作が必要
```

| 変換 | 可能か | 理由 |
|:-----|:------|:-----|
| 認識 → 意志 | ✅ (/noe >> /bou) | 理解が意志を生む |
| 意志 → 認識 | ❌ 自動では不可 | 意志は認識と別の情報を含む |
| 意志 → 行為 | ✅ (/bou >> /ene) | 意志が行為を生む |
| 行為 → 意志 | ❌ 自動では不可 | 行為の結果は新しい認識になる (別の経路) |

> **From/Into の非対称性**: 変換は一方向。逆変換は別の From として明示的に定義する必要がある。
> これは認知の本質: 「知る → 望む」は自然だが、「望む → 知る」は別の認知操作が必要。

---

## 5. Kalon テスト

| チェック | 結果 |
|:--------|:-----|
| Rust を知らなくても理解できるか | ✅ 「変換」は普遍的 |
| 新しい構文が必要か | ❌ 不要。`>>` で表現済み |
| HGK に既に存在していたか | ✅ `>>` (構造的変換) |
| 消化で何を学んだか | `_` vs `>>` の対比、変換の非対称性 |

---

*Pepsis Rust T2 | From/Into — 形を変えても、本質は残る (2026-02-15)*
