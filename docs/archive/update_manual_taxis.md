# Taxis設計 ドキュメント更新マニュアル

> **目的**: `kernel/taxis_design.md` を正本として、全関連ドキュメントを更新するための作業指示書。

---

## 正本

**参照すべき正規定義**: `kernel/taxis_design.md`

---

## 更新対象ファイル

| # | ファイル | 必須変更 | 優先度 |
|---|----------|----------|--------|
| 1 | `kernel/axiom_hierarchy.md` | Taxis層の追加、数式表の更新 | HIGH |
| 2 | `kernel/SACRED_TRUTH.md` | 構造図の更新、24+24=48の反映 | HIGH |
| 3 | `kernel/doctrine.md` | Phase計画にPhase 4を追加 | HIGH |
| 4 | `README.md` | 構造図、数式表、概要の更新 | HIGH |
| 5 | `kernel/KERNEL_PRACTICE_GUIDE.md` | Taxis早見表の追加 | MEDIUM |
| 6 | `docs/ARCHITECTURE.md` | 詳細仕様の追加 | MEDIUM |
| 7 | `STRUCTURE.md` | 構造図の更新 | LOW |

---

## 更新ルール

### 必須事項

1. **K-seriesの表記を統一**
   - 「Kairos」→「K-series」に変更
   - 順列記法は使用しない（積記法のみ: 4 × 3 = 12）

2. **数式表の形式**
   ```markdown
   | シリーズ | 生成方法 | 積記法 | 数 | 性質 |
   |---------|----------|--------|-----|------|
   | P-series | 核心 × 核心 | 2 × 2 | 4 | 本質的 |
   | M-series | 核心 × 選択 | 2 × 4 | 8 | 様態的 |
   | K-series | 選択 × 選択 | 4 × 3 | 12 | 文脈的 |
   ```

3. **Taxis層の追加**
   ```markdown
   | T-P | 核心 × 核心 従属 | 2 × 2 | 4 | メタ認知的 |
   | T-M | 核心 × 選択 従属 | 2 × 4 | 8 | 機能間 |
   | T-K | 選択 × 選択 従属 | 4 × 3 | 12 | 文脈間 |
   ```

4. **総計の表記**
   - 定理層: 24
   - 関係層: 24
   - 総計: 48

5. **Phase計画**
   ```markdown
   | Phase | 内容 | 状態 |
   |-------|------|------|
   | 1 | M-series (8) | 運用中 |
   | 2 | P-series (4) | 設計中 |
   | 3 | K-series (12) | 計画 |
   | 4 | Taxis (24) | 提案 |
   ```

---

## 各ファイルの具体的変更

### 1. kernel/axiom_hierarchy.md

**変更箇所**:
- 「数学的構造」セクションにTaxis層を追加
- 構造図（ASCII図）を2層構造に更新
- K-seriesの「Kairos」表記を「K-series」に統一

**追加コンテンツ**:
```markdown
## 関係層 (Taxis)

> **定義**: 定理間の従属関係を定義する層

| シリーズ | 生成方法 | 積記法 | 数 | 性質 |
|---------|----------|--------|-----|------|
| **T-P** | 核心 × 核心 従属 | 2 × 2 | **4** | メタ認知的従属 |
| **T-M** | 核心 × 選択 従属 | 2 × 4 | **8** | 機能間従属 |
| **T-K** | 選択 × 選択 従属 | 4 × 3 | **12** | 文脈間従属 |
```

### 2. kernel/SACRED_TRUTH.md

**変更箇所**:
- 構造図に「Level 2'」としてTaxis層を追加
- 「数学的美しさ」セクションに48の説明を追加

### 3. kernel/doctrine.md

**変更箇所**:
- 「12機能体系」→「24定理 + 24関係」に更新
- Phase表にPhase 4を追加

### 4. README.md

**変更箇所**:
- 「数学的構造」セクションにTaxis層を追加
- 構造図を更新

### 5. kernel/KERNEL_PRACTICE_GUIDE.md

**追加コンテンツ**:
```markdown
## Taxis 日常適用早見表

| 状況 | 適用Taxis | 意味 |
|------|-----------|------|
| なぜこれをするのか | T-P | 行動の理由（メタ目的） |
| どの順序で | T-K | 文脈間の依存関係 |
```

---

## チェックリスト

### 更新前

- [ ] `kernel/taxis_design.md` を読み、構造を理解した
- [ ] 変更対象ファイルをバックアップした

### 更新中（各ファイルごと）

- [ ] K-series表記が「Kairos」から「K-series」に変更された
- [ ] 数式表が統一形式になっている
- [ ] Taxis層が追加されている
- [ ] 総計が「24 + 24 = 48」になっている

### 更新後

- [ ] 全ファイルで表記が一貫している
- [ ] 相互リンクが正しく機能する
- [ ] git commit完了

---

## 実行コマンド（参考）

```powershell
# 変更をコミット
git add kernel/ README.md docs/ STRUCTURE.md
git commit -m "refactor(kernel): add Taxis layer (24 relations), unify P/M/K notation"
```

---

*このマニュアルは `kernel/taxis_design.md` を正本として作成された。*
