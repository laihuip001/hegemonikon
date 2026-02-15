# Interior Mutability — ランタイムで安全に変える

> **CCL**: `/gno+{source=rust.interior_mutability}`
> **消化タイプ**: T2 (再発見)
> **Date**: 2026-02-15
> **Kalon テスト**: ✅

---

## 1. Rust の Interior Mutability とは何か

通常の Rust:

```rust
let x = 5;         // 不変。変更不可
let mut x = 5;     // 可変。変更可能
let y = &x;        // 不変借用。変更不可
let z = &mut x;    // 可変借用。変更可能。但し排他的
```

**問題**: `&T` (不変参照) を持っているのに、中身を変えたいことがある。
例: カウンタ、キャッシュ、遅延初期化。

**Interior Mutability の解決策**:

```rust
use std::cell::RefCell;

let data = RefCell::new(5);

// &data (不変参照) なのに中身を変更できる
{
    let mut borrow = data.borrow_mut();  // ← ランタイムチェック
    *borrow = 10;
}
// borrow_mut() が2回呼ばれたら panic! (ランタイムエラー)
```

**核心**: コンパイル時に安全性を証明できないが、ランタイムで検証する。

| 方式 | Rust | チェック時点 | 失敗時 |
|:-----|:-----|:-----------|:-------|
| 通常 | `&mut T` | コンパイル時 | コンパイルエラー |
| Interior | `RefCell<T>` | **ランタイム** | panic! |
| unsafe | `UnsafeCell<T>` | なし | 未定義動作 |

---

## 2. HGK の三層安全モデル

HGK にも同じ三層がある:

| 層 | Rust | HGK | チェック |
|:---|:-----|:----|:---------|
| コンパイル時 | Borrow Checker | **Hermēneus dispatch()** | CCL 解析時 |
| ランタイム | RefCell | **BC (Behavioral Constraints)** | WF 実行中 |
| unsafe | UnsafeCell | **BC-5 EAFP (明示的リスク許容)** | チェックなし (自己責任) |

これは**構造的同型**。

### 2.1 Hermēneus = Borrow Checker

```python
# dispatch() が CCL を解析して安全性をチェック
def dispatch(ccl_expression):
    if "||" in ccl_expression:
        # 並行実行の安全条件をコンパイル時にチェック
        check_parallel_safety(left_wf, right_wf)
```

Hermēneus は CCL を実行前にパースして安全条件を検証する。
これは Rust の Borrow Checker と同じ役割。

### 2.2 BC = RefCell

```
# WF 実行中に BC が安全性をランタイムチェック
/noe+{topic: sacred_axiom}
  → BC-5: 「これは kernel/ の変更。LBYL が必要」
  → BC-14: FaR チェック発動
  → BC-9: メタ認知チェック
```

BC は WF 実行中にルールを検証する。
Rust の RefCell がランタイムで借用ルールを検証するのと同じ。

**RefCell が panic! するのは、ルール違反が検出されたとき。**
**BC が違反をフラグするのは、行動規範が破られたとき。**

| RefCell | BC |
|:--------|:---|
| `borrow()` 成功 | BC チェック通過 |
| `borrow_mut()` 成功 | BC-5 LBYL 確認済み |
| 二重 `borrow_mut()` → panic! | **BC 違反検出** → 即座に停止 |

### 2.3 BC-5 EAFP = unsafe

```
# experiments/ での作業 = unsafe ブロック
# BC-5 が「EAFP (許可より謝罪)」を許容する場
```

Rust の `unsafe` は「コンパイラを信じるな、自分で保証する」。
BC-5 EAFP は「事前チェック不要、失敗したらリカバリする」。

---

## 3. 深い洞察: なぜランタイムチェックが必要か

### Rust の理由

コンパイル時に全ての安全性を証明できない場合がある:

- グラフ構造 (相互参照)
- キャッシュ (読み取り中に更新)
- Observer パターン

### HGK の理由

認知操作の安全性を事前に完全に検証できない場合がある:

- **自己修正**: /noe+ の途中で前提が崩れる
- **対話的発見**: /zet+ で新しい問いが浮上し、計画が変わる
- **文脈依存**: 同じ WF でも文脈によって安全/危険が変わる

> **共通の真理**: 完全な事前チェックは不可能な場合がある。
> そのとき、ランタイムチェック (RefCell / BC) が安全の最後の砦になる。

---

## 4. Cell vs RefCell の区別

```rust
// Cell<T>: Copy 型のみ。借用なしで値を出し入れ
let cell = Cell::new(42);
cell.set(100);         // 借用チェック不要。値がコピーされる

// RefCell<T>: 任意の型。借用をランタイムで追跡
let refcell = RefCell::new(vec![1, 2, 3]);
let mut borrow = refcell.borrow_mut();  // ランタイム追跡あり
borrow.push(4);
```

| Rust | HGK |
|:-----|:----|
| `Cell<T>` (軽量) | BC-6 確信度の更新。値を置き換えるだけ。副作用なし |
| `RefCell<T>` (重量) | BC-5 + BC-14。構造的変更。ランタイムで安全性を検証 |

- Cell = 「確信度を 70% → 85% に更新」(軽い変更)
- RefCell = 「設計方針を変更する」(重い変更。副作用チェック必須)

---

## 5. HGK に欠けている可能性

[主観] RefCell の panic は**即座に停止**する。BC 違反は**違反ログに記録**されるが、
即座に停止しないことがある。

→ BC 違反の重篤度に応じた自動停止メカニズム:

| 重篤度 | RefCell 対応 | HGK 対応 |
|:------|:-----------|:---------|
| Critical | panic! (即座に停止) | I-1 違反 → 即座に停止 (既存) |
| Warning | — (Rust にはない) | BC 違反 → 警告 + 続行 (既存) |
| Info | — | メタ認知チェック通過 → 記録のみ |

→ 既に機能している。RefCell の二値 (OK/panic) よりも HGK の三値 (OK/warn/stop) の方が段階的。

---

## 6. Kalon テスト

| チェック | 結果 |
|:--------|:-----|
| Rust を知らなくても理解できるか | ✅ 「ルールを事前にチェックするか、実行中にチェックするか」 |
| 新しい構文が必要か | ❌ 不要。BC は既にランタイムチェック |
| HGK に既に存在していたか | ✅ 三層安全モデルが構造的に同型 |
| 消化で何を学んだか | HGK の Hermēneus/BC/EAFP = Rust の Borrow Checker/RefCell/unsafe |

---

*Pepsis Rust T2 | Interior Mutability — ランタイムで安全に変える (2026-02-15)*
