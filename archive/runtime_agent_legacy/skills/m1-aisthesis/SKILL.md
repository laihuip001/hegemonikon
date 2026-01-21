---
name: "M1 Aisthēsis"
description: |
  FEP Octave M1: 知覚モジュール (I-E-F)。状況・文脈を即時認識し、意味を推論する。
  Use when: 新規メッセージ受信時、文脈が不明確な時、「これは何？」質問時、セッション開始時。
  Use when NOT: 既に状況把握済みで行動決定フェーズに入っている時。
  Triggers: M2 Krisis (状況認識→優先度判断へ連携)
  Keywords: perception, context, situation, first-analysis, input-parsing, what-is-this.
---

# M1: Aisthēsis (αἴσθησις) — 知覚

> **FEP Code:** I-E-F (Inference × Epistemic × Fast)
> **Hegemonikón:** 09 Aisthēsis-H

---

## Core Function

**役割:** 今何が起きているかを認識する

| 項目 | 内容 |
|------|------|
| **FEP役割** | 観測 o の取得、状態 s の推論 |
| **本質** | 環境からの信号を構造化し、意味を付与する |

---

## Precondition

| 条件 | 内容 |
|------|------|
| **位置** | 全処理の入口。常に最初に実行される |
| **依存** | なし（他モジュールに依存しない） |

---

## Input / Output

### Input

| 種別 | 形式 | ソース | 備考 |
|------|------|--------|------|
| ユーザー発話 | テキスト | セッション | 必須 |
| チャット履歴 | Markdown | Vault | 設定可能な日数 |
| ファイル/コード | 任意 | ワークスペース | 開いているファイル |
| IDE状態 | JSON | Antigravity | カーソル位置、選択範囲 |
| 時刻・日付 | ISO 8601 | システム | 自動取得 |

### Output

| 種別 | 形式 | 送信先 | 備考 |
|------|------|--------|------|
| 状況ラベル | Enum | M2 Krisis | 5値分類 |
| 文脈サマリ | テキスト | M2, M5, M3 | 500文字以内 |
| 検出エンティティ | JSON | M2 | 信頼度付き |
| 不確実性スコア | Float (0-1) | M5 Peira | 計算式あり |
| 観測履歴 | JSON | M3 Theōria | 因果モデル構築用 |

---

## Trigger

| トリガー | 条件 | 優先度 |
|----------|------|--------|
| セッション開始 | 常に | 最高 |
| 新規入力 | ユーザー発話検出 | 高 |
| ファイル変更 | ワークスペース変更 | 中 |
| IDE状態変更 | アクティブファイル変更 | 低 |

---

## Processing Logic

```
Phase 1: 入力収集
  1. ユーザー発話を取得
  2. 関連履歴をスキャン（デフォルト: 7日、設定可能）
  3. 現在のコンテキストを取得
  4. IDE状態を取得（開いているファイル、カーソル位置）

Phase 2: 構造化
  5. 時間的文脈を特定（→ 時間帯判定参照）
  6. 進行中タスクを抽出（→ エンティティ検出パターン参照）
  7. エンティティを検出（タスク、人物、日付、プロジェクト）

Phase 3: 意味推論
  8. 状況ラベルを分類（→ 状況分類基準参照）
  9. 不確実性スコアを算出（→ 不確実性計算参照）

Phase 4: 出力
  10. 構造化出力を生成
  11. M2 Krisis, M5 Peira, M3 Theōria へ送信
```

---

## Situation Classification Criteria

| ラベル | 判定条件 | 例 |
|--------|----------|-----|
| **urgent** | 明示的な緊急キーワード OR 期限 < 24h | 「今すぐ」「急ぎで」「今日中に」 |
| **decision_required** | 選択肢の提示 OR 質問形式 | 「AとBどちらが」「〜すべき？」 |
| **information_gathering** | 調査・検索キーワード | 「調べて」「教えて」「〜とは」 |
| **reflection** | 振り返りキーワード | 「レビュー」「まとめ」「振り返り」 |
| **routine** | 上記いずれにも該当しない | 通常の作業依頼 |

**判定優先順位:** urgent > decision_required > information_gathering > reflection > routine

---

## Entity Detection Patterns

| エンティティ種別 | 検出パターン | 信頼度調整 |
|------------------|--------------|------------|
| **Task** | 動詞 + 目的語、「〜する」「〜して」 | 明示的: 0.9, 暗示的: 0.6 |
| **Date** | 日付表現、「明日」「来週」「N日後」 | 具体的: 0.95, 相対的: 0.8 |
| **Person** | 固有名詞、「〜さん」、代名詞 | 明示的: 0.9, 代名詞: 0.5 |
| **Project** | プロジェクト名、リポジトリ名 | 完全一致: 0.95, 部分一致: 0.7 |
| **Commitment** | 「やる」「する」「約束」 | 一人称: 0.9, 三人称: 0.5 |

---

## Uncertainty Calculation

```yaml
# 不確実性スコア U の計算
U = w1 * info_gap + w2 * ambiguity + w3 * contradiction

weights:
  w1: 0.4  # 情報欠如度
  w2: 0.35 # 曖昧性度
  w3: 0.25 # 矛盾検出度

info_gap:
  formula: 1 - (detected_entities / expected_entities)
  description: 必要な情報がどれだけ欠けているか

# expected_entities: コンテキスト別期待エンティティ数
expected_entities_table:
  routine: 2        # タスク + 対象
  urgent: 3         # タスク + 対象 + 期限
  decision_required: 4  # タスク + 選択肢A + 選択肢B + 基準
  information_gathering: 2  # トピック + スコープ
  reflection: 3     # 対象 + 期間 + 視点

ambiguity:
  triggers:
    - 「〜とか」「〜など」「何か」「いい感じ」
    - 主語の省略
    - 目的の不明確さ
  formula: ambiguous_tokens / total_tokens

contradiction:
  triggers:
    - 履歴との矛盾
    - 自己矛盾する記述
  formula: contradicting_statements / total_statements

threshold:
  low: U < 0.3      # M5 Peira不要
  medium: 0.3 <= U < 0.6  # M5 Peira推奨
  high: U >= 0.6    # M5 Peira必須
```

---

## Edge Cases

| ケース | 検出条件 | フォールバック動作 |
|--------|----------|-------------------|
| **空入力** | ユーザー発話が空 or null | IDE状態のみで文脈推論、situation_label = "routine" |
| **履歴なし** | Vaultが空 or アクセス不可 | 現在入力のみで処理、history_context = null |
| **IDE状態なし** | Antigravity外での実行 | ファイル情報なしで処理続行 |
| **全入力欠如** | 発話・履歴・IDEすべてなし | エラー返却、M2に進まない |

---

## Test Cases

| ID | 入力 | 期待される状況ラベル | 期待される不確実性 |
|----|------|---------------------|-------------------|
| T1 | 「今すぐこのバグを直して」 | urgent | low (< 0.3) |
| T2 | 「AとBどちらがいい？」 | decision_required | medium (0.3-0.6) |
| T3 | 「何かいい感じにして」 | routine | high (>= 0.6) |
| T4 | 「昨日の作業を振り返って」 | reflection | low (< 0.3) |
| T5 | 「」(空) | routine (fallback) | N/A |
| T6 | 「Xについて調べて」 | information_gathering | low (< 0.3) |

---

## Temporal Context

| 時間帯 | 判定基準 | 備考 |
|--------|----------|------|
| **朝** | 05:00 - 11:59 | morning |
| **昼** | 12:00 - 17:59 | afternoon |
| **夜** | 18:00 - 04:59 | evening |

| 曜日 | 判定 |
|------|------|
| **平日** | 月-金 |
| **週末** | 土-日 |

---

## Failure Modes

| 失敗 | 症状 | 検出方法 | 回復策 |
|------|------|----------|--------|
| 文脈誤認 | 無関係なタスクを抽出 | M2からの否定フィードバック | 履歴スキャン範囲を狭める |
| 過検出 | 大量のエンティティ | entity_count > 20 | confidence閾値を0.7以上に |
| 見落とし | 重要コミットメント未検出 | ユーザー指摘 | キーワードリスト拡張 |
| 不確実性過小評価 | M5が起動すべき時に起動せず | 後続エラー率 | 閾値を下げる (0.5 → 0.4) |

---

## Integration

| 依存 | 対象 | 関係 |
|------|------|------|
| **Precondition** | なし | 入口モジュール |
| **Postcondition** | M2 Krisis | 状況認識結果を渡す |
| **Postcondition** | M5 Peira | 不確実性が高い場合に起動 |
| **Postcondition** | M3 Theōria | 観測履歴を渡す |

---

## Configuration

| パラメータ | デフォルト | 説明 |
|------------|-----------|------|
| `history_scan_days` | 7 | 履歴スキャン日数 |
| `entity_confidence_threshold` | 0.5 | エンティティ検出閾値 |
| `uncertainty_threshold` | 0.6 | M5起動閾値 |
| `max_context_summary_length` | 500 | 文脈サマリ最大文字数 |
