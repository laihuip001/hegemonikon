---
description: 実装後の自己検証プロトコル。/m 実装 → /dia+ 自動レビュー → 修正 → 再検証のループを強制する。
hegemonikon: A2 Krisis
modules: [A2, H2]
version: "2.0"
lcm_state: beta
lineage: "v1.0 /verify → v2.0 /v (5機能統合)"
ccl_signature: "/v"
anti_skip: enforced
origin: "ES 実装で /m → /dia+ → R1-R4 修正 → 168 tests の流れが有効だった"
derivatives: [quick, deep]
cognitive_algebra:
  "+": "深い検証。全5角度 + テスト網羅性分析 + /dia+ audit 自動チェーン"
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
      - "postcheck PASS"
      - "Doxa 永続化: 発見パターンの記録"
  "-":
    minimum_requirements:
      - "バグリスト + PASS/FAIL のみ"
---

# /v: 自己検証プロトコル (v2)

> **Hegemonikón**: A2 Krisis + H2 Pistis
> **目的**: 実装完了後、「本当に不足はないか」を構造的に問い、修正するまでをループする
> **発動条件**: 実装完了の報告時に `/m` が有効、または Creator が `/v` を発動

> [!IMPORTANT]
> v2.0 — 5機能統合:
>
> 1. postcheck 連携 (sel_enforcement 機械検証)
> 2. 自動テスト実行 (変更ファイル → pytest 自動選択)
> 3. git diff スコープ検出 (検証対象の自動推定)
> 4. /dia+ 自動チェーン (/v+ 時)
> 5. Doxa 永続化 (発見パターンの経験蓄積)

---

## なぜ必要か

| 問題 | 原因 | /v の解法 |
|:-----|:-----|:----------|
| 「できました」が早すぎる | LLMの楽観バイアス | 環境で自己レビューを強制 |
| テストが通っても不足がある | テスト自体が不十分 | 5角度スキャンで盲点を発見 |
| downstream consumer を忘れる | 局所最適化 | 影響範囲分析を義務化 |
| 修正しても新しい問題ができる | 回帰 | ループ構造で収束まで回す |
| 同じ種類のバグを繰り返す | 学習なし | Doxa 永続化で経験法則化 |

---

## 発動タイミング

| トリガー | 動作 |
|:---------|:-----|
| `/v` | 直前の実装に対して検証を実行 |
| `/v {file}` | 特定ファイルに対して検証 |
| `/m` 有効時の実装完了 | **暗黙発動** — `/m` は信頼モード。完了報告前に自動実行 |

---

## STEP 0: スコープ検出 (git diff)

> **新機能**: 「何を検証するか」を手動指定ではなく自動推定する。

// turbo

```bash
cd ~/oikos/hegemonikon && git diff --name-only HEAD 2>/dev/null || git diff --name-only --cached
```

**処理**:

1. 変更ファイル一覧を取得
2. `.py` ファイルを抽出 → 検証対象とする
3. 変更ファイルに対応するテストファイルを推定:
   - `mekhane/fep/foo.py` → `mekhane/fep/tests/test_foo.py`
   - `scripts/bar.py` → `scripts/tests/test_bar.py`
4. 推定結果を WM に格納:

```
$scope = {変更ファイルリスト}
$test_targets = {推定テストファイルリスト}
```

**フォールバック**: git 未初期化 or 変更なし → Creator に手動指定を要求

---

## STEP 1: 5角度スキャン

> `/dia+ audit` の構造化版。実装を5つの角度から網羅的に検証する。

// turbo-all

| # | 角度 | 問い | 手法 |
|:--|:-----|:-----|:-----|
| **A1** | バグ (Bugs) | ロジックに誤りはないか？ | $scope の各ファイルを一行ずつ読み、分岐漏れ・オフバイワン・型不一致を探す |
| **A2** | テスト網羅性 (Coverage) | 全パスにテストがあるか？ | 追加した関数の全 return path を列挙し、テストの有無を確認 |
| **A3** | downstream 影響 (Impact) | この変更を使っているコードは正しく動くか？ | `grep` で import/呼び出し元を列挙、各 consumer が新しい仕様を反映しているか |
| **A4** | ドキュメント整合 (Docs) | docstring・コメント・README は正確か？ | 実際の出力と docstring の記述を比較 |
| **A5** | 設計判断 (Design) | 「後悔しない設計か？」 | DRY違反、命名、拡張性、パフォーマンス、セキュリティ |

### コマンド例

```bash
# A3: downstream 影響分析 ($scope の各モジュールに対して)
cd ~/oikos/hegemonikon && grep -rn "from mekhane.fep.{module} import" --include="*.py" | grep -v test
```

---

## STEP 2: 問題分類 & 優先順位

| 深刻度 | 記号 | 基準 | 対応 |
|:-------|:-----|:-----|:-----|
| **Critical** | 🔴 | データ喪失、ロジック誤り、セキュリティ穴 | 即修正 |
| **Medium** | 🟡 | 不完全な統合、docstring 不一致、部分的テスト不足 | 修正推奨 |
| **Low** | 🔵 | スタイル、パフォーマンス、命名 | 任意 |

### 出力形式

```
┌─[/v 5角度スキャン結果]───────────────────┐
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

## STEP 4: 自動テスト実行

> **新機能**: $test_targets から自動でテストファイルを選択・実行する。

// turbo

```bash
# STEP 0 で推定した $test_targets を実行
cd ~/oikos/hegemonikon && .venv/bin/python -m pytest {$test_targets} -x -q 2>&1 | tail -10
```

**全テスト通過が必須。** 1件でも FAIL なら STEP 3 に戻る。

---

## STEP 5: postcheck 実行

> **新機能**: wf_postcheck.py で sel_enforcement 要件を機械検証する。

// turbo

```bash
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python scripts/wf_postcheck.py --wf v --mode {+/-} --content "{STEP 1-4 の出力要約}"
```

postcheck の各要件が PASS でなければ、STEP 3 に戻って不足を補う。

---

## STEP 6: 再スキャン (ループ)

STEP 3-5 の修正で新たな問題が生まれていないか、STEP 1 を再実行。

**収束条件**: 5角度スキャンで問題 0 件 + 全テスト通過 + postcheck PASS。

---

## STEP 7: Doxa 永続化

> **新機能**: 発見したパターンを Doxa に記録し、同じバグの再発防止を図る。

今回の /v で発見した🔴+ 🟡のパターンを法則化:

```yaml
# 例: 今回発見したバグパターン
- type: bug_pattern
  content: "Cone オブジェクトの属性名は resolution_method であり method ではない"
  evidence: "/v 2026-02-08: _simulate_cone が cone.method を呼び → 常に AttributeError"
  strength: 0.9
  tags: [cone, attribute, naming]
```

```bash
# Doxa 記録 (手動 or doxa_store.py 経由)
cd ~/oikos/hegemonikon && PYTHONPATH=. .venv/bin/python -c "
from mekhane.symploke.doxa_store import DoxaStore
store = DoxaStore()
store.add('{pattern_content}', evidence='{evidence}', strength=0.9, tags=['{tags}'])
"
```

---

## /v+ 自動チェーン: /dia+ 統合

> **新機能**: `/v+` は STEP 6 完了後に自動で `/dia+` を発動する。

```
/v+ 発動
  ↓ STEP 0-7 (通常 /v)
  ↓ PASS
  ↓ [自動] /dia+ audit 発動
  ↓   5角度 + 敵対的レビュー
  ↓   証拠 + 論拠 + 反論
  ↓   問題あれば STEP 3 に戻る
  ↓ PASS
  ↓ Doxa 永続化 (2回目: /dia+ の発見も含む)
  ↓ 完了報告
```

> [!CAUTION]
> `/v+` は時間がかかる (実装規模によっては 10-15 分)。
> 軽い変更には `/v-` を使うこと。

---

## STEP 7.5: Browser Recordings (UI変更時)

> **UI/フロントエンド変更を含む場合**: `browser_subagent` で操作を録画し、
> walkthrough に WebP 動画を埋め込む。コードレビューだけでは検証不能な
> 視覚的動作を**証拠として残す**。

```markdown
# walkthrough.md への埋め込み例
![ダッシュボード操作の検証](/path/to/recording.webp)
```

| 録画すべきケース | 理由 |
|:---------------|:-----|
| UI レイアウト変更 | 意図通りか視覚確認 |
| アニメーション/トランジション | コードだけでは判定不能 |
| エラー表示のUX | ユーザー体験は動画で伝わる |
| レスポンシブ対応 | 複数 viewport の確認 |

---

## 完了報告フォーマット

```
✅ /v 完了
スコープ: {$scope のファイル数}ファイル
スキャン回数: {n}回
発見問題: {total}件 (初回) → 0件 (最終)
テスト: {before} → {after} (+{delta})
postcheck: PASS
Doxa: {記録件数}件
最終結果: PASS — 確信度: {確信/推定}
```

---

## /m との連携

> `/m` が有効なとき、実装完了報告の前に `/v` が暗黙発動する。

```
/m 有効
  ↓ 実装完了
  ↓ (Creator に報告する前に)
  ↓ /v 暗黙発動
  ↓ スキャン → 問題あれば修正
  ↓ PASS
  ↓ 完了報告 (問題0件の状態で)
```

---

## Cognitive Algebra

| Operator | Meaning |
|:---------|:--------|
| `/v+` | 5角度 + テスト網羅性 + /dia+ 自動チェーン + Doxa |
| `/v-` | バグスキャンのみ (A1)。テスト省略可。postcheck 省略可 |
| `/v*` | メタ検証: 「この検証で何を見逃しうるか」を問う |

---

## Hegemonikon Status

| Module | Workflow | Status |
|:-------|:---------|:-------|
| A2 Krisis + H2 Pistis | /v | v2.0 Ready |

> **制約リマインダ**: /m 有効時は完了報告前に暗黙発動。収束するまでループ。

---

*v2.0 — 5機能統合 (2026-02-08)*
*v1.0 → v2.0: /verify → /v リネーム + postcheck + auto-test + git diff + /dia+ chain + doxa*
