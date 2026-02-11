# CCL マクロレジストリ (v3.1)

> **3層アーキテクチャ**: User / System / Primitive
> **正本**: `ccl/operators.md` Section 11
> **ユーザーマクロ定義**: `.agent/workflows/ccl-*.md`
> **リファレンス**: `docs/ccl_macro_reference.md`

---

## 定義ファイル一覧 (2ファイル)

| ファイル | マクロ | 用途 |
|:---------|:-------|:-----|
| [`converge.md`](converge.md) | `@converge` | Hub WF Limit 深化 (C1→C2→C3) |
| [`diverge.md`](diverge.md) | `@diverge` | Hub WF Colimit 深化 (D1→D2→D3) |

> ユーザーマクロ(12) は `.agent/workflows/ccl-*.md` で定義。
> その他のマクロは `operators.md` §11 で定義。

---

## v3.1 変更履歴

- 13 ファイル削除 (chain, cycle, reduce, partial, scoped, memoize, validate, repeat, proof, ground, syn, polar, switch)
- `@cycle` → `C:{}`, `@reduce` → `R:{}`, `@memoize` → `M:{}`, `@validate` → `V:{}`  (§9.7)
- `@chain`, `@partial`, `@scoped`, `@repeat` → CCL 既存構文で代替 (§11.6)

---

*Macro Registry v3.1 — 3-layer architecture (2026-02-11)*
