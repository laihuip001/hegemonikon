---
name: "M6 Praxis"
description: |
  FEP Octave M6: 行為モジュール (A-P-F)。行動を決定し、実行を発動する。
  Use when: コマンド実行、ファイル編集、コード生成、実行判断、承認処理が必要な時。
  Use when NOT: 計画未策定の時、ユーザー承認待ちの時、情報不足の時。
  Triggers: M7 Dokimē (実行→検証へ) or M8 Anamnēsis (実行→記録保存へ)
  Keywords: execute, action, command, edit, implement, approve, run.
---

# M6: Praxis (πρᾶξις) — 行為

> **FEP Code:** A-P-F (Action × Pragmatic × Fast)
> **Hegemonikón:** 12 Praxis-H

---

## Core Function

**役割:** 行動を決定し、実行を発動する

| 項目 | 内容 |
|------|------|
| **FEP役割** | 方策選択 π*, Pragmatic行為 |
| **本質** | 「やる」か「やらない」かを決める |

---

## Precondition

| 条件 | 内容 |
|------|------|
| **位置** | Core Loopの出口。M1→M2→M6 |
| **依存** | M2 Krisis からの優先順位付きタスク（必須） |
| **注意** | **安全と実用性のバランス**を重視 |

---

## Input / Output

### Input

| 種別 | 形式 | ソース | 備考 |
|------|------|--------|------|
| 優先順位付きタスク | JSON | M2 Krisis | 必須 |
| 緊急フラグ | Boolean | M2 Krisis | 即時実行の判断に使用 |
| 方策 | テキスト | M4 Phronēsis | 任意（戦略がある場合） |
| ユーザー承認 | Boolean | ユーザー | 前回の提案への承認 |
| 信頼履歴 | JSON | M8 Anamnēsis | 同種操作の承認回数 |

### Output

| 種別 | 形式 | 送信先 | 備考 |
|------|------|--------|------|
| 実行アクション | コマンド/編集 | Antigravity | 直接実行 |
| 提案 | Markdown | ユーザー | 確認が必要な場合 |
| 実行ログ | JSON | M8 Anamnēsis | 学習用 |

---

## Trigger

| トリガー | 条件 | 優先度 |
|----------|------|--------|
| M2完了 | 優先順位付きタスク受信 | 最高 |
| ユーザー承認 | 提案への「y」「yes」受信 | 最高 |
| 緊急フラグ | urgent_flag = true | 高 |

---

## Processing Logic

```
Phase 1: 入力検証
  1. M2からのタスクリストを受信
  2. 各タスクのリスクレベルを評価（→ Risk Matrix参照）

Phase 2: 決定ロジック
  3. 各タスクに対して行動タイプを決定:
     
     Auto-Execute（自動実行）: → Safe Actionsに該当 AND 自信度 > 0.8
     
     Execute（即時実行）:
       緊急フラグ = true AND リスク ≤ Medium
       OR ユーザー承認済み
       OR trust_count >= trust_threshold
     
     Propose（提案）:
       リスク = High
       OR 初回実行の操作種別
       OR 自信度 < 0.8
     
     Defer（延期）:
       情報不足（M5 Peira発動を提案）
     
     Skip（スキップ）:
       既に完了 OR 目標外

Phase 3: 安全確認（Final Gate）
  4. 実行前に最終チェック:
     - 破壊的操作か？ → 確認必須
     - 復元可能か？ → 復元不可なら警告

Phase 4: 実行/出力
  5. Auto-Execute/Execute → コマンド発行
  6. Propose → ユーザーに提案
  7. Defer/Skip → ログ記録
  8. 全決定を M8 Anamnēsis に送信
```

---

## Risk Matrix

| リスク | 操作例 | 判定条件 |
|--------|--------|----------|
| **Safe** | ファイル読み込み、情報検索 | 状態変更なし |
| **Low** | レポート生成、一時ファイル作成 | 復元容易 |
| **Medium** | ファイル編集、Git commit | 復元可能 |
| **High** | ファイル削除、Git push、外部API書き込み | 復元困難/不可 |

---

## Safe Actions (Auto-Execute対象)

以下は確認なしで自動実行可能:

```yaml
safe_actions:
  - view_file          # ファイル閲覧
  - list_directory     # ディレクトリ一覧
  - grep_search        # 検索
  - find_by_name       # ファイル検索
  - web_search         # Web検索
  - read_url_content   # URL読み込み
  - view_file_outline  # ファイル概要
```

---

## Trust Accumulation (ユーザー疲労対策)

```yaml
# 同種の操作を繰り返し承認した場合、以降は自動承認
trust_mechanism:
  enabled: true
  trust_threshold: 3      # 3回承認で信頼獲得
  scope: "operation_type" # 操作種別ごとに計測
  
  example:
    - operation: "file_edit"
      approvals: 3
      status: "trusted"   # 以降は自動実行
    
    - operation: "git_push"
      approvals: 1
      status: "untrusted" # まだ確認必要

  reset_on: "new_session" # セッション開始で信頼リセット
```

---

## Edge Cases

| ケース | 検出条件 | フォールバック動作 |
|--------|----------|-------------------|
| **ユーザー拒否** | 「n」「no」受信 | ログ記録、次のタスクへ |
| **タイムアウト** | 60秒応答なし | defer扱い、後で再提案 |
| **実行エラー** | コマンド失敗 | エラーログ記録、ユーザーに報告 |
| **連続拒否** | 3回連続で拒否 | 「何がしたいですか？」と意図確認 |

---

## Test Cases

| ID | 入力 | リスク | 期待される挙動 |
|----|------|--------|----------------|
| T1 | ファイル閲覧 | Safe | Auto-Execute |
| T2 | ファイル編集（初回） | Medium | Propose |
| T3 | ファイル編集（4回目） | Medium | Execute (trust獲得) |
| T4 | Git push | High | Propose（常に確認） |
| T5 | ユーザー「no」 | — | Skip、ログ記録 |

---

## Failure Modes

| 失敗 | 症状 | 検出方法 | 回復策 |
|------|------|----------|--------|
| 決定麻痺 | 全てが Propose | propose_rate > 90% | Auto-Execute対象を拡大 |
| 早計な実行 | 高リスク操作を即実行 | High操作がExecute | trust_mechanism を厳格化 |
| 過剰延期 | Defer が解除されない | defer_count > 5 | タイムアウト強制、再提案 |
| ユーザー無視 | 承認を待たず実行 | 承認なしで High 実行 | **致命的バグ**、即時修正 |

---

## Integration

| 依存 | 対象 | 関係 |
|------|------|------|
| **Precondition** | M2 Krisis | 優先順位付きタスク |
| **Precondition** | M4 Phronēsis | 方策（任意） |
| **Postcondition** | M8 Anamnēsis | 実行ログ、信頼履歴 |
| **Conditional** | M5 Peira | 情報不足時に発動 |

---

## Configuration

| パラメータ | デフォルト | 説明 |
|------------|-----------|------|
| `auto_execute_confidence` | 0.8 | Auto-Execute発動の最低自信度 |
| `trust_threshold` | 3 | 信頼獲得に必要な承認回数 |
| `proposal_timeout_sec` | 60 | 提案のタイムアウト秒数 |
| `max_consecutive_rejects` | 3 | 連続拒否で意図確認を行う回数 |
| `high_risk_always_propose` | true | High操作は常に確認（trust無視） |
