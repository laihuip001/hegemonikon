# CCL マクロレジストリ (v3.3)

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

### Forge 由来マクロ (v2.0 — 演算子フル活用)

| ファイル | マクロ | CCL | 特徴的演算子 |
|:---------|:-------|:----|:-------------|
| [`dump.md`](dump.md) | `@dump` | `/zet! \|> R:{/s+} \|> /bou-` | `!`, `R:{}`, `-` |
| [`scan.md`](scan.md) | `@scan` | `/met+ \|> /kho \|> /noe' \|> /s+` | `'` (微分) |
| [`invert.md`](invert.md) | `@invert` | `/noe+ >* /dia! _ /zet` | `>*` (射的融合) |
| [`devil.md`](devil.md) | `@devil` | `/dia+ \|> /noe! \|> /pis{out:pass\|fail}` | 型記法 |
| [`sys.md`](sys.md) | `@sys` | `/met _ /noe+*/sta \|> /mek+ _ /pra _ /tek` | `*` (融合) |
| [`poc.md`](poc.md) | `@poc` | `/zet- \|> /ene _ V:{/dia-{out:pass\|fail}}` | `-`, `V:{}`, 型 |
| [`proc.md`](proc.md) | `@proc` | `/sta+ \|> /pra \|> /mek _ /dox-` | `\|>` チェイン |
| [`review.md`](review.md) | `@review` | `/dia+^ _ /pis _ I:[...]{C:{...}} E:{...}` | `^`, `C:{}` |
| [`retro.md`](retro.md) | `@retro` | `/epo+ _ /pro~*/noe _ /dox _ M:{/bye}` | `~*` (収束振動) |

> ユーザーマクロ(12) は `.agent/workflows/ccl-*.md` で定義。
> 演算子カバレッジ: **17/30+** (v1.0: 8 → v2.0: 17, +112%)

---

## v3.3 変更履歴

- v2.0 演算子フル活用リファクタ: `>*`, `~*`, `^`, `!`, `R:{}`, `C:{}`, `'`, 型記法
- v1.1 改善: @scan (バイアス検出), @poc (縮約), @retro (感情), @sys (暗黙知)

---

*Macro Registry v3.3 — Operator full utilization (2026-02-11)*
