# Dendron Architecture v3.6 — Matrix Structure

> 設計ドキュメント

## 概要

Dendron は **2軸マトリクス構造** を持つ存在証明システム。
DB正規化理論 (NF1→BCNF) をコードの存在証明に転用し、漸進的に制約を強化する。

## マトリクス構造

### 軸1: Depth Layer (走査の深さ)

| Layer | 対象 | 検証方法 | 状態 |
|:------|:-----|:---------|:-----|
| **L0** | ディレクトリ | PROOF.md の存在 | ✅ 実装済み |
| **L1** | ファイル | PROOF ヘッダー | ✅ 実装済み |
| **L2** | 関数・クラス | `# PURPOSE:` コメント | ✅ v2.6 実装済み |
| **L3** | 変数・字句 | 型ヒント + 命名品質 | ✅ v3.0 実装済み |

### 軸2: Meta Layer (検証の種類 = 正規形)

| Meta Layer | DB正規形 | 説明 | 検証対象 | 状態 |
|:-----------|:---------|:-----|:---------|:-----|
| **表層 (Surface)** | NF1 | 存在宣言の有無 | PROOF/PURPOSE ヘッダー | ✅ 実装済み |
| **構造層 (Structure)** | NF2 | 依存関係の明示性・妥当性 | import/呼出/型参照/親参照 | ✅ v3.1 実装済み |
| **機能層 (Function)** | NF3 | 機能的冗長性 (MECE) | SRP/類似度/再代入/親子重複 | ✅ v3.2 実装済み |
| **実証層 (Verification)** | BCNF | 不可欠性 (削除耐性) | 被import/dead func/unused var | ✅ v3.3 実装済み |

> **注意**: NF2-BCNF はデフォルト OFF (`--structure`, `--function-nf`, `--verification` で有効化)。
> CI では全層有効化を推奨。

## 完全マトリクス

```
                    表層      構造層        機能層        実証層
                  Surface   Structure     Function    Verification
              ┌─────────┬───────────┬───────────┬─────────────┐
    L0 (Dir)  │ ✅       │ ✅ P01     │ ✅ 親子重複 │ ✅ トートロジー │
              ├─────────┼───────────┼───────────┼─────────────┤
    L1 (File) │ ✅       │ ✅ P11     │ — (未実装)  │ ✅ P13       │
              ├─────────┼───────────┼───────────┼─────────────┤
    L2 (Func) │ ✅ v2.6  │ ✅ P21/P31 │ ✅ P22/P12  │ ✅ P23       │
              ├─────────┼───────────┼───────────┼─────────────┤
    L3 (Var)  │ ✅ v3.0  │ —          │ ✅ P32      │ ✅ P33       │
              └─────────┴───────────┴───────────┴─────────────┘
```

**現在のカバレッジ: 14/16 セル (87.5%)**

未実装セル:

- L1×NF3 (ファイルレベルの機能重複検出)
- L3×NF2 (変数レベルの依存検証)

### Structure (NF2) 検証一覧

| ID | 対象 | 検証内容 | メソッド |
|:---|:-----|:---------|:---------|
| P01 | L0 Dir | PROOF.md 内の親参照が実在するか | `check_dir_structure` |
| P11 | L1 File | import 先のモジュールが存在するか | `_check_imports_from_tree` |
| P21 | L2 Func | 関数内の呼出先が解決可能か | `_check_calls_from_tree` |
| P31 | L2 Func | 型アノテーションが import されているか | `_check_type_refs_from_tree` |

### Function (NF3) 検証一覧

| ID | 対象 | 検証内容 | メソッド |
|:---|:-----|:---------|:---------|
| P12 | L2 Func | 同ファイル内の類似関数検出 (Jaccard ≥ 80%) | `_check_similarity_from_tree` |
| P22 | L2 Func | SRP 違反 (行数/分岐/引数の閾値超過) | `_check_complexity_from_tree` |
| P32 | L3 Var | 変数の過剰再代入 (動的閾値) | `_check_reassignment_from_tree` |
| R02 | L0 Dir | 親子 REASON 重複 (Jaccard ≥ 60%) | `_aggregate_results` |
| R12 | L1 File | ファイル←→親Dir REASON 重複 | `_aggregate_results` |
| R22 | L2 Func | 関数←→ファイル REASON 重複 | `_aggregate_results` |

### Verification (BCNF) 検証一覧

| ID | 対象 | 検証内容 | メソッド |
|:---|:-----|:---------|:---------|
| P13 | L1 File | ファイルが他ファイルから import されているか | `_check_verification_global` |
| P23 | L2 Func | Dead function 検出 | `_check_verification_global` |
| P33 | L3 Var | Unused variable 検出 | `_check_verification_global` |
| R03 | L0 Dir | REASON ≈ PURPOSE トートロジー検出 | `check_dir_proof` |
| R23 | L2 Func | REASON ≈ PURPOSE トートロジー検出 | `_check_functions_from_tree` |

## L2 Surface 実装詳細 (v2.6)

| 機能 | 説明 | 状態 |
|:-----|:-----|:-----|
| PURPOSE 検出 | `# PURPOSE:` コメントの有無チェック | ✅ |
| 品質検証 | WEAK パターン検出 (WHAT vs WHY) | ✅ |
| CLI サブコマンド | `dendron purpose [PATH] --ci --strict` | ✅ |
| CI 統合 | dendron.yml に L2 ステップ追加 | ✅ |
| 段階的展開 | dendron/ strict + mekhane/ warn | ✅ |

## FEP 対応

| Depth | FEP 層 | 意味 |
|:------|:-------|:-----|
| L0 | Kairos (K) | 文脈・配置 |
| L1 | Ousia/Schema (O/S) | 本質・様態 |
| L2 | Hormē/Perigraphē (H/P) | 動機・境界 |
| L3 | Akribeia (A) | 精密・検証 |

## 抽象化（任意リポジトリ対応）

```
Hegemonikón 固有          →  抽象化 (汎用)
─────────────────────────────────────────
L0: PROOF.md              →  README.md / PURPOSE.md
L1: PROOF ヘッダー        →  ファイル docstring
L2: # PURPOSE: コメント   →  関数・メソッド説明
L3: 命名規則              →  変数・型ヒント
```

## ロードマップ

### Phase 1: 表層完成 ✅

- [x] L0 ディレクトリ PROOF.md
- [x] L1 ファイル PROOF ヘッダー
- [x] L2 関数 `# PURPOSE:` コメント (v2.6)
- [x] L3 型ヒストカバレッジ + 命名品質 (v3.0)

### Phase 2: 構造層 ✅

- [x] import 先の存在検証 (P11)
- [x] 関数呼出の解決可能性 (P21)
- [x] 型参照の import 照合 (P31)
- [x] PROOF.md 親参照の存在検証 (P01)

### Phase 3: 機能層 ✅

- [x] SRP 複雑度 — 行数/分岐/引数 (P22)
- [x] 関数類似度 — AST 構造ベース Jaccard (P12)
- [x] 変数再代入 — 動的閾値 (P32)
- [x] 親子 REASON 重複 — テキスト Jaccard (R02/R12/R22)
- [ ] ファイルレベル重複検出 (L1×NF3 — 未実装)

### Phase 4: 実証層 ✅

- [x] 被 import カウント — ファイル不可欠性 (P13)
- [x] Dead function 検出 (P23)
- [x] Unused variable 検出 (P33)
- [x] トートロジー検出 — REASON ≈ PURPOSE (R03/R23)

### Phase 5: 次世代 (計画中)

- [ ] L1×NF3 ファイルレベル機能重複
- [ ] L3×NF2 変数レベル依存検証
- [ ] NF2-BCNF のデフォルト有効化
- [ ] 外部リポジトリ対応 (汎用化)
- [ ] GitHub Actions との完全統合

---

*Origin: 2026-02-01_conv_12_Dendron Project Creation.md*
*Updated: 2026-02-14 (v3.6: NF2/NF3/BCNF 実装状態を反映、全検証ID一覧追加)*
