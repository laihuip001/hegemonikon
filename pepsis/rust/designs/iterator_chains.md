# Iterator — 遅延する知の連鎖

> **CCL**: `/gno+{source=rust.iterator}`
> **消化タイプ**: T2 (再発見)
> **Date**: 2026-02-15
> **Kalon テスト**: ✅

---

## 1. Rust の Iterator とは何か

```rust
let numbers = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

let result: Vec<i32> = numbers.iter()
    .filter(|&&x| x % 2 == 0)    // 偶数だけ
    .map(|&x| x * 3)              // 3倍にする
    .take(3)                       // 最初の3つだけ
    .collect();                    // [6, 12, 18]
```

**2 つの核心**:

1. **チェーン (Composability)**: 小さな操作を連結して複雑な処理を作る
2. **遅延評価 (Laziness)**: `.collect()` が呼ばれるまで何も計算しない

---

## 2. CCL のイテレータ: F:[] + _ + I:[]

### 2.1 チェーン = `_` (シーケンス)

```rust
// Rust: filter → map → take → collect
numbers.iter().filter(...).map(...).take(3).collect()
```

```ccl
# CCL: WF1 → WF2 → WF3 → 集約
/noe+{source} _ /dia-{filter} _ /ene+{transform} _ /pis{collect}
```

| Rust Iterator | CCL | 意味 |
|:-------------|:----|:-----|
| `.filter(predicate)` | `_ I:[cond]{WF}` | 条件に合うものだけ通す |
| `.map(transform)` | `_ /wf` | 各要素を変換する |
| `.take(n)` | `F:[×n]{WF}` | 最初の n 個だけ |
| `.collect()` | `_ /pis` or `_ /dox-` | 結果を集約・記録 |
| `.fold(init, f)` | `R:{} F:[]{WF}` | 累積処理 |
| `.zip(other)` | `*` (結合) | 二つの系列を組み合わせ |
| `.enumerate()` | `F:[×n]{WF _ /dox-{step: N}}` | 番号付き反復 |
| `.chain(other)` | `_` (単純連結) | 二つの系列を連続 |

### 2.2 CCL マクロの Iterator パターン

```ccl
# /ccl-chew (噛む) の構造:
/s- _ /pro _ F:[×3]{/eat+~(/noe*/dia)} _ ~(/h*/k) _ @proof _ /pis _ /dox-
#                ^^^^^^^^^^^^^^^^^^^^^^^^^^^
#                これは Iterator パターンそのもの:
#                F:[×3]  = .take(3)
#                /eat+   = .map() (各要素を消化)
#                ~()     = .filter() 的な収束チェック
```

**既に使っている**: CCL マクロは Iterator パターンで書かれている。

---

## 3. 遅延評価 — CCL にないもの

### Rust の遅延評価

```rust
// この行では何も計算されない
let lazy = (0..1_000_000).filter(|x| x % 2 == 0).map(|x| x * 3);
// collect() で初めて計算が走る
let result: Vec<i32> = lazy.take(3).collect();
// → 全 100万件を処理せずに、必要な 3件だけ計算
```

**なぜ重要か**: 不要な計算を避ける。効率。

### CCL には遅延評価がない — そして、それでいい

CCL は**即時評価**。`/noe+ _ /dia+` と書いたら:

1. まず `/noe+` が完全に実行される
2. 次に `/dia+` が完全に実行される

遅延はない。だが認知操作に遅延評価は必要か？

**必要ない理由**:

1. **認知は副作用**: 思考は「する」ことに意味がある。遅延して「しない」のは思考ではない
2. **CCL チェーンは短い**: 3-10 ステップ。100万回のループではない。効率の問題がない
3. **既存の「遅延」メカニズム**: `/rom` (後で読む) や `/bye` (セッション切り替え) が「後で考える」を実現

**しかし、Rust が教えてくれた「遅延」の本質**:

> 遅延とは「必要になるまでやらない」。

HGK では:

| 遅延の形 | CCL 表現 | 意味 |
|:--------|:---------|:-----|
| 計算の遅延 | なし (CCL は即時) | — |
| 判断の遅延 | `/dia epochē` | 今は判断しない |
| 実行の遅延 | `/rom` → 後のセッション | 後で実行する |
| 消化の遅延 | `/eat` の `incoming/` | 消化キューに入れて後で処理 |

→ **CCL は「計算」は即時だが、「判断」と「実行」は遅延できる**。
これは認知に適した設計。

---

## 4. Iterator Protocol — pull vs push

```rust
// Rust Iterator = pull (消費者が引く)
trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
    // 消費者が .next() を呼ぶ。生産者は待つ。
}
```

CCL は **push モデル** (生産者が押す):

```ccl
/noe+ _ /dia+
# /noe+ が結果を「押す」→ /dia+ がそれを受け取る
# /dia+ が「次をくれ」と引くのではない
```

| モデル | Rust | CCL | 意味 |
|:------|:-----|:----|:-----|
| Pull | Iterator `.next()` | — | 消費者が制御 |
| Push | — | `_` (シーケンス) | 生産者が制御 |

**どちらが認知に適しているか**: Push。
思考は「次を考えろ」と自分に命令するのではなく、
前の思考の結果が自然に次の思考を引き起こす。

→ FEP の active inference: 予測が行動を生む = push。

---

## 5. 教訓のまとめ

| Rust が教えたこと | HGK が教え返すこと |
|:---------------|:-----------------|
| チェーン合成の力 | CCL の `_` は既にチェーン |
| 遅延 = 必要になるまでやらない | 認知の「遅延」は判断停止として存在 |
| Pull vs Push | 認知は Push。FEP と整合 |
| Iterator の組み合わせ可能性 | CCL マクロの組み合わせ可能性 |

---

## 6. Kalon テスト

| チェック | 結果 |
|:--------|:-----|
| Rust を知らなくても理解できるか | ✅ 「ステップを連結する」は普遍的 |
| 新しい構文が必要か | ❌ 不要。F:[] + _ + I:[] |
| HGK に既に存在していたか | ✅ CCL マクロは既に Iterator パターン |
| 消化で何を学んだか | CCL は push モデル (FEP 整合)、遅延は判断停止で実現 |

---

*Pepsis Rust T2 | Iterator — 遅延する知の連鎖 (2026-02-15)*
