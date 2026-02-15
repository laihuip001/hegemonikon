# Generics — 全ては文脈次第

> **CCL**: `/gno+{source=rust.generics}`
> **消化タイプ**: T2 (再発見)
> **Date**: 2026-02-15
> **Kalon テスト**: ✅

---

## 1. Rust のジェネリクスとは何か

```rust
// T は「何でもいい」。しかし Display を実装していなければならない。
fn print_value<T: Display>(value: T) {
    println!("{}", value);
}

// 複数の境界
fn process<T: Clone + Debug + Serialize>(item: T) { ... }

// where 句で可読性向上
fn complex<T, U>(t: T, u: U) -> impl Display
where
    T: Clone + Debug,
    U: Into<String>,
{ ... }
```

**2 つの核心**:

1. **パラメトリズム**: 同じ関数が異なる型で動く
2. **トレイト境界**: 「何でもいい」に制約を付ける

### Monomorphization

```rust
// コンパイラが T=i32, T=String の2つの関数を生成する
// ゼロコスト抽象: 実行時にはジェネリックではない
print_value(42);        // → print_value_i32(42)
print_value("hello");   // → print_value_str("hello")
```

---

## 2. CCL は「ジェネリクスしかない」

```ccl
/noe+{topic: ???}
```

`topic` は何でもいい。型制約がない。全ての WF が**デフォルトでジェネリック**。

```ccl
/noe+{topic: "Rust の所有権"}          # topic = 自然言語
/noe+{topic: core_mapping.md}          # topic = ファイル
/noe+{topic: FEP}                      # topic = 概念
/noe+{topic: 42}                       # topic = 数値 (意味があるか別として)
```

Rust はジェネリクスを**追加機能**として設計した。
CCL はジェネリクスを**唯一の方法**として持っている。

---

## 3. トレイト境界の不在 — HGK の弱点か？

### Rust の境界は型安全を保証する

```rust
fn sort<T: Ord>(items: &mut Vec<T>) { ... }
// T が Ord (順序付け可能) でなければコンパイルエラー
```

### CCL には境界がない

```ccl
/dia+{target: ???}
# target は「判定対象」であるべき。だが CCL は強制しない。
# /dia+{target: 42} は文法的に正しいが、意味的に壊れている
```

**これは弱点か？**

答え: **はい、しかし認知操作では許容できる弱点**。

| 観点 | Rust | CCL |
|:-----|:-----|:----|
| 型安全 | コンパイル時に保証 | なし |
| 意味安全 | 型で近似 | **エージェントの判断に依存** |
| 不正入力 | コンパイルエラー | 意味のない結果 → /dia で検出 |

認知操作に「型チェック」を入れると:

- 「このトピックは /noe+ に適しているか？」→ 事前に判定不可能
- 思考の入力に「正しい型」はない。全てが潜在的に有意義

→ **CCL の型なしジェネリクスは、認知の本質的な開放性を反映している**。

### しかし、Hermēneus は部分的に境界を検証できる

```python
# dispatch() が一部の制約をチェックする例:
def dispatch(ccl_expression):
    for wf in parse(ccl_expression):
        if wf.name == "dia" and not wf.params.get("target"):
            raise CCLError("/dia は target パラメータを必要とします")
```

Hermēneus = 「型チェッカーの代わり」としての最低限の制約チェック。
全てを型で保証する Rust と、最低限の制約を dispatch で保証する CCL。

---

## 4. Monomorphization と WF 派生

```rust
// Rust: generics → monomorphized (特殊化)
fn process<T>(t: T) → process_i32(42), process_str("hello")
```

```ccl
# CCL: WF → 派生 (特殊化)
/noe       → /noe+ (深化), /noe- (削減), /noe* (拡大)
```

| Rust | CCL |
|:-----|:----|
| ジェネリック関数 | 基底 WF (`/noe`) |
| 型パラメータ T | 派生 (`+/-/*`) |
| Monomorphization | Hermēneus が派生を展開 → 具体的な WF 定義を参照 |
| ゼロコスト | 派生は別ファイルではなく同じ WF 定義の中 (**意味的ゼロコスト**) |

---

## 5. 教訓

> **Rust**: ジェネリクスは「制限された自由」。何でもいいが、トレイト境界で制約する。
>
> **HGK**: CCL は「制限なき自由」。何でもいい。意味は実行時にエージェントが判断する。
>
> **どちらが認知に適しているか**: CCL。
> 思考に「正しい型」はない。あらゆる入力が潜在的に有意義。
> ただし、Hermēneus による最低限の制約チェックは有用。

---

## 6. Kalon テスト

| チェック | 結果 |
|:--------|:-----|
| Rust を知らなくても理解できるか | ✅ 「汎用的な処理」は普遍的 |
| 新しい構文が必要か | ❌ 不要。CCL はデフォルトでジェネリック |
| HGK に既に存在していたか | ✅ WF は型なしジェネリック |
| 消化で何を学んだか | 認知の開放性 = 型なしジェネリクスの必然性 |

---

*Pepsis Rust T2 | Generics — 全ては文脈次第 (2026-02-15)*
