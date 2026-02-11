# CCL マクロレジストリ (v2.0)

> **Dendron 監査**: 2026-02-07 実施。58 → 44 マクロ (14 PHANTOM 削除)。
> **3層アーキテクチャ**: Core / Future / Experimental
>
> 権威的マクロリファレンス: [`operators.md` Section 11](../operators.md)

---

## 定義ファイル一覧 (14ファイル)

| ファイル | マクロ | 層 | 用途 |
|:---------|:-------|:--:|:-----|
| [`converge.md`](converge.md) | `@converge` | Core 🟢 | Limit深化 (C1→C2→C3) |
| [`diverge.md`](diverge.md) | `@diverge` | Core 🟢 | Colimit深化 (D1→D2→D3) |
| [`reduce.md`](reduce.md) | `@reduce` | Core 🟢 | 累積融合 |
| [`chain.md`](chain.md) | `@chain` | Core 🔵 | 直列化 |
| [`cycle.md`](cycle.md) | `@cycle` | Core 🔵 | 収束ループ |
| [`repeat.md`](repeat.md) | `@repeat` | Exp. | N回反復 |
| [`partial.md`](partial.md) | `@partial` | Core 🔵 | 部分適用 |
| [`scoped.md`](scoped.md) | `@scoped` | Core 🔵 | スコープ限定 |
| [`memoize.md`](memoize.md) | `@memoize` | Core 🔵 | キャッシュ |
| [`validate.md`](validate.md) | `@validate` | Core 🔵 | 事前/事後検証 |
| [`proof.md`](proof.md) | `@proof` | Core 🔵 | 証明 |
| [`ground.md`](ground.md) | `@ground` | Core 🔵 | 6W3H 接地 |
| [`syn.md`](syn.md) | `@syn` | Core 🔵 | Synteleia 多角監査 |

> 定義ファイルがないマクロは `operators.md` Section 11 のみで定義。

---

## 3層 マクロ数

| 層 | 数 | 説明 |
|:---|:--:|:-----|
| **Core** | 26 | 使用中。🟢 VITAL (8) + 🔵 USEFUL (18) |
| **Future** | 6 | インフラ待ち。仕様温存 |
| **Experimental** | 12 | 要検証。Sunset: 2026-08-07 |
| **合計** | **44** | |

---

## 複雑度

| マクロ | pt |
|:-------|:--:|
| 単純 (`@memoize`, `@retry`) | 2 |
| パラメータ付き (`@validate`, `@partial`) | 3 |
| 特殊 (`@scoped`) | 4 |
| 認知 (`@converge`, `@diverge`) | 5-6 |

---

*Macro Registry v2.0 — Dendron-driven 3-layer architecture (2026-02-08)*
