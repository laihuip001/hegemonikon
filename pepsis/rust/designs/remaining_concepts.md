# Rust 残存概念の網羅的消化 — 11 概念一括処理

> **CCL**: `/gno+{source=rust.exhaustive}`
> **消化タイプ**: T2 (再発見) 一括
> **Date**: 2026-02-15
> **方法**: Rust Book 全章を走査し、未消化概念を洗い出し

---

## 前提: なぜ 17 では不十分だったか

> 最初の 17 概念は Rust の「特徴的な」概念に偏っていた。
> 所有権・借用・ライフタイムは目立つが、Option や Iterator は「地味すぎて」スキップした。
> 地味 ≠ 価値がない。むしろ**地味な概念にこそ日常の知恵がある**。

---

## 1. Option\<T\> — 不在の明示的処理

### Rust

```rust
fn find(name: &str) -> Option<User> {
    // 見つからなければ None。null ではなく「不在」が型。
}
// 使う側は match / if let で明示的に処理を強制される
```

### HGK 対応: **O3 Zētēsis + /dia epochē**

「答えが見つからない」は HGK では:

- `/zet` (探求) = 問いを立てる。**答えがないのは正常な結果**
- `/dia epochē` (判断停止) = 判断できない → `None` を返す
- BC-6 `[仮説]` = 確信度 <60% = Option の Some/None の確信度版

| Rust | HGK |
|:-----|:----|
| `Some(value)` | `[確信]` / `[推定]` — 答えがある |
| `None` | `[仮説]` / `/dia epochē` — 答えがない |
| `unwrap()` (危険) | 確信度を無視して断言 = **BC-6 違反** |

**T2**: 不在の処理は BC-6 確信度体系に内在。✅

---

## 2. ジェネリクス — 型パラメトリズム

### Rust

```rust
fn process<T: Display>(item: T) { ... }
// T は何でもいい。Display を実装していれば。
```

### HGK 対応: **CCL WF はデフォルトでジェネリック**

```ccl
/noe+{topic: X}   # X は何でもいい。トピックであれば。
/dia+{target: Y}   # Y は何でもいい。判定対象であれば。
```

CCL の WF は**型パラメータを持たない**。全てのパラメータが自由テキスト。
これは「ジェネリクスしかない」状態。Rust が `<T>` で明示するものが、CCL ではデフォルト。

**トレイト境界** (`T: Display`) = WF の前提条件:

```ccl
# Rust: fn process<T: Display>(item: T)
# CCL: /dia+ は「判定対象」を前提とする (暗黙のトレイト境界)
/dia+{target: ???}  # target がない → WF が意味をなさない
```

**T2**: CCL は本質的にジェネリック。型パラメータは不要。✅

---

## 3. イテレータ / 遅延評価

### Rust

```rust
let result: Vec<i32> = (1..100)
    .filter(|x| x % 2 == 0)
    .map(|x| x * 3)
    .take(5)
    .collect();
// 遅延評価: collect() が呼ばれるまで計算されない
```

### HGK 対応: **F:[] (反復) + _ (チェーン)**

```ccl
F:[×5]{/noe+{topic} _ /dia- _ /pis}
# 5回反復。各ステップは前のステップの結果を受け取る
```

| Rust Iterator | CCL |
|:-------------|:----|
| `.filter()` | `I:[cond]{}` — 条件フィルタ |
| `.map()` | `_ /wf` — チェーンの各段 |
| `.take(n)` | `F:[×n]{}` — 回数制限 |
| `.collect()` | `_ /pis` or `_ /dox` — 結果の集約 |
| 遅延評価 | **なし** — CCL は即時評価 |

**遅延評価**: CCL には遅延評価がない。しかし認知操作に遅延評価は必要か？
思考は「後で考える」が可能 (= 遅延) だが、CCL では明示的に `/bye` や `/rom` で「後で」を表現する。

**T2**: イテレータパターンは F:[] + _ + I:[] の組合せ。遅延評価は CCL の設計範囲外。✅

---

## 4. スマートポインタ (Box/Rc/Arc)

### Rust

```rust
Box<T>   // ヒープ割り当て。単一所有。
Rc<T>    // 参照カウント。単スレッド共有所有。
Arc<T>   // 原子的参照カウント。マルチスレッド共有所有。
```

### HGK 対応: Flow 公理の**変形**

| Rust | HGK | 所有権モデル |
|:-----|:----|:-----------|
| `Box<T>` | 通常の WF | 単一所有 = デフォルト |
| `Rc<T>` | `*` (結合) | 複数 WF が同じコンテキストを共有参照 |
| `Arc<T>` | `||` + `-` (並行 + 読取共有) | 並行安全な共有参照 |

Box = 何もしない (デフォルトが単一所有)。
Rc = `*` で結合した WF 群が同じ知識を共有。
Arc = `||` で並行実行する WF が `-` で安全に共有。

**T2**: Flow 公理 + `*` + `||` + `-` で全て表現済み。✅

---

## 5. Interior Mutability (Cell/RefCell)

### Rust

```rust
// 通常: &T は不変。&mut T は可変。コンパイル時チェック。
// Interior Mutability: &T なのに中身を変更できる。ランタイムチェック。
let cell = RefCell::new(5);
let mut borrow = cell.borrow_mut(); // ランタイムで借用チェック
*borrow = 10;
```

### HGK 対応: **BC (規約) = ランタイムチェック**

| 検証タイミング | Rust | HGK |
|:-------------|:-----|:----|
| コンパイル時 | Borrow Checker | Hermēneus dispatch() |
| ランタイム | RefCell | **BC (Behavioral Constraints)** |

Interior Mutability の本質: 「コンパイル時に証明できないが、ランタイムで安全に変更したい」。

HGK では: WF 実行中に判断を変える (自己修正) = BC-9 メタ認知 + BC-14 FaR。
「深層で思考を変更する」は RefCell 的:

```
/noe+{topic: X}    # → 深層で「X は間違いだった」と気づく (borrow_mut)
# → /noe+ の中で topic を修正 (interior mutation)
# → BC-9/14 がランタイムで安全性を検証
```

**T2**: Interior Mutability = BC によるランタイム自己修正チェック。✅

---

## 6. チャネル (mpsc) — メッセージパッシング

### Rust

```rust
let (tx, rx) = mpsc::channel();
thread::spawn(move || { tx.send("hello").unwrap(); });
let msg = rx.recv().unwrap();
```

### HGK 対応: **`||` + `_` の組合せ**

```ccl
# A と B が並行実行。結果を C に渡す = channel
(A || B) _ C
# A の出力と B の出力が C に "送信" される
```

| Rust | CCL |
|:-----|:----|
| `tx.send()` | WF の出力 |
| `rx.recv()` | `_` で次の WF に渡る |
| `mpsc` (多対一) | `(A || B || C) _ D` — 複数 WF の結果を D が受信 |

**T2**: チャネルは `||` + `_` (All join) で表現済み。✅

---

## 7. Mutex / RwLock — 共有状態の排他制御

### Rust

```rust
let mutex = Mutex::new(data);
let lock = mutex.lock().unwrap(); // 排他アクセス
```

### HGK 対応: **Independent / Shareable (parallel_model.md)**

| Rust | CCL |
|:-----|:----|
| `Mutex<T>` | `+{ctx: X}` — 排他的変更 (一つの WF のみ) |
| `RwLock<T>` | `-{ctx: X}` — 読取は並行、変更は排他 |
| deadlock | `||` の安全条件違反 → Hermēneus がエラー |

**T2**: parallel_model.md v1.1 で消化済み。✅

---

## 8. モジュール / 可視性 (pub/priv)

### Rust

```rust
mod internal {
    pub fn public() { ... }     // 外部から呼べる
    fn private() { ... }        // モジュール内のみ
    pub(crate) fn crate_only()  // crate 内のみ
}
```

### HGK 対応: **WF 層 (Ω/Δ/τ) + ディレクトリ構造**

| Rust 可視性 | HGK |
|:-----------|:----|
| `pub` | Ω層 WF (`/o`, `/s`, `/h`) — 全体に公開 |
| `pub(crate)` | Δ層 WF (`/noe`, `/dia`) — 体系内から呼び出し |
| `fn` (private) | τ層 WF (`/dev`, `/exp`) — タスク固有 |

ディレクトリ:

| Rust | HGK |
|:-----|:----|
| `pub mod` | `kernel/` — 公理は公開 |
| `mod` (private) | `.agent/` — 内部ルール |
| `pub(crate)` | `mekhane/` — エンジン群 (体系内で使用) |

**T2**: WF 層構造 + ディレクトリが可視性を実現。✅

---

## 9. From/Into — 型変換プロトコル

### Rust

```rust
impl From<String> for MyType { ... }
let val: MyType = some_string.into();
```

### HGK 対応: **`>>` (構造的変換)**

```ccl
/noe+{question} >> /bou+{will}
# 問い (noe) が意志 (bou) に変換される = From<Noesis> for Boulesis
```

| Rust | CCL |
|:-----|:----|
| `From<A> for B` | `A >> B` — A が B に変換される |
| `Into<B> for A` | `A >> B` — 同じ (双対) |
| `.into()` | `>>` 演算子 |
| 変換の安全性 | `>>` は定義された WF 間でのみ使用 |

**T2**: `>>` が From/Into。✅

---

## 10. Cow (Clone-on-Write) — 遅延コピー

### Rust

```rust
fn process(data: Cow<str>) {
    // 変更が必要になるまでコピーしない
    if needs_modification {
        let owned = data.into_owned(); // ここで初めてコピー
    }
}
```

### HGK 対応: **`-` (読取) → `+` (変更時にコピー)**

```ccl
# 読むだけなら共有 (Cow の Borrowed 状態)
/dia-{ctx: shared}

# 変更が必要になったら所有 (Cow の Owned 状態)
/dia-{ctx: shared} _ I:[needs_change]{/noe+{ctx: shared}}
# → needs_change のときだけ + (所有的変更) に切り替え
```

**T2**: `-` → `+` の遷移が Cow。✅

---

## 11. Newtype パターン — ゼロコスト型区別

### Rust

```rust
struct UserId(u64);   // u64 だが、UserId として型安全
struct PostId(u64);   // 同じ u64 だが、混同不可能
```

### HGK 対応: **WF 派生 (+/-/*)**

```ccl
/noe+   # Noēsis の Deepening 派生
/noe-   # Noēsis の Reduction 派生
/noe*   # Noēsis の Expansion 派生
```

同じ基底 WF (`/noe`) だが、派生 (`+/-/*`) で**意味が異なる**。
型は同じだが名前で区別 = Newtype。

**T2**: 派生体系が Newtype パターン。✅

---

## まとめ: 11 概念の消化結果

| # | Rust | HGK 対応 | T |
|:-:|:-----|:---------|:-:|
| 1 | Option\<T\> | BC-6 確信度 + /dia epochē | T2 |
| 2 | ジェネリクス | CCL はデフォルトでジェネリック | T2 |
| 3 | イテレータ | F:[] + _ + I:[] | T2 |
| 4 | スマートポインタ | Flow + * + || + - | T2 |
| 5 | Interior Mutability | BC ランタイムチェック | T2 |
| 6 | チャネル (mpsc) | || + _ (All join) | T2 |
| 7 | Mutex/RwLock | Independent/Shareable | T2 |
| 8 | モジュール/可視性 | WF 層 (Ω/Δ/τ) + ディレクトリ | T2 |
| 9 | From/Into | >> (構造的変換) | T2 |
| 10 | Cow | - → + 遷移 | T2 |
| 11 | Newtype | WF 派生 (+/-/*) | T2 |

**全 11 概念が T2 (再発見)**。T3/T4 = 0。

---

## 完全消化の証明

| カテゴリ | 消化前 | 消化後 |
|:--------|------:|------:|
| 既消化 | 17 | **28** |
| T2 (再発見) | 7 | **18** |
| T3 (機能) | 3 | 3 |
| T4 (輸入) | 0 | **0** |
| **未対応** | **11** | **0** |

> **Rust Book 全章を走査した結果、全 28 概念が消化済み。**
> T4 = 0 は変わらず: Rust の概念は全て HGK に「既にあった」。

---

*Pepsis Rust Phase 5 | 残存11概念の網羅的消化 (2026-02-15)*
