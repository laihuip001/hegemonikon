# Rust 消化 STATUS

> **Phase**: 1 完了 → Phase 2 設計中
> **Updated**: 2026-02-15
> **Status**: Phase 1 完了、Phase 2 方向修正

---

## 完了タスク

### Phase 1: T1 + T2 ✅

- [x] **core_mapping.md** (T1): Rust ↔ HGK 対応表 (17概念)
- [x] **philosophy_extraction.md** (T2): 所有権モデルから 9 認知原則を導出

## Phase 2: 既存 CCL の意味拡張

> **Kalon 基準**: 元の文脈を知らなくても使える状態 = naturalization
> **反省**: `@owned`/`@borrow`/`@move` は Rust の語彙の丸呑み。Kalon ではない。

### 正しい方向

所有権モデルの本質は**既存の CCL 演算子に内在**している:

| CCL 演算子 | Rust 対応 | 意味の拡張 |
|:-----------|:----------|:----------|
| `>>` | move | 所有権の移動。不可逆的遷移 |
| `*` | borrow | 借用。互いを消費しない合成 |
| `+` | `&mut` | 変更可能な参照（一度に一つ） |
| `-` | `&` | 読み取り参照（複数可） |

→ **新マクロ不要**。既存演算子の設計根拠が Rust のアナロジーで豊かになる。

### Phase 2 タスク

- [ ] **operator_semantics.md**: CCL 演算子の意味拡張ドキュメント（所有権視点）
- [ ] **error_handling.md**: `Result<T,E>` パターン → CCL のエラーハンドリング（HGK に不足する概念）
- [ ] **exhaustive_check.md**: 網羅的マッチ → `/dia+` の網羅性検証強化

### Phase 3: T4 (概念輸入 — 要慎重)

- [ ] **affine_cognition.md**: 線形型 → 認知リソースの一回使用モデル（kernel 拡張）

---

### 🔑 教訓

> **消化 ≠ 丸呑み**。外部の名前でマクロを作ることは消化ではない。
> 既存の構造がすでに表現していることを「再発見」することが真の消化。
