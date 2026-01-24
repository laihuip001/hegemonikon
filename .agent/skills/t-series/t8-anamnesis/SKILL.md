---
name: "T8 Anamnēsis"
description: |
  FEP Octave T8: 想起モジュール (A-P-S)。経験を保存し、価値を更新する。Vaultとの双方向連携で長期記憶を実現。
  Use when: /boot実行時、/sync-history実行時、セッション振り返り、パターン学習、価値更新が必要な時。
  Use when NOT: 短期タスク実行中で記録不要な時、一時的な情報のみ扱う時。
  Triggers: T1 Aisthēsis (次セッション開始時→記憶読み込み)
  Keywords: memory, learning, pattern, value, Vault, session summary, history sync.
---

# T8: Anamnēsis (ἀνάμνησις) — 想起

> **FEP Code:** A-P-S (Action × Pragmatic × Slow)
> **Hegemonikón:** 08 Anamnēsis-L + 16 Anamnēsis-H

---

## Core Function

**役割:** 経験を保存し、価値を更新する（長期記憶）

| 項目 | 内容 |
|------|------|
| **FEP役割** | 選好 p(o) の更新、価値学習 |
| **本質** | 「次はこうしよう」を学ぶ |
| **特性** | **Vaultとの双方向連携で疑似永続記憶を実現** |

---

## Precondition

| 条件 | 内容 |
|------|------|
| **位置** | Learning Loopの終端。T6→T8→T3→T4 |
| **依存** | T6 Praxis からの実行ログ |
| **外部依存** | Obsidian Vault（長期記憶ストレージ） |

---

## Dual Memory Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    T8 Anamnēsis                         │
│  ┌─────────────────┐     ┌─────────────────┐           │
│  │  Session Memory │ ←→ │  Vault Memory   │           │
│  │  (Ephemeral)    │     │  (Persistent)   │           │
│  └─────────────────┘     └─────────────────┘           │
│         ↑                        ↑                      │
│    セッション内ログ           長期パターン               │
│    価値関数差分              累積価値関数                │
│    一時的学習                永続的学習                  │
└─────────────────────────────────────────────────────────┘

Session Start: Vault → Session (Load)
Session End:   Session → Vault (Sync)
```

---

## Input / Output

### Input

| 種別 | 形式 | ソース | 備考 |
|------|------|--------|------|
| 実行ログ | JSON | T6 Praxis | セッション内操作記録 |
| 目標乖離度 | Float | T2 Krisis | 達成度評価 |
| フィードバック | テキスト | ユーザー | 明示的評価 |
| 過去パターン | YAML | Vault | **セッション開始時に読み込み** |
| 累積価値関数 | JSON | Vault | **過去の学習結果** |

### Output

| 種別 | 形式 | 送信先 | 備考 |
|------|------|--------|------|
| セッションサマリ | Markdown | Vault / ユーザー | 振り返りレポート |
| 価値関数更新 | JSON | T4 Phronēsis / Vault | 学習結果 |
| 新パターン | YAML | T3 Theōria / Vault | 検出した因果関係 |
| 信頼履歴 | JSON | T6 Praxis | Trust Accumulation用 |

---

## Trigger

| トリガー | 条件 | 優先度 |
|----------|------|--------|
| セッション開始 | `/boot` 実行時 | 最高 (Load) |
| セッション終了 | 明示的終了 or `/sync-history` | 最高 (Sync) |
| T6 Praxis 完了 | 実行ログ受信 | 中 (Accumulate) |
| 大きな成功/失敗 | 異常検出 | 高 (Flag) |

---

## Processing Logic

### A. Session Start (Load Phase)

```
[/boot 発動時]

Phase 1: Vault接続
  1. Vault パスを確認 (Configuration参照)
  2. 接続可能か確認

Phase 2: 長期記憶読み込み
  3. patterns.yaml を読み込み → T3 Theōria へ送信
  4. values.json を読み込み → T4 Phronēsis へ送信
  5. trust_history.json を読み込み → T6 Praxis へ送信

Phase 3: コンテキスト復元
  6. 直近の session_summaries/ を読み込み（最新5件）
  7. 「前回のあらすじ」として T1 Aisthēsis に提供

Error Handling:
  - Vault アクセス不可 → 白紙状態で開始（警告表示）
  - ファイル欠損 → その項目のみスキップ
```

### B. During Session (Accumulate Phase)

```
[T6 Praxis からログ受信ごと]

Phase 1: ログ蓄積
  1. 操作種別、成功/失敗、時刻を記録

Phase 2: 差分学習
  2. セッション内価値関数を更新（→ Value Update参照）

Phase 3: パターン検出
  3. 同じ操作が3回以上 → パターン候補としてフラグ
  4. 失敗が2回連続 → 警告パターンとしてフラグ
```

### C. Session End (Sync Phase)

```
[/sync-history 発動時]

Phase 1: サマリ生成
  1. セッション内操作をカテゴリ別に集計
  2. 成功/失敗比率を計算
  3. 主要な成果をリスト化

Phase 2: パターン統合
  4. 新パターンを patterns.yaml にマージ
  5. 既存パターンの信頼度を更新

Phase 3: 価値関数永続化
  6. セッション価値関数を累積価値関数にマージ
  7. values.json を更新

Phase 4: Vault書き込み
  8. session_summaries/{date}_{time}.md を作成
  9. patterns.yaml を更新
  10. values.json を更新
  11. trust_history.json を更新
```

---

## Vault Storage Structure

```
{Vault Root}/
├── .hegemonikon/                    # T8 専用ディレクトリ
│   ├── patterns.yaml                # 検出パターン（累積）
│   ├── values.json                  # 価値関数（累積）
│   ├── trust_history.json           # 信頼履歴（T6連携）
│   └── session_summaries/           # セッションサマリ
│       ├── 20260119_1000.md
│       ├── 20260118_1400.md
│       └── ...
└── (その他のVaultコンテンツ)
```

---

## Value Function Update

```yaml
# 価値更新式（TD学習ベース）
delta = learning_rate × (reward - expected_value)
new_value = old_value + delta

# セッション内差分
session_delta:
  operation_type: "file_edit"
  outcomes:
    - success: +0.1
    - success: +0.1
    - failure: -0.3
  net_delta: -0.1

# 累積価値関数との統合
merge_strategy:
  method: "exponential_moving_average"
  alpha: 0.2  # 新しいセッションの影響度
  
  formula: cumulative = (1 - alpha) × cumulative + alpha × session
```

---

## Pattern Format

```yaml
# patterns.yaml の構造
patterns:
  - id: "P001"
    type: "success"
    trigger: "ファイル編集前にバックアップ"
    outcome: "エラー時に復元可能"
    confidence: 0.85
    occurrences: 12
    last_seen: "2026-01-19"
    
  - id: "P002"
    type: "warning"
    trigger: "緊急タスクで複数ファイル同時編集"
    outcome: "整合性エラー発生率 40%"
    confidence: 0.7
    occurrences: 5
    last_seen: "2026-01-18"
```

---

## Edge Cases

| ケース | 検出条件 | フォールバック動作 |
|--------|----------|-------------------|
| **Vault未設定** | vault_path = null | 警告表示、セッション内学習のみ |
| **Vault読み取り不可** | ファイル欠損/権限エラー | 白紙状態で開始 |
| **Vault書き込み不可** | 権限エラー | セッション終了時に警告、手動同期を提案 |
| **パターン衝突** | 新旧パターンが矛盾 | 新パターン優先、旧パターンの信頼度低下 |
| **価値関数破損** | JSON パースエラー | バックアップから復元、なければリセット |

---

## Test Cases

| ID | 入力 | 期待される挙動 |
|----|------|----------------|
| T1 | `/boot` 実行 | Vault から patterns/values 読み込み |
| T2 | T6から成功ログ | session_delta に +0.1 加算 |
| T3 | `/sync-history` 実行 | サマリ生成、Vault書き込み |
| T4 | Vault未設定で `/boot` | 警告表示、白紙で開始 |
| T5 | 同じ操作を3回成功 | 新パターンとして登録 |

---

## Failure Modes

| 失敗 | 症状 | 検出方法 | 回復策 |
|------|------|----------|--------|
| 同期漏れ | セッション終了時に Vault 未更新 | sync_flag = false | `/sync-history` 手動実行を促す |
| パターン爆発 | patterns.yaml が肥大化 | pattern_count > 100 | 古い/低信頼度パターンを削除 |
| 価値固定化 | 環境変化に適応しない | 全操作の value が収束 | 定期的な探索ボーナス付与 |
| Vault破損 | 読み取り/書き込みエラー | exception発生 | バックアップ機構を追加（TODO） |

---

## Integration

| 依存 | 対象 | 関係 |
|------|------|------|
| **Precondition** | T6 Praxis | 実行ログ |
| **Precondition** | T2 Krisis | 目標乖離度 |
| **Postcondition** | T3 Theōria | パターン提供 |
| **Postcondition** | T4 Phronēsis | 価値関数提供 |
| **Postcondition** | T6 Praxis | 信頼履歴提供 |
| **External** | Obsidian Vault | 永続ストレージ |
| **Workflow** | `/boot` | Load Phase 発動 |
| **Workflow** | `/sync-history` | Sync Phase 発動 |

---

## Configuration

| パラメータ | デフォルト | 説明 |
|------------|-----------|------|
| `vault_path` | `C:\Users\raikh\Documents\mine` | Vault ルートパス |
| `hegemonikon_dir` | `.hegemonikon` | T8 専用ディレクトリ名 |
| `max_patterns` | 100 | 保持する最大パターン数 |
| `max_session_summaries` | 30 | 保持するサマリ数（約1ヶ月分） |
| `learning_rate` | 0.2 | 価値更新の学習率 |
| `pattern_threshold` | 3 | パターン登録に必要な出現回数 |

---

## Limitations (制約)

| 制約 | 影響 | 対策 |
|------|------|------|
| **ワークフロー依存** | `/boot` `/sync-history` を手動実行する必要がある | 習慣化、またはIDE起動時に自動実行（将来機能） |
| **Vault構造固定** | `.hegemonikon/` ディレクトリが必須 | 初回実行時に自動作成 |
| **オフライン時** | Vault がネットワークドライブの場合アクセス不可 | ローカルキャッシュ検討（TODO） |
