---
description: 実装後の自己検証プロトコル。/m 実装 → /dia+ 自動レビュー → 修正 → 再検証のループを強制する。
hegemonikon: A2 Krisis
modules: [A2, H2]
version: "1.0"
lcm_state: beta
lineage: "2026-02-08 Explanation Stack 実装時の経験から形式化"
ccl_signature: "/verify"
anti_skip: enforced
origin: "ES 実装で /m → /dia+ → R1-R4 修正 → 168 tests の流れが有効だった"
derivatives: [quick, deep]
cognitive_algebra:
  "+": "深い検証。全5角度 + テスト網羅性分析"
  "-": "軽い検証。バグのみ。テスト省略"
  "*": "メタ検証。検証プロセス自体の妥当性を問う"
sel_enforcement:
  "+":
    minimum_requirements:
      - "5角度スキャン完全実行"
      - "バグリスト: 深刻度付き"
      - "テスト網羅性: 未テストパス列挙"
      - "downstream 影響分析"
      - "修正+テスト追加+全テスト通過"
  "-":
    minimum_requirements:
      - "バグリスト + PASS/FAIL のみ"
---

# /verify: 自己検証プロトコル

> **Hegemonikón**: A2 Krisis + H2 Pistis
> **目的**: 実装完了後、「本当に不足はないか」を構造的に問い、修正するまでをループする
> **発動条件**: 実装完了の報告時に `/m` が有効、または Creator が `/verify` を発動

> [!IMPORTANT]
> このプロトコルは、2026-02-08 の Explanation Stack 実装で
> 「速すぎないか？」(Creator) → `/dia+` → B1-B3 + T1-T2 発見 → 修正
> → 「本当に不足はない？」 → R1-R4 発見 → 修正 → 168 tests
> という経験を形式化したもの。

---

## なぜ必要か

| 問題 | 原因 | /verify の解法 |
|:-----|:-----|:---------------|
| 「できました」が早すぎる | LLMの楽観バイアス | 環境で自己レビューを強制 |
| テストが通っても不足がある | テスト自体が不十分 | 5角度スキャンで盲点を発見 |
| downstream consumer を忘れる | 局所最適化 | 影響範囲分析を義務化 |
| 修正しても新しい問題ができる | 回帰 | ループ構造で収束まで回す |

---

## 発動タイミング

| トリガー | 動作 |
|:---------|:-----|
| `/verify` | 直前の実装に対して検証を実行 |
| `/verify {file}` | 特定ファイルに対して検証 |
| `/m` 有効時の実装完了 | **暗黙発動** — `/m` は信頼モード。完了報告前に自動実行 |

---

## 処理フロー

```
実装完了
  ↓
[STEP 1] 5角度スキャン
  ↓
[STEP 2] 問題分類 & 優先順位
  ↓
[STEP 3] 修正
  ↓
[STEP 4] テスト追加 + 全テスト実行
  ↓
[STEP 5] 再スキャン (問題 0 になるまでループ)
  ↓
完了報告
```

---

## STEP 1: 5角度スキャン

> `/dia+ audit` の構造化版。実装を5つの角度から網羅的に検証する。

// turbo-all

| # | 角度 | 問い | 手法 |
|:--|:-----|:-----|:-----|
| **A1** | バグ (Bugs) | ロジックに誤りはないか？ | コードを一行ずつ読み、分岐漏れ・オフバイワン・型不一致を探す |
| **A2** | テスト網羅性 (Coverage) | 全パスにテストがあるか？ | 追加した関数の全 return path を列挙し、テストの有無を確認 |
| **A3** | downstream 影響 (Impact) | この変更を使っているコードは正しく動くか？ | `grep` で import/呼び出し元を列挙、各 consumer が新しい仕様を反映しているか |
| **A4** | ドキュメント整合 (Docs) | docstring・コメント・README は正確か？ | 実際の出力と docstring の記述を比較 |
| **A5** | 設計判断 (Design) | 「後悔しない設計か？」 | DRY違反、命名、拡張性、パフォーマンス、セキュリティ |

### 実行コマンド

各角度について、以下のパターンで確認:

```bash
# A3: downstream 影響分析
cd ~/oikos/hegemonikon && grep -rn "from mekhane.fep.cone_consumer import" --include="*.py" | grep -v test
```

```bash
# A2: テスト実行
cd ~/oikos/hegemonikon && .venv/bin/python -m pytest {test_file} -x -q 2>&1 | tail -5
```

---

## STEP 2: 問題分類

| 深刻度 | 記号 | 基準 | 対応 |
|:-------|:-----|:-----|:-----|
| **Critical** | 🔴 | データ喪失、ロジック誤り、セキュリティ穴 | 即修正 |
| **Medium** | 🟡 | 不完全な統合、docstring 不一致、部分的テスト不足 | 修正推奨 |
| **Low** | 🔵 | スタイル、パフォーマンス、命名 | 任意 |

### 出力形式

```
┌─[/verify 5角度スキャン結果]──────────────┐
│ A1 Bugs:     {n}件 (🔴{x} 🟡{y} 🔵{z})
│ A2 Coverage: {未テストパス数}
│ A3 Impact:   {未統合 consumer 数}
│ A4 Docs:     {不整合数}
│ A5 Design:   {懸念数}
│ 
│ 合計: {total} 件
│ 推奨: {全修正 / 🔴のみ / PASS}
└──────────────────────────────────────────┘
```

---

## STEP 3: 修正

- 問題を優先順位順に修正
- 各修正に対してテストを追加 (A2 で不足が判明した場合)

---

## STEP 4: テスト実行

// turbo

```bash
cd ~/oikos/hegemonikon && .venv/bin/python -m pytest {test_file} -x -q 2>&1 | tail -5
```

**全テスト通過が必須。** 1件でも FAIL なら STEP 3 に戻る。

---

## STEP 5: 再スキャン

STEP 3-4 の修正で新たな問題が生まれていないか、STEP 1 を再実行。

**収束条件**: 5角度スキャンで問題 0 件、かつ全テスト通過。

---

## 完了報告フォーマット

```
✅ /verify 完了
スキャン回数: {n}回
発見問題: {total}件 (初回) → 0件 (最終)
テスト: {before} → {after} (+{delta})
最終結果: PASS — 確信度: {確信/推定}
```

---

## /m との連携

> `/m` が有効なとき、実装完了報告の前に `/verify` が暗黙発動する。

```
/m 有効
  ↓ 実装完了
  ↓ (Creator に報告する前に)
  ↓ /verify 暗黙発動
  ↓ スキャン → 問題あれば修正
  ↓ PASS
  ↓ 完了報告 (問題0件の状態で)
```

---

## Cognitive Algebra

| Operator | Meaning |
|:---------|:--------|
| `/verify+` | 5角度 + テスト網羅性分析 + downstream 全件チェック |
| `/verify-` | バグスキャンのみ (A1)。テスト省略可 |
| `/verify*` | メタ検証: 「この検証で何を見逃しうるか」を問う |

---

## Hegemonikon Status

| Module | Workflow | Status |
|:-------|:---------|:-------|
| A2 Krisis + H2 Pistis | /verify | v1.0 Ready |

> **制約リマインダ**: /m 有効時は完了報告前に暗黙発動。収束するまでループ。

---

*v1.0 — ES 実装経験から形式化 (2026-02-08)*
