# 実装計画: Cognitive Algebra Artifact 継承規則

## 問題概要

`/bou+*zet+` のような Cognitive Algebra 複合式を実行した際、出力がチャットに生成され、artifact に保存されない。

## 根本原因 (/noe+~zet-)

**本質**: Cognitive Algebra 演算子仕様に「出力形式継承規則」が存在しない。

1. **演算子の役割限定**: `+`, `-`, `^`, `/`, `*`, `~` は **認知操作** を定義
2. **artifact 規則の独立性**: 各ワークフロー (`.md`) が独自に「Artifact 自動保存」セクションを持つ
3. **継承の欠如**: 複合実行時に、構成要素の artifact 規則が **継承/集約** されるメカニズムがない

```
/bou+*zet+ の問題:
  /bou → artifact 保存規則あり ✓
  /zet → artifact 保存規則あり ✓
  /bou+*zet+ → 規則継承なし ✗ ← ここが欠落
```

## 設計方針

**原則**: **OR 継承** — 複合式の任意の構成要素が artifact 規則を持てば、複合式も artifact を生成

```
if any(has_artifact_rule(t) for t in theorems_in_expression):
    generate_artifact()
```

## 提案変更

### [MODIFY] [operators_and_layers.md](file:///home/makaron8426/oikos/.gemini/antigravity/knowledge/cognitive_algebra_system/artifacts/architecture/operators_and_layers.md)

新セクション「5. 出力形式継承」を追加:

```markdown
## 5. 出力形式継承

### 5.1 Artifact 継承原則

複合式の場合、**OR 継承**を適用:

| 構成要素の artifact 規則 | 複合式の出力 |
|:-------------------------|:-------------|
| 全部なし | チャット |
| 1つ以上あり | artifact |

### 5.2 artifact ファイル命名

複合式の場合:

```

/mneme/.hegemonikon/workflows/<primary>_<secondary>_<date>.md

```

例: `/bou+*zet+` → `bou_zet_20260129.md`

### 5.3 演算子と artifact の関係

| 演算子 | artifact への影響 |
|:-------|:------------------|
| `+` | 詳細セクションを追加 |
| `-` | サマリーのみ |
| `*` | 融合結果を1ファイルに |
| `~` | 振動ログを時系列で記録 |
```

---

### [MODIFY] [overview.md](file:///home/makaron8426/oikos/.gemini/antigravity/knowledge/cognitive_algebra_system/artifacts/overview.md)

`## 演算子一覧` の後に「Artifact 継承」を追記。

---

## 検証計画

### 自動テスト

現時点でこの仕様は **ドキュメント（人間向け指示）** であり、自動テストは不要。

### 手動検証

1. 修正後、新しいセッションで `/bou+*zet+` を実行
2. `/mneme/.hegemonikon/workflows/` に `bou_zet_YYYYMMDD.md` が生成されることを確認
3. チャット出力が最小化されていることを確認

---

_Hegemonikón A2 Krisis: この計画は妥当か？_
