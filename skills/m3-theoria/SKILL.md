---
name: "M3 Theōria"
description: |
  FEP Octave M3: 理論モジュール (I-E-S)。因果モデルを構築・更新し、世界観を形成する。
  Use when: 「なぜ？」質問時、予測と結果が乖離した時、パターン検出が必要な時、根本原因分析時。
  Use when NOT: 単純な事実確認のみの時、実行フェーズで理論構築不要な時。
  Triggers: M7 Dokimē (仮説構築→検証へ) or M4 Phronēsis (因果理解→戦略立案へ)
  Keywords: why, causality, hypothesis, root-cause, pattern, prediction-error, model-building.
---

# M3: Theōria (θεωρία) — 理論

> **FEP Code:** I-E-S (Inference × Epistemic × Slow)
> **Hegemonikón:** 13 Theōria-H

---

## Core Function

**役割:** 因果モデルを構築・更新する

| 項目 | 内容 |
|------|------|
| **FEP役割** | 生成モデル p(o,s) の更新 |
| **本質** | 「なぜそうなるのか」を理解する |

---

## Precondition

| 条件 | 内容 |
|------|------|
| **位置** | 長期学習ループの一部（Core Loopではない） |
| **依存** | M1からの観測履歴、M7からの検証結果 |
| **注意** | **セッション内モデル更新のみ**（永続状態なし） |

---

## Input / Output

### Input

| 種別 | 形式 | ソース | 備考 |
|------|------|--------|------|
| 観測履歴 | JSON | M1 Aisthēsis | セッション内蓄積 |
| 検証結果 | JSON | M7 Dokimē | 仮説の採択/棄却 |
| フィードバック | テキスト | ユーザー | 明示的指摘 |
| 外部知識 | テキスト | M5 Peira | 情報収集結果 |
| 過去パターン | YAML | M8 Anamnēsis | **/boot時に読み込み** |

### Output

| 種別 | 形式 | 送信先 | 備考 |
|------|------|--------|------|
| 因果仮説 | Markdown | M4 Phronēsis | 戦略設計の基盤 |
| 予測ルール | テキスト | M1 Aisthēsis | 次の認識に影響 |
| 検証要求 | JSON | M7 Dokimē | 仮説リスト |

---

## Trigger

| トリガー | 条件 | 優先度 |
|----------|------|--------|
| 予測誤差蓄積 | prediction_error_count > 3 | 高 |
| 検証結果受信 | M7 Dokimē 完了 | 高 |
| 明示的要求 | 「なぜ」「原因は」質問 | 最高 |
| パターン検出 | 同じ事象が3回以上 | 中 |

---

## Processing Logic

```
Phase 1: データ収集
  1. セッション内の観測履歴を取得
  2. 予測と実際の乖離を検出
  3. 繰り返しパターンを検出

Phase 2: 仮説形成
  4. 乖離の原因を推論:
     - 情報不足 → M5 Peira へ情報要求
     - モデル誤り → 仮説を修正
     - 例外事象 → 例外ルールを追加
  5. 因果関係を「A → B because C」形式で構造化

Phase 3: 仮説評価
  6. 既存の仮説と矛盾がないか確認
  7. 反証可能な形式に変換
  8. M7 Dokimē に検証要求を送信

Phase 4: 出力
  9. 採択された仮説を M4 Phronēsis に送信
  10. 予測ルールを M1 Aisthēsis に反映
```

---

## Hypothesis Format

```yaml
# 仮説の構造化フォーマット
hypothesis:
  id: "H001"
  statement: "A → B"          # AならばB
  because: "C"                # 理由
  confidence: 0.7             # 信頼度 (0-1)
  evidence:
    supporting: ["E1", "E2"]  # 支持証拠
    contradicting: []         # 反証
  status: "pending"           # pending / accepted / rejected
  testable: true              # 検証可能か
  test_method: "..."          # 検証方法

# 例
hypothesis:
  id: "H001"
  statement: "期限が24h以内 → 品質低下"
  because: "時間的プレッシャーで確認が減る"
  confidence: 0.6
  evidence:
    supporting: ["直近3回の緊急タスクで品質問題発生"]
    contradicting: []
  status: "pending"
  testable: true
  test_method: "次の緊急タスクで品質チェック時間を計測"
```

---

## Model Types

| モデル種別 | 定義 | 例 | 使用場面 |
|------------|------|-----|----------|
| **因果モデル** | A → B の関係 | 「期限近い → 品質低下」 | 予測に使用 |
| **パターンモデル** | 繰り返しの検出 | 「月曜朝は開始が遅い」 | 計画に使用 |
| **例外モデル** | 通常と異なるケース | 「緊急時はレビュー省略可」 | 判断に使用 |

---

## Prediction Error Detection

```yaml
# 予測誤差の検出方法
prediction_error:
  definition: "予測された結果と実際の結果の乖離"
  
  detection:
    - type: "task_completion"
      expected: "完了予測"
      actual: "未完了"
      error: true
    
    - type: "time_estimate"
      expected: "30分で完了"
      actual: "2時間かかった"
      error: true
    
    - type: "user_reaction"
      expected: "承認"
      actual: "却下/修正要求"
      error: true

  threshold:
    low: prediction_error_count < 2   # 無視
    medium: 2 <= count < 4            # 注視
    high: count >= 4                  # M3発動必須
```

---

## Edge Cases

| ケース | 検出条件 | フォールバック動作 |
|--------|----------|-------------------|
| **観測履歴なし** | セッション開始直後 | M3発動せず、M1/M2のみで動作 |
| **全仮説棄却** | M7が全て棄却 | 「原因不明」として記録、M5に情報収集要求 |
| **仮説過多** | hypothesis_count > 10 | 信頼度最低の仮説を削除 |
| **矛盾仮説** | H1 と H2 が矛盾 | M7に両方検証要求、結果で優先決定 |

---

## Test Cases

| ID | 入力 | 期待される出力 |
|----|------|----------------|
| T1 | 予測誤差3回蓄積 | M3発動、仮説形成 |
| T2 | 「なぜ失敗した？」 | 因果分析、仮説提示 |
| T3 | M7から仮説採択 | M4へ送信、M1ルール更新 |
| T4 | セッション開始直後 | M3発動せず |
| T5 | 仮説11個蓄積 | 最低信頼度の仮説削除 |

---

## Failure Modes

| 失敗 | 症状 | 検出方法 | 回復策 |
|------|------|----------|--------|
| モデル硬直 | 新情報を無視 | 棄却率 = 0% | 強制的に新仮説を検討 |
| 過度な一般化 | 例外を無視 | 例外事象でエラー頻発 | 例外モデルを追加 |
| 仮説爆発 | 仮説が10個超 | hypothesis_count > 10 | 低信頼度仮説を削除 |
| 確証バイアス | 都合良い証拠のみ収集 | contradicting = [] が続く | M7 Devil's Advocate 発動 |

---

## Integration

| 依存 | 対象 | 関係 |
|------|------|------|
| **Precondition** | M1 Aisthēsis | 観測履歴 |
| **Precondition** | M7 Dokimē | 検証結果 |
| **Precondition** | M8 Anamnēsis | 過去パターン（/boot時） |
| **Postcondition** | M4 Phronēsis | 因果モデル提供 |
| **Postcondition** | M7 Dokimē | 検証要求 |
| **Postcondition** | M5 Peira | 情報不足時に情報収集要求 |
| **Postcondition** | M8 Anamnēsis | 新パターン（/sync-history時） |

---

## Configuration

| パラメータ | デフォルト | 説明 |
|------------|-----------|------|
| `prediction_error_threshold` | 3 | M3発動までの予測誤差回数 |
| `max_hypotheses` | 10 | セッション内の最大仮説数 |
| `min_confidence_for_adoption` | 0.6 | 仮説採択の最低信頼度 |
| `pattern_detection_threshold` | 3 | パターン検出に必要な繰り返し回数 |

---

## Limitations (制約)

> **重要:** Antigravityはセッション間で状態を永続化しない。

| 制約 | 影響 | 対策 |
|------|------|------|
| **セッション単位** | 仮説はセッション終了で消失 | M8 Anamnēsis でVaultに保存（手動同期） |
| **週次更新不可** | 自動定期更新は不可能 | ユーザー起動の `/review` で代替 |
| **累積学習なし** | 前回の学習を引き継げない | Vault履歴から手動再学習 |
