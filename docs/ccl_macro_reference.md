# CCL マクロリファレンス

> **バージョン**: v3.0 (2026-02-11)
> **目的**: 認知の再利用性 — 複雑な CCL パターンを短い名前で呼び出す
> **設計原則**: CPL v2.0 構文をフル活用。最低 2 種の制御構文を使用。

---

## クイックリファレンス

| マクロ | 一言説明 | CCL 定義 | CPL 構文 |
|:-------|:---------|:---------|:---------|
| `@dig` | 深掘り | `/s+~(/p*/a)_/dia*/o+` | ~, *, _ |
| `@plan` | 計画策定 | `/bou+_/s+~(/p*/k)_@validate{/dia}` | @validate |
| `@build` | 構築 | `@partial{/bou-, goal:define}_/s+_@scoped{/ene+}_@validate{/dia-}_I:[pass]{@memoize{/dox-}}` | @partial, @scoped, @validate, I:, @memoize |
| `@fix` | 修正サイクル | `@cycle{/dia+_/ene+}_I:[pass]{@memoize{/dox-}}` | @cycle, I:, @memoize |
| `@v` | 自己検証 | `@scoped{/kho{git_diff}}_@cycle{@validate{/dia+}_/ene+}_/pra{test}_@memoize{/pis_/dox}` | @scoped, @cycle, @validate, @memoize |
| `@tak` | タスク整理 | `/s1_F:[×3]{/sta~/chr}_F:[×3]{/kho~/zet}_I:[gap]{/sop}_/euk_/bou` | F:, I:, ~ |
| `@kyc` | 認知循環 | `@cycle{/sop_/noe_/ene_/dia-}` | @cycle |
| `@learn` | 学習永続化 | `/dox+_*^/u+_@memoize{/bye+}` | @memoize |
| `@nous` | 問いの深化 | `@reduce{F:[×2]{/u+*^/u^}}_@memoize{/dox-}` | @reduce, F:, @memoize |
| `@ground` | 具体化 | `@scoped{/tak-}*@partial{/bou+, mode:6w3h}~/p-_/ene-` | @scoped, @partial, ~ |
| `@osc` | 多角振動 | `@reduce{F:[/s,/dia,/noe]{L:[x]{x~x+}}, ~(/h*/k)}` | @reduce, F:[], L:[], ~ |
| `@proof` | 存在証明 | `@validate{/noe{axiom:FEP}~/dia}_I:[confidence=1]{/ene{output:PROOF.md}}_E:{/ene{action:move, to:_limbo/}}` | @validate, I:, E: |

---

## MECE 分類（複数軸）

### 軸1: Flow × Value (I/A × E/P)

```
              E (認識的)          P (実用的)
           ┌──────────────┬──────────────┐
I (推論)   │  @dig @nous  │ @plan @tak   │
           │  @osc        │ @ground      │
           ├──────────────┼──────────────┤
A (行為)   │  @v @learn   │ @fix @build  │
           │  @proof      │              │
           └──────────────┴──────────────┘
```

### 軸2: 時間

| 前方 (計画) | 現在 (実行) | 後方 (振返) |
|:-----------|:-----------|:-----------|
| @plan, @tak, @ground | @build, @fix, @dig, @osc | @v, @learn, @proof |
| | @kyc (全フェーズ横断) | @nous (全フェーズ横断) |

### 軸3: FEP 予測誤差処理

| 検出 | 修正 | 防止 |
|:-----|:-----|:-----|
| @dig, @v, @osc | @fix, @build | @plan, @tak |
| @nous | @ground | @learn, @proof |

---

## CPL 構文カバレッジ

| 構文 | 使用マクロ |
|:-----|:----------|
| ~~`@chain`~~ | CCL 演算子 `_` で代替 → 除去 |
| `@cycle` | @fix, @kyc, @v |
| `@reduce` | @osc, @nous |
| `@partial` | @build, @ground |
| `@scoped` | @build, @ground, @v |
| `@memoize` | @fix, @nous, @learn, @v, @build |
| `@validate` | @plan, @proof, @v, @build |
| `L:[x]{}` | @osc |
| `F:[×N]{}` | @tak, @nous |
| `F:[A,B]{}` | @osc |
| `I:/E:` | @fix, @proof, @build |

**11/14 構文をカバー** (未使用: W:[], @retry (Sunset), @async (将来))

---

## マクロ演算子

マクロは通常のワークフローと同様に演算子を適用できる。

| 演算子 | 意味 | 例 |
|:-------|:-----|:---|
| `@macro+` | 全WFを詳細化 | `@dig+` → 各構成要素が + に |
| `@macro^` | メタ分析 | `@plan^` → 計画自体を問う |
| `@macro~/wf` | 振動 | `@tak~/s` → 分類↔戦略 |
| `@macro*/wf` | 融合 | `@tak*/ene` → 分類結果を即実行 |
| `@macro _ /wf` | チェイン | `@tak _ /ene` → 分類後に実行 |

---

## アーカイブ済みマクロ

| マクロ | 旧 CCL 定義 | 理由 |
|:-------|:-----------|:-----|
| `@go` | `/s+_/ene+` | エイリアス — 直接書ける |
| `@wake` | `/boot+_@dig_@plan` | `/boot` で代替 |

---

## ユーザー定義マクロ

`let` 構文で新しいマクロを定義・永続化できる:

```ccl
let @morning = /boot+_@dig_@plan_@build
```

**永続化先**: `~/.hegemonikon/ccl_macros.json`

---

## 関連ファイル

| ファイル | 内容 |
|:---------|:-----|
| `.agent/macros/REGISTRY.md` | マクロ演算子ルール |
| `mekhane/ccl/macro_registry.py` | Python 実装 |
| KI `cognitive_algebra_system` | 設計思想・詳細仕様 |

---

*v3.0 — CPL v2.0 フル活用リファクタ (2026-02-11)*
*変更履歴: v2.5 (2026-01-30) → v3.0: @build 新設, @go/@wake アーカイブ, @tak/@v 復活, 全マクロ CPL 進化, MECE 分類追加*
