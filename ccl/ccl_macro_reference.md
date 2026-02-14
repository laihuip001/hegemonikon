# CCL マクロリファレンス

> **バージョン**: v4.1 (2026-02-14)
> **設計原則**: CCL 演算子で書けるものは演算子に。制御構文のみ略記号。
> **正本**: `.agent/workflows/ccl-*.md` が各マクロの正規定義

---

## クイックリファレンス

> **核**: そのマクロ固有の認知操作（ボイラープレート除外）
> **完全式**: WF定義の CCL 式（正本）

| マクロ | 俗名 | 核 | 完全式 |
|:-------|:-----|:---|:-------|
| `@dig` | 掘る | `/s+~(/p*/a)_/ana_/dia*/o+` | `/pro_/s+~(/p*/a)_/ana_/dia*/o+_/pis_/dox-` |
| `@plan` | 段取る | `/chr_/s+~(/p*/k)_V:{/dia}` | `/bou+_/chr_/s+~(/p*/k)_V:{/dia}_/pis_/dox-` |
| `@build` | 組む | `/s+_/ene+_V:{/dia-}` | `/bou-_/s+_/ene+_V:{/dia-}_I:[✓]{/dox-}` |
| `@fix` | 直す | `C:{/dia+_/ene+}` | `/kho_/tel_C:{/dia+_/ene+}_I:[✓]{/pis_/dox-}` |
| `@vet` | 確かめる | `C:{V:{/dia+}_/ene+}_/pra{test}` | `/kho{git_diff}_C:{V:{/dia+}_/ene+}_/pra{test}_/pra{dendron_guard}_/pis_/dox` |
| `@tak` | 捌く | `F:[×3]{/sta~/chr}_F:[×3]{/kho~/zet}` | `/s1_F:[×3]{/sta~/chr}_F:[×3]{/kho~/zet}_I:[∅]{/sop}_/euk_/bou` |
| `@kyc` | 回す | `C:{/sop_/noe_/ene_/dia-}` | `/pro_C:{/sop_/noe_/ene_/dia-}_/pis_/dox-` |
| `@learn` | 刻む | `/dox+_F:[×2]{/u+~(/noe*/dia)}` | `/pro_/dox+_F:[×2]{/u+~(/noe*/dia)}_~(/h*/k)_/pis_/bye+` |
| `@nous` | 問う | `R:{F:[×2]{/u+*^/u^}}` | `/pro_/s-_R:{F:[×2]{/u+*^/u^}}_~(/noe*/dia)_/pis_/dox-` |
| `@proof` | 裁く | `V:{/noe~/dia}` | `V:{/noe~/dia}_I:[✓]{/ene{PROOF.md}}_E:{/ene{_limbo/}}` |
| `@syn` | 監る | `/dia+{synteleia}` | `/kho_/s-_/pro_/dia+{synteleia}_~(/noe*/dia)_V:{/pis+}_/dox-` |
| `@ready` | 見渡す | `/kho_/chr_/euk_/tak-` | `/bou-_/pro_/kho_/chr_/euk_/tak-_~(/h*/k)_/pis_/dox-` |
| `@chew` | 噛む | `F:[×3]{/eat+~(/noe*/dia)}` | `/s-_/pro_F:[×3]{/eat+~(/noe*/dia)}_~(/h*/k)_@proof_/pis_/dox-` |
| `@read` | 読む | `F:[×3]{/m.read~(/noe*/dia)}` | `/s-_/pro_F:[×3]{/m.read~(/noe*/dia)}_/ore_~(/h*/k)_/pis_/dox-` |
| `@helm` | 舵 | `/bou+*%/zet+\|>/u++` | `/pro_/kho_/bou+*%/zet+\|>/u++_~(/h*/k)_/pis_/dox-` |

---

## 構文体系

### CCL 演算子（ネイティブ）

| 演算子 | 意味 |
|:-------|:-----|
| `_` | チェーン（直列化） |
| `~` | 振動（行き来） |
| `*` | 融合 |
| `*^` | メタ融合 |
| `*%` | 融合外積 |
| `+` | 深化 |
| `-` | 簡略化 |
| `{params}` | パラメータ |
| `(group)` | グループ |
| `\|>` | パイプライン |

### 制御構文（CPL）

| 構文 | 意味 | Python 対応 |
|:-----|:-----|:-----------|
| `F:[×N]{X}` | N回反復 | `for _ in range(N)` |
| `F:[a,b]{X}` | 各要素に適用 | `for x in [a,b]` |
| `I:[cond]{X}` | 条件分岐 | `if cond:` |
| `E:{X}` | その他 | `else:` |
| `L:[x]{X}` | Lambda | `lambda x: X` |

### 記号構文（CPL デコレータ圧縮）

| 記号 | 意味 | 元の名称 |
|:-----|:-----|:---------|
| `C:{X}` | 収束ループ | @cycle |
| `R:{X}` | 累積融合 | @reduce |
| `V:{X}` | 検証ゲート | @validate |

---

## MECE 分類

### 軸1: Flow × Value

```
                E (認識的)          P (実用的)
             ┌──────────────┬──────────────┐
 I (推論)    │ @dig @nous   │ @plan @tak   │
             │ @read @helm  │ @ready       │
             ├──────────────┼──────────────┤
 A (行為)    │ @vet @learn  │ @fix @build  │
             │ @proof @syn  │              │
             └──────────────┴──────────────┘
```

### 軸2: 認知骨格パターン

| パターン | マクロ |
|:---------|:-------|
| Prior → Likelihood → Posterior | @dig, @plan, @fix, @kyc, @learn, @nous, @syn, @helm, @ready |
| 反復深化 (F:[×N]) | @chew, @read, @tak |
| 収束ループ (C:/R:) | @kyc, @fix |
| 検証ゲート (V:) | @vet, @proof, @build |

### 軸3: 双対構造

| 対 | 共有構造 | 違い |
|:---|:---------|:-----|
| @chew ↔ @read | `F:[×3]{X~(/noe*/dia)}` | X = `/eat+` vs `/m.read` |
| @dig ↔ @plan | S-series 関与 | 分析(掘る) vs 設計(段取る) |

---

## アーカイブ

| マクロ | 理由 |
|:-------|:-----|
| `@go` | エイリアス (`/s+_/ene+`) |
| `@wake` | `/boot` で代替 |
| `@v` | → `@vet` にリネーム |
| `@scan` | FuseOuter 1演算。直接 `/s*%/dia` と書ける |
| `@weigh` | FuseOuter 1演算。直接 `/bou*%/noe` と書ける |
| `@osc` | 多視点自動深化。使用実績ゼロでアーカイブ |
| `@feel` | `/ore~(/pis_/ana)`。Hub-only 統合だが使用実績不足 |
| `@clean` | `/kat_/sym~(/tel_/dia-)`。同上 |
| `@ground` | 抽象→具体変換。設計系WFへの組み込みを検討中 |

---

*v4.1 — /dia++ レビューで 21→15 に間引き (2026-02-14)*
