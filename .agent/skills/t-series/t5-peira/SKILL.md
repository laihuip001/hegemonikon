---
name: "T5 Peira"
description: |
  FEP Octave T5: 探求モジュール (A-E-F)。情報不足を検出し、収集行動を発動する。
  Use when: 情報収集、Web検索、「調べて」要求、不確実性が高い時(U>0.6)。
  Use when NOT: 既知情報で回答可能な時、実行フェーズで追加調査不要な時。
  Triggers: T3 Theōria (情報収集→仮説構築へ) or T6 Praxis (情報収集→即時行動へ)
  Keywords: search, research, query, information gathering, uncertainty, fact-check.
---

# T5: Peira (πεῖρα) — 探求

> **FEP Code:** A-E-F (Action × Epistemic × Fast)
> **Hegemonikón:** 11 Peira-H

---

## Core Function

**役割:** 情報不足を検出し、収集行動を発動する

| 項目 | 内容 |
|------|------|
| **FEP役割** | Epistemic価値 E[H[P(o|s)]] の追求 |
| **本質** | 「わからないこと」を解消する |

---

## Precondition

| 条件 | 内容 |
|------|------|
| **位置** | T1/T2/T6 から呼び出されるオンデマンド実行 |
| **依存** | 外部検索ツール (Web Search/API) |
| **コスト** | 高コスト操作（時間・API）のため、乱発禁止 |

---

## Input / Output

### Input

| 種別 | 形式 | ソース | 備考 |
|------|------|--------|------|
| 不確実性スコア | Float | T1 Aisthēsis | **> 0.2 で発動検討** |
| 情報ギャップ | JSON | T2 Krisis | 具体的な欠損情報 |
| 明示的質問 | テキスト | ユーザー | 「調べて」 |
| 仮説検証要求 | JSON | T7 Dokimē | 裏付け調査 |

### Output

| 種別 | 形式 | 送信先 | 備考 |
|------|------|--------|------|
| 検索クエリ | String[] | Web Search | 実行されるクエリ |
| 調査レポート | Markdown | ユーザー | 構造化された回答 |
| 新事実 | JSON | T3 Theōria | モデル更新用 |
| 文脈更新 | JSON | T1 Aisthēsis | 変数埋め |

---

## Trigger

| トリガー | 条件 | 優先度 |
|----------|------|--------|
| 明示的情報要求 | ユーザーが検索を指示 | 最高 |
| **クリティカル情報不足** | **U > 0.4** → 強制発動 | 高 |
| 仮説検証 | T7からの裏付け要求 | 中 |
| **補足情報収集** | **U > 0.2** → 発動検討 | 低 |

### 強制発動条件（1:3 ピラミッド）

> **代表例**: 外部統合
> - MCP実装 → stdout汚染でハング (2026-01-24)
> - REST API → 認証フローの誤解
> - SDK更新 → 破壊的変更の見落とし

> **代表例**: 未知技術
> - 新フレームワーク → ベストプラクティス不明
> - 新言語機能 → 挙動の誤解
> - 新プロトコル → 仕様の読み違い

> **代表例**: デバッグ
> - エラー原因が推測 → 根本原因の見落とし
> - 再現手順が不明 → 環境差異の無視
> - 修正後も再発 → 本質的誤解

---

## Processing Logic

```
Phase 1: 検索戦略策定 (Search Strategy)
  1. 入力から「知りたいこと（User Intent）」を抽出
  2. 検索タイプを決定（→ Search Strategy Matrix参照）
  3. 検索クエリを生成（最低3パターン）

Phase 2: 情報収集実行 (Local First)
  4. **[Gnōsis]** ローカルKBを検索
     - ヒットかつ十分 → 終了
  5. **[Web/Perplexity]** 外部検索を実行
     - 不足があれば実行
  6. 内容の関連性と信頼性を評価

Phase 3: 情報統合・合成
  7. 複数の検索結果から回答を合成
  8. 矛盾がある場合は両論併記 (Gnōsisを優先)
  9. 出典（URL/Paper ID）を明記

Phase 4: 出力・フィードバック
  10. 調査レポートを生成
  11. T1/T3へ構造化データを送信
```

---

## Search Strategy Matrix

| タイプ | 適用場面 | クエリ特徴 | 検索深度 |
|--------|----------|------------|----------|
| **Fact check** | 事実確認、仕様検索 | 具体的なエラー名、API名 | Quick (1-2 queries) |
| **Exploration** | 概念理解、ベストプラクティス | "How to...", "Best practices..." | Medium (3-5 queries) |
| **Comparison** | 技術選定、A vs B | "A vs B performance", "pros cons" | Deep (5+ queries) |
| **Debugging** | エラー解決 | エラーログそのまま + "solution" | Quick but Iterative |

---

## Query Generation Rules

1.  **ノイズ除去**: "Please", "I want to know" などの自然言語を排除
2.  **専門用語**: 最も一般的な技術用語を使用 ("Rails" not "Ruby framework")
3.  **文脈付与**: 言語やフレームワーク名を必ず含める ("datetime format" → "python datetime format")
4.  **演算子活用**: 必要に応じて `site:`, `"exact match"`, `-exclude` を使用

---

## Edge Cases

| ケース | 検出条件 | フォールバック動作 |
|--------|----------|-------------------|
| **検索結果ゼロ** | ヒット数 0 | クエリを一般化して再検索（"exact"を外す等） |
| **オフライン** | ネットワークエラー | 「検索できませんでした」と即時報告 |
| **情報過多/矛盾** | 信頼度スコアが分散 | 「諸説あり」として両論提示し、一次情報へのリンクを優先 |
| **API制限** | Quota Exceeded | 検索を中止し、ユーザーに手動確認を依頼 |

---

## Test Cases

| ID | 入力 | 戦略 | 期待される挙動 |
|----|------|------|----------------|
| T1 | 「Reactの最新バージョンは？」 | Fact check | 公式doc/release noteを提示 |
| T2 | 「Docker vs Podman」 | Comparison | メリット・デメリットの比較表作成 |
| T3 | エラーログ "System.NullReference..." | Debugging | StackOverflow等の解決策提示 |
| T4 | 曖昧な質問「あれってどうやるの？」 | Exploration | T1履歴から文脈補完してクエリ生成 |
| T5 | 検索結果なし | Retry | クエリを短くして再試行 |

---

## Failure Modes

| 失敗 | 症状 | 検出方法 | 回復策 |
|------|------|----------|--------|
| ハルシネーション | 検索結果にない情報を捏造 | 出典URLチェック | 出典がない記述を削除 |
| 情報の陳腐化 | 古い記事を参照 | 日付フィルタ | "after:2024" 等の演算子追加 |
| 文脈ロスト | ユーザーの意図とズレる | ユーザー「違う」 | 意図確認のための逆質問を行う |
| ループ | 同じクエリを繰り返す | 履歴チェック | 過去のクエリを除外リスト登録 |

---

## Integration

| 依存 | 対象 | 関係 |
|------|------|------|
| **Precondition** | T1 Aisthēsis | 文脈・不確実性 |
| **Precondition** | T2 Krisis | 情報ギャップ |
| **Postcondition** | T3 Theōria | 新しい事実・知識 |
| **Postcondition** | ユーザー | レポート提示 |

---

## Configuration

| パラメータ | デフォルト | 説明 |
|------------|-----------|------|
| `max_search_depth` | 3 | 1回の要求に対する最大検索回数 |
| `uncertainty_trigger` | 0.8 | 自動検索を発動する不確実性閾値 |
| `max_results_per_query` | 5 | 1クエリあたりの取得件数 |
| `citation_required` | true | 回答に出典必須とするか |

---

## 外部AI連携

T5 Peiraは複数の情報源を使い分ける。

### 情報源の使い分け

| 情報源 | 用途 | コスト |
|--------|------|--------|
| **search_web** | クイック検索（デフォルト） | 無料 |
| **Perplexity API** (パプ君) | 自律的な下調べ、質問の質向上 | 月$5まで自律使用可 |
| **ユーザー手動リサーチ** | 深い調査が必要な場合 | 無料 |

### Perplexity API 自律使用

> **設計原則**: 私が自律的に使用し、ユーザーへの質問の質を高める。

**発動条件**:
- 情報不足を検出した時 (U > 0.6)
- `/ask` で調査依頼書を作成する前の下調べ
- 背景知識の補強が必要な時

**呼び出し方法**:
```bash
python m:/Hegemonikon/forge/scripts/perplexity_api.py search "クエリ"
```

**使用時の表示**:
```
[Perplexity API] $0.XX used | Budget: $X.XX remaining
```

**やらないこと**:
- ユーザーがリサーチモードで調べた方が良い深い調査
- 無意味な呼び出し

### 連携フロー（更新版）

```
T5 Peira (情報不足検出)
    ↓
search_web で基本情報収集
    ↓
不足がある場合 → Perplexity API で補完
    ↓
ユーザーに深い調査が必要な場合 → /ask で調査依頼書を生成
    ↓
T3 Theōria ← 新情報入力
```

### 対応ワークフロー

| コマンド | 動作 |
|----------|------|
| `/src [クエリ]` | search_web で検索 |
| `/src pp [クエリ]` | Perplexity API で検索 |
| `/ask [質問]` | 調査依頼書を生成（ユーザーがPerplexityにコピペ） |



## Gnōsis Integration (Local First)

> **原則**: 外部検索の前に、検証済みのローカル知識 (Gnōsis) を確認する。

**コマンド**:
```bash
python m:/Hegemonikon/forge/gnosis/cli.py search "query"
```

**Local First フロー**:
1. **内部検索**: Gnōsis KBを検索 (学術・技術論文)
2. **評価**: 十分な情報が得られたか判定
   - Yes → 回答生成へ (Web検索スキップ)
   - No → Web検索へフォールバック

**使い分け**:
- **Gnōsis**: 技術詳細、理論、論文、信頼性が求められる情報
- **Search Web**: 最新ニュース、ドキュメントの最新版、一般的な情報
- **Perplexity**: 複雑な概念の噛み砕き、またはGnōsis/Webで見つからない場合

## Prompt-Lang Integration

T5 Peira は複雑な推論や構造化された出力が必要な場合、`prompt-lang` で定義されたプロンプトを使用する。

**コマンド**:
```bash
python m:/Hegemonikon/forge/prompt-lang/prompt_lang_integrate.py match "query"
```

**使用例**:
- **Research Planning**: `prompt_lang_integrate.py match "research plan"` → `research_planner.prompt` をロード
- **Summarization**: `prompt_lang_integrate.py match "summarize paper"` → `summarizer.prompt` をロード

**SkillAdapter API**:
M-Series スキルからは `prompt_lang_integrate.SkillAdapter` を経由してアクセス可能。
```python
from forge.prompt_lang.prompt_lang_integrate import SkillAdapter
plan_prompt = SkillAdapter.find_prompt("research plan")[0]
```

