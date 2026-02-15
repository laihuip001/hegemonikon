# Mutex / RwLock — 鍵と閲覧室

> **CCL**: `/gno+{source=rust.mutex}`
> **消化タイプ**: T2 (再発見)
> **Date**: 2026-02-15
> **Kalon テスト**: ✅

---

## 1. Rust の Mutex / RwLock とは何か

```rust
// Mutex: 排他的ロック。一人しかアクセスできない。
let mutex = Arc::new(Mutex::new(vec![1, 2, 3]));

let handle = thread::spawn({
    let data = Arc::clone(&mutex);
    move || {
        let mut lock = data.lock().unwrap();  // ロック取得
        lock.push(4);
        // lock が drop → 自動アンロック (RAII)
    }
});
```

```rust
// RwLock: 読み書きロック。読みは並行可、書きは排他。
let rwlock = RwLock::new(42);

// 読み取り: 複数スレッドが同時にOK
let read1 = rwlock.read().unwrap();
let read2 = rwlock.read().unwrap();

// 書き込み: 他の全てのロックを待つ
let mut write = rwlock.write().unwrap();
*write = 100;
```

| 型 | 読み | 書き | 用途 |
|:---|:-----|:-----|:-----|
| `Mutex<T>` | 排他 | 排他 | 常に単一アクセス |
| `RwLock<T>` | **共有** | 排他 | 読みが多い場面 |

---

## 2. parallel_model.md での消化 (既存)

parallel_model.md v1.1 で既に定義:

| Rust | CCL | 意味 |
|:-----|:----|:-----|
| `Mutex<T>` | `+{ctx}` in `\|\|` | 排他的変更。同じ ctx を `+` で並行は不可 |
| `RwLock<T>` read | `-{ctx}` in `\|\|` | 読取共有。同じ ctx を `-` で並行は安全 |
| `RwLock<T>` write | `+{ctx}` | 書き込みは排他。Hermēneus が検出 |

```ccl
# RwLock read — 安全
(/noe-{ctx: report} || /dia-{ctx: report})
# → 両方が report を読むだけ。安全 (Shareable)

# Mutex — Hermēneus が拒否
(/noe+{ctx: report} || /dia+{ctx: report})
# → 両方が report を変更しようとする。dispatch エラー
```

---

## 3. 深い洞察: RAII ロックの美しさ

```rust
{
    let lock = mutex.lock().unwrap();
    // ... lock を使う ...
}  // ← drop → 自動アンロック。忘れることがない。
```

これは RAII (raii_error_propagation.md) そのもの。
「ロック取得」と「ロック解放」がスコープに紐づく。

CCL でも同じ:

```ccl
C:{/noe+{ctx: shared_resource}}
# C:{} スコープ内で shared_resource をロック
# C:{} が閉じたら自動解放 (RAII)
```

**ロック + RAII + スコープ — 3 つの消化概念が同時に動く**。

---

## 4. Deadlock = CCL で起こりうるか？

```rust
// Deadlock の典型パターン
let a = Mutex::new(1);
let b = Mutex::new(2);
// スレッド1: a.lock() → b.lock()
// スレッド2: b.lock() → a.lock()
// → 互いに待ち合って永遠に停止
```

CCL では:

```ccl
# 潜在的 deadlock?
(/noe+{ctx: A} _ /dia+{ctx: B}) || (/dia+{ctx: B} _ /noe+{ctx: A})
# → Hermēneus が安全条件をチェック
# → +{ctx: A} と +{ctx: A} が並行 → dispatch エラー
```

**Hermēneus がデッドロックを防ぐ**: 並行実行で同じ ctx を `+` で変更する
パターンをコンパイル時に検出する。

| 言語 | Deadlock 防止 |
|:-----|:------------|
| Rust | プログラマの責任 (ロック順序の統一等) |
| CCL | **Hermēneus が自動検出** |

→ CCL の方が安全。ただし、Hermēneus のチェック能力は Rust の型システムより弱い
(全ての deadlock パターンを検出できるとは限らない)。

---

## 5. Kalon テスト

| チェック | 結果 |
|:--------|:-----|
| Rust を知らなくても理解できるか | ✅ 「読むのは自由、書くのは一人ずつ」 |
| 新しい構文が必要か | ❌ 不要。+/- と \|\| で表現済み |
| HGK に既に存在していたか | ✅ parallel_model.md v1.1 |
| 消化で何を学んだか | RAII + ロック + スコープの三位一体 |

---

*Pepsis Rust T2 | Mutex/RwLock — 鍵と閲覧室 (2026-02-15)*
