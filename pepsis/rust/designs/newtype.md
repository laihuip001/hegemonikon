# Newtype — 名前が意味を作る

> **CCL**: `/gno+{source=rust.newtype}`
> **消化タイプ**: T2 (再発見)
> **Date**: 2026-02-15
> **Kalon テスト**: ✅

---

## 1. Rust の Newtype パターンとは何か

```rust
struct UserId(u64);
struct PostId(u64);

fn get_user(id: UserId) -> User { ... }
fn get_post(id: PostId) -> Post { ... }

let user_id = UserId(42);
let post_id = PostId(42);

get_user(user_id);   // ✅ OK
get_user(post_id);   // ❌ コンパイルエラー! PostId ≠ UserId
```

**核心**: 同じ内部データ (u64) でも、**名前が違えば別の型**。
混同をコンパイル時に防ぐ。実行時コストはゼロ。

```rust
// Newtype = ラッパー構造体
struct Meters(f64);
struct Kilometers(f64);

// f64 の生の値では混同するが、Newtype では不可能
fn distance_km(d: Kilometers) -> Meters {
    Meters(d.0 * 1000.0)  // 変換を明示
}
```

---

## 2. CCL の派生体系 = Newtype

### 2.1 WF 派生の型安全性

```ccl
/noe+   # Noēsis の Deepening 派生 — 深く掘る
/noe-   # Noēsis の Reduction 派生 — 要約する
/noe*   # Noēsis の Expansion 派生 — 広げる
```

`/noe+` と `/noe-` は**同じ基底 WF** (Noēsis) だが、**異なる操作**。
UserId と PostId が同じ u64 だが異なる型であるのと同じ。

| Rust Newtype | CCL 派生 |
|:------------|:---------|
| `UserId(42)` | `/noe+{topic}` |
| `PostId(42)` | `/noe-{topic}` |
| `UserId ≠ PostId` | `/noe+ ≠ /noe-` |
| 中身は同じ u64 | 中身は同じ Noēsis |
| 混同 = コンパイルエラー | 混同 = 誤った認知操作 |

### 2.2 Hermēneus が Newtype をチェックする

```python
# Hermēneus dispatch:
# /noe+ と /noe- は異なる WF として扱われる
# 派生記号 (+/-/*) が「型」の役割を果たす
```

| チェック | Rust | CCL |
|:--------|:-----|:----|
| 型の混同 | コンパイルエラー | Hermēneus が派生を区別して dispatch |
| 暗黙の変換 | 不可 (明示的 From 必要) | 不可 (派生間の変換は未定義) |
| ゼロコスト | ✅ コンパイル時に解決 | ✅ 派生は意味の区別のみ |

---

## 3. 深い洞察: 派生は 3 種類、Newtype は無限

Rust の Newtype は任意の数を定義できる:

```rust
struct Temperature(f64);
struct Pressure(f64);
struct Humidity(f64);
// ... 無限に作れる
```

CCL の派生は **3 種類に限定されている**:

| 派生 | 意味 | 方向 |
|:----|:-----|:-----|
| `+` | 深化 / 追加 | 内側に掘る |
| `-` | 削減 / 要約 | 圧縮する |
| `*` | 拡張 / 探索 | 外側に広げる |

**なぜ 3 つか**: 6 座標のうち Function (Explore ↔ Exploit) の操作空間が
`+` (exploit), `-` (reduce), `*` (explore) の 3 方向だから。

> **Rust**: Newtype は「名前」で型を区別する。無限に定義できる。
> **CCL**: 派生は「方向」で意味を区別する。3 方向に制約される。
>
> CCL の制約は弱点ではなく**設計**:
> 認知操作の方向は「深く/浅く/広く」の 3 方向に集約できる。

---

## 4. 組合せ派生 = ネストした Newtype

```rust
struct Valid(UserId);    // ネスト: Valid な UserId
struct Unverified(UserId);  // ネスト: Unverified な UserId
```

```ccl
# CCL: 基底 WF + 派生 + 深度
/noe+   # L1: 標準的深化
/noe++  # L2: もっと深く (二重派生 = ネスト Newtype)
```

派生の組合せは Newtype のネストと同じ構造。
表現力は制限されるが、認知操作には十分。

---

## 5. Kalon テスト

| チェック | 結果 |
|:--------|:-----|
| Rust を知らなくても理解できるか | ✅ 「名前で区別する」は普遍的 |
| 新しい構文が必要か | ❌ 不要。派生 (+/-/*) で表現済み |
| HGK に既に存在していたか | ✅ WF 派生が Newtype |
| 消化で何を学んだか | 派生の 3 方向制約は Function 座標の帰結 |

---

*Pepsis Rust T2 | Newtype — 名前が意味を作る (2026-02-15)*
