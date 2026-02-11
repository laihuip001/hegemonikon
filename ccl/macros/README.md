# CCL マクロレジストリ (v3.2)

> **3層アーキテクチャ**: User / System / Primitive
> **正本**: `ccl/operators.md` Section 11
> **ユーザーマクロ定義**: `.agent/workflows/ccl-*.md`
> **リファレンス**: `ccl/ccl_macro_reference.md`

---

## 定義ファイル一覧

### System マクロ (Hub WF 統合)

| ファイル | マクロ | 用途 |
|:---------|:-------|:-----|
| [`converge.md`](converge.md) | `@converge` | Hub WF Limit 深化 (C1→C2→C3) |
| [`diverge.md`](diverge.md) | `@diverge` | Hub WF Colimit 深化 (D1→D2→D3) |

### Forge 由来マクロ (v1.0)

| ファイル | マクロ | CCL | Forge Origin |
|:---------|:-------|:----|:-------------|
| [`dump.md`](dump.md) | `@dump` | `/zet+ \|> /s+ \|> /bou` | 🤯 Brain Dump |
| [`scan.md`](scan.md) | `@scan` | `/met+ _ /kho _ /s+` | 🔍 What is? + 🗺️ Overview |
| [`invert.md`](invert.md) | `@invert` | `/noe+ _ /dia! _ /zet` | 🙃 Invert |
| [`devil.md`](devil.md) | `@devil` | `/dia+ \|> /noe! \|> /pis` | 🛡️ Devil's Advocate |
| [`sys.md`](sys.md) | `@sys` | `/met _ /mek+ _ /pra _ /tek` | 🏗️ Systemize |
| [`poc.md`](poc.md) | `@poc` | `/zet _ /ene+ _ V:{/dia-}` | 🧪 Prototype |
| [`proc.md`](proc.md) | `@proc` | `/sta+ _ /pra _ /mek` | 📐 Procedure |
| [`review.md`](review.md) | `@review` | `/dia+ _ /pis _ I:[V[]>0.3]{..}` | ✨ Quality? + 🔧 Improve |
| [`retro.md`](retro.md) | `@retro` | `/epo+ _ /dox _ M:{/bye}` | 📖 Retrospect + 💾 Archive |

> ユーザーマクロ(12) は `.agent/workflows/ccl-*.md` で定義。
> その他のマクロは `operators.md` §11 で定義。

---

## v3.2 変更履歴

- Forge v2.0 由来 9マクロ新設 (dump, scan, invert, devil, sys, poc, proc, review, retro)
- v3.1: 13 ファイル削除 (chain, cycle 等 → §9.7 CPL 構文に統合)

---

*Macro Registry v3.2 — Forge integration (2026-02-11)*
