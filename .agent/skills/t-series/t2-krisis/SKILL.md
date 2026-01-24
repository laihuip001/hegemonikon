---
name: "T2 Krisis"
description: |
  FEP Octave T2: 判断モジュール (I-P-F)。目標との整合性を即時判断し、優先順位を決定する。
  **サブ機能**: モデル選択判断（model-selection-guide.md準拠）
  Use when: 
    - T1完了後、複数タスク存在時、「どれを先に？」質問時、Eisenhower分類が必要な時
    - /plan 開始時（モデル適性チェック）
  Use when NOT: 単一タスクで優先判断不要な時、既に実行フェーズに入っている時。
  Triggers: T4 Phronēsis (優先判断→戦略立案へ) or T6 Praxis (優先判断→即時実行へ)
  Keywords: priority, evaluation, ranking, importance, urgency, which-first, Eisenhower, model-selection.
---

# T2: Krisis (κρίσις) — 判断

> **FEP Code:** I-P-F (Inference × Pragmatic × Fast)
> **Hegemonikón:** 10 Krisis-H

---

## Core Function

**役割:** 目標との整合性を即時判断する

| 項目 | 内容 |
|------|------|
| **FEP役割** | Pragmatic価値 E[ln P(o)] の評価 |
| **本質** | 「今やるべきこと」を選別する |

---

## Precondition

| 条件 | 内容 |
|------|------|
| **位置** | T1 Aisthēsis の直後に実行 |
| **依存** | T1 からの状況認識結果が必須 |

---

## Input / Output

### Input

| 種別 | 形式 | ソース | 備考 |
|------|------|--------|------|
| 状況認識結果 | JSON | T1 Aisthēsis | 必須 |
| ユーザー目標 | テキスト | セッション履歴 | 暗黙的に抽出 |
| 制約条件 | テキスト | GEMINI.md | 自動読み込み |

### Output

| 種別 | 形式 | 送信先 | 備考 |
|------|------|--------|------|
| 優先順位付きタスク | JSON | T6 Praxis | Eisenhower分類付き |
| 緊急フラグ | Boolean | T6 Praxis | 即時対応が必要か |
| 目標乖離度 | Float (0-1) | T8 Anamnēsis | 現状と目標の差分 |
| 情報不足フラグ | JSON | T5 Peira | 追加情報が必要なタスク |

---

## Trigger

| トリガー | 条件 | 優先度 |
|----------|------|--------|
| T1完了 | 状況認識結果受信 | 最高 |
| 目標更新 | goals.yaml 変更 | 高 |
| 手動要求 | `/review` コマンド | 中 |

---

## Processing Logic

```
Phase 1: 入力統合
  1. T1からの状況認識結果を受信
  2. 目標リストを読み込み（存在しない場合はデフォルト）
  3. 制約条件を読み込み（存在しない場合はスキップ）

Phase 2: タスク分類
  4. 検出エンティティをタスク候補として整理
  5. 各タスクに対して:
     a. 明示的コミットメント判定
     b. 完了済み判定
     c. Eisenhower象限分類（→ Eisenhower Matrix参照）

Phase 3: 優先順位付け
  6. 各タスクに対して:
     a. 目標との整合性スコア算出（→ Goal Alignment計算参照）
     b. 緊急度判定（期限ベース）
  7. 時間軸で分類:
     - today / 3days / week / 3weeks / 2months
  8. Q2保護: 重要だが緊急でないタスクの強制浮上

Phase 4: 出力
  9. 優先順位付きリスト生成
  10. 緊急フラグ判定
  11. T6 Praxis, T5 Peira へ送信
```

---

## Goal Alignment Calculation

```yaml
# goal_alignment スコアの計算（キーワードマッチのみ、embedding不使用）
goal_alignment = max(keyword_match(task, goal_i) for goal_i in inferred_goals)

keyword_match:
  formula: matched_keywords / total_keywords
  boost: explicit_mention × 0.2  # 明示的言及でブースト

# 暗黙的目標推論（外部ファイル不要）
inferred_goals:
  source: "セッション履歴から抽出"
  method: |
    1. 直近の会話から「〜したい」「〜が目標」を検出
    2. 進行中プロジェクト名を目標として扱う
    3. 検出できない場合は汎用目標を適用

# 汎用目標（フォールバック）
generic_goals:
  - name: "タスク完了"
    keywords: ["完了", "終わらせる", "やる", "修正", "作成"]
  - name: "情報収集"
    keywords: ["調べる", "調査", "確認", "教えて"]
  - name: "品質向上"
    keywords: ["改善", "レビュー", "最適化", "リファクタ"]
```

---

## Priority Calculation

```yaml
priority_score = (goal_alignment × 0.4) + (urgency × 0.3) + (explicit_commitment × 0.3)

urgency_mapping:
  today: deadline <= now + 24h        # urgency = 1.0
  3days: deadline <= now + 72h        # urgency = 0.8
  week: deadline <= now + 7d          # urgency = 0.6
  3weeks: deadline <= now + 21d       # urgency = 0.4
  2months: deadline <= now + 60d      # urgency = 0.2
  no_deadline: urgency = 0.3          # デフォルト

explicit_commitment:
  explicit: 1.0   # 「やる」「約束した」
  implicit: 0.5   # 暗示的な依頼
  none: 0.0       # コミットメントなし
```

---

## Eisenhower Matrix

| 象限 | 緊急 | 重要 | 処理 |
|------|------|------|------|
| **Q1** | ✅ | ✅ | 即実行 (Do First) |
| **Q2** | ❌ | ✅ | 計画 (Schedule) — **保護対象** |
| **Q3** | ✅ | ❌ | 委任/簡略化 (Delegate) |
| **Q4** | ❌ | ❌ | 削除/延期 (Eliminate) |

### Q2 保護メカニズム

```yaml
# Q2タスクが埋没しないための強制ルール
q2_protection:
  min_q2_ratio: 0.2  # 出力の20%以上はQ2を含める
  q2_boost: 0.15     # Q2タスクの優先度に+0.15ボーナス
  daily_q2_slot: 1   # 毎日最低1つのQ2タスクを提案
```

---

## Edge Cases

| ケース | 検出条件 | フォールバック動作 |
|--------|----------|-------------------|
| **タスクゼロ** | T1から検出タスクが0件 | "特になし" を返却、T6に進まない |
| **目標推論失敗** | 履歴から目標を抽出できない | generic_goals を使用 |
| **全タスクがQ4** | 全て緊急でも重要でもない | 最も goal_alignment が高いものを1つ提案 |
| **期限過ぎ** | deadline < now | urgency = 1.0 (最高) + 警告フラグ |

---

## Test Cases

| ID | 入力 | 期待される出力 |
|----|------|----------------|
| T1 | タスク: 「今日中にバグ修正」 | Q1, urgency=1.0, today |
| T2 | タスク: 「来月の企画を考える」 | Q2, urgency=0.2, 2months |
| T3 | タスク: 「メール返信」(期限なし) | Q3, urgency=0.3, week |
| T4 | T1からタスク0件 | "特になし", T6不発動 |
| T5 | 目標推論失敗 | generic_goals適用、正常動作 |

---

## Failure Modes

| 失敗 | 症状 | 検出方法 | 回復策 |
|------|------|----------|--------|
| 優先順位誤り | 重要タスクが低優先度 | ユーザー指摘 | goal_alignment 重みを上げる |
| 過剰分類 | 全てが「今日」に集中 | today_count > 5 | 時間軸分散を強制 |
| 緊急偏重 | Q2タスクが0件 | q2_count = 0 | Q2保護メカニズム発動 |
| 目標ミスマッチ | 全タスクのalignmentが低い | max(alignment) < 0.3 | 目標リスト見直しを提案 |

---

## Integration

| 依存 | 対象 | 関係 |
|------|------|------|
| **Precondition** | T1 Aisthēsis | 状況認識結果 |
| **Postcondition** | T6 Praxis | 優先順位付きタスクを渡す |
| **Postcondition** | T5 Peira | 情報不足タスクを渡す |
| **Postcondition** | T8 Anamnēsis | 目標乖離度を渡す |

---

## Configuration

| パラメータ | デフォルト | 説明 |
|------------|-----------|------|
| `goal_alignment_weight` | 0.4 | 優先度計算における目標整合性の重み |
| `urgency_weight` | 0.3 | 優先度計算における緊急度の重み |
| `commitment_weight` | 0.3 | 優先度計算におけるコミットメントの重み |
| `q2_protection_enabled` | true | Q2保護メカニズムの有効/無効 |
| `min_q2_ratio` | 0.2 | 出力に含める最小Q2比率 |
| `max_today_tasks` | 5 | "today"に分類するタスクの上限 |

---

## サブ機能: モデル選択判断

> **派生元**: T2 Krisis（高次意思決定）
> **参照**: `.agent/rules/model-selection-guide.md`
> **発動フック**: `/plan` Step 0.1

### 優先度ルール

```
1. [最優先] セキュリティ/監査/コンプライアンス → Claude
2. [優先]   マルチモーダル（画像/UI/UX）→ Gemini
3. [通常]   探索/ブレスト/プロトタイプ/MVP → Gemini
4. [通常]   高速反復/大量処理/初期調査 → Gemini Flash
5. [デフォルト] 上記に該当しない → Claude
```

### 検出キーワード

| 優先度 | キーワード | 推奨 |
|--------|-----------|------|
| **P1** | セキュリティ, 監査, コンプライアンス, 品質保証 | Claude |
| **P2** | 画像, UI, UX, 図, 可視化, デザイン | Gemini |
| **P3** | 探索, ブレスト, プロトタイプ, MVP, 試作 | Gemini |
| **P4** | 高速, バッチ, 初期調査, トリアージ | Gemini Flash |
| **P5** | （デフォルト） | Claude |

### 出力形式

```
[Hegemonikon] T2 Krisis（モデル選択）
  検出特性: {キーワード}
  優先度: {P1-P5}
  推奨: {Claude / Gemini / Gemini Flash}
  理由: {1行}
  → このまま継続 / Geminiに切り替え？
```

### テストケース

| ID | 入力 | 期待 |
|----|------|------|
| T1 | 「ドキュメント整理」 | P5 → Claude |
| T2 | 「プロトタイプのセキュリティレビュー」 | P1 → Claude |
| T3 | 「ダッシュボードのUI設計」 | P2 → Gemini |
| T4 | 「新機能のブレスト」 | P3 → Gemini |
