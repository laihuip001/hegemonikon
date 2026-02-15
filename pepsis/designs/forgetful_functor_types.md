# C3: 忘却関手の型理論

> **ステータス**: 設計段階 (2026-02-15)
> **依存**: F7 (ε≠1 知見) + Pepsis Rust 設計

---

## 概要

F7 で判明した「G (忘却関手) は実装詳細を構造的に忘却する」という知見を、
Rust の型システムで形式化する。忘却の**粒度**を型として定義し、
消化プロセスでの情報損失を型レベルで制御する。

---

## 理論的基盤

### ε ≠ 1 の構造的意味

```
G: HGK → Set (忘却関手)
G は以下を忘却する:
  - 実装詳細 (コード構造、API 設計)
  - 設計意図 (なぜその構造を選んだか)
  - 文脈依存情報 (その時の議論の流れ)

G が保存するもの:
  - 概念の骨格 (定義、定理)
  - 構造的関係 (随伴、射)
  - 操作的パターン (使い方の例)
```

### 忘却レベルの階層

```
Forget<Nothing>      ⊂  同型 (完全保存 = 実現不可能)
Forget<Context>      ⊂  文脈を忘却 (議論の流れ)
Forget<Design>       ⊂  設計意図を忘却
Forget<Implementation> ⊂  実装詳細を忘却
Forget<All>          =  全忘却 (消化 = 自明)
```

---

## Rust 型設計案

```rust
use std::marker::PhantomData;

/// 忘却レベルのマーカー型 (ゼロコスト)
pub struct Context;
pub struct Design;  
pub struct Implementation;

/// 忘却関手 G の型パラメータ化
pub struct ForgetfulFunctor<Level> {
    _marker: PhantomData<Level>,
}

/// 忘却されたデータの型
pub struct Forgotten<T, Level> {
    /// 保存された情報
    preserved: T,
    /// 忘却の証拠 (PhantomData)
    _level: PhantomData<Level>,
}

/// 忘却レベル間の射 (サブタイピング)
impl<T> From<Forgotten<T, Context>> for Forgotten<T, Design> {
    fn from(f: Forgotten<T, Context>) -> Self {
        // 文脈忘却 → 設計忘却は常に可能 (忘却は単調)
        Forgotten {
            preserved: f.preserved,
            _level: PhantomData,
        }
    }
}
```

---

## CCL との接続

| CCL 演算子 | 忘却レベル |
|:-----------|:----------|
| `+` (深化) | `Forget<Context>` — 文脈保存、詳細追加 |
| (無印) | `Forget<Design>` — 標準的忘却 |
| `-` (縮約) | `Forget<Implementation>` — 実装まで忘却 |

---

## HGK への統合ポイント

1. **消化品質の型安全性**: η/ε の値だけでなく、忘却レベルが型で保証される
2. **CCL 演算子の意味深化**: `+/-` が忘却レベルを型レベルで切り替える
3. **Pepsis Affine Cognition**: 認知資源の「消費」と忘却の「損失」が型で統一

---

## 実装見積り

| 作業 | 見積り |
|:-----|:-------|
| 型設計の詳細化 | 1h |
| Rust プロトタイプ | 2h |
| CCL パーサーとの接続設計 | 1h |
| **合計** | **4h** |

---

## 反証条件

- 忘却レベルの階層が実際の消化プロセスと一致しない場合
- 型パラメータが実用上の制約にならない場合 (型が多すぎて煩雑)
