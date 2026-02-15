# Intent-WAL (Write-Ahead Log) YAML スキーマ設計

> **Status**: Draft → Approved (2026-02-15)
> **Priority**: P1 (long_lived_agent_design.md P1)
> **導出**: /eat+ F7 (長期エージェント寿命) → long_lived_agent_design.md

## 概要

Intent-WAL は DB の WAL パターンを借用した「意図の先書きログ」。
セッション中断がいつ起きても intent が残り、再開時にリカバリ可能にする。

```
RAM (コンテキスト) → 揮発性
Intent-WAL          → 半永続 (ファイルベース)
Handoff (ROM)       → 永続 (セッション間)
KI / Sophia         → 永続 (プロジェクト間)
```

## YAML スキーマ定義

### パス規約

```
~/oikos/mneme/.hegemonikon/wal/
  intent_{YYYYMMDD}_{HHMM}.yaml   # セッション単位
```

### スキーマ v1.0

```yaml
# Intent-WAL v1.0
version: "1.0"

# ── メタデータ ──
meta:
  session_id: "uuid-or-timestamp"        # セッション識別子
  agent: "Claude"                        # 実行エージェント
  created_at: "2026-02-15T15:00:00+09:00"
  updated_at: "2026-02-15T16:30:00+09:00"
  n_chat_messages: 15                    # BC-18 連動

# ── 意図宣言 (required) ──
intent:
  session_goal: "registry.yaml 修正 + Safety Warnings 解消"
  acceptance_criteria:
    - "YAML パースエラーが 0"
    - "Safety Audit: Errors 0, Warnings 0"
  context: |
    前セッションで 6 errors を解消済み。
    残り 72 warnings を解決する。

# ── 進捗ログ (append-only) ──
progress:
  - timestamp: "2026-02-15T15:10:00+09:00"
    step: 1
    action: "registry.yaml パースエラー修正"
    status: "done"           # pending | in_progress | done | blocked
    detail: "periskope のインデント修正"

  - timestamp: "2026-02-15T15:30:00+09:00"
    step: 2
    action: "Skills フロントマター修正 (12ファイル)"
    status: "in_progress"
    detail: "reversible/requires_approval/fallbacks 追加中"

# ── リカバリ情報 ──
recovery:
  last_file_edited: ".agent/skills/taxis/SKILL.md"
  uncommitted_changes: true
  blockers: []
  # 中断時にここを読めば再開可能

# ── BC-18 連動 ──
context_health:
  level: "green"             # green | yellow | orange | red
  savepoint: null            # yellow 到達時にパス記録
  recommendation: null       # "新規タスク受付停止" etc.
```

### フィールド仕様

| フィールド | 型 | 必須 | 説明 |
|:-----------|:---|:-----|:-----|
| `version` | string | ✅ | スキーマバージョン |
| `meta.session_id` | string | ✅ | セッション識別子 |
| `meta.agent` | string | ✅ | Claude / Jules |
| `meta.created_at` | ISO8601 | ✅ | 作成日時 |
| `meta.updated_at` | ISO8601 | ✅ | 最終更新日時 |
| `meta.n_chat_messages` | int | ❌ | BC-18 用 N値 |
| `intent.session_goal` | string | ✅ | セッション目標 (1行) |
| `intent.acceptance_criteria` | list[str] | ❌ | 完了判定基準 |
| `intent.context` | string | ❌ | 補足コンテキスト |
| `progress` | list[entry] | ❌ | 進捗ログ (append-only) |
| `recovery.last_file_edited` | string | ❌ | 最後に編集したファイル |
| `recovery.uncommitted_changes` | bool | ❌ | 未コミット変更有無 |
| `recovery.blockers` | list[str] | ❌ | ブロッカー |
| `context_health.level` | enum | ❌ | BC-18 閾値レベル |

### boot_integration.py との整合性

既存の postcheck (L701-717) は以下のパターンを検出する:

```python
re.search(r"intent_wal:|session_goal:", content, re.IGNORECASE)
```

WAL YAML に `intent.session_goal` が存在すれば `session_goal:` パターンにマッチする。
Boot Report に WAL の内容を `## Intent-WAL` セクションとして埋め込めば互換性が保たれる。

### 生成・更新タイミング

| タイミング | 操作 | トリガー |
|:-----------|:-----|:---------|
| `/boot` 完了時 | 新規作成 | Boot Report に `session_goal` 記入時 |
| タスク完了時 | progress 追記 | task_boundary TaskStatus=done |
| BC-18 🟡到達 | context_health 更新 | N chat messages ≥ 31 |
| `/bye` 時 | WAL → Handoff 変換 | セッション終了 |

## 次のアクション

- [x] P1: YAML スキーマ設計 ← **本ドキュメント**
- [ ] P2: `/rom` 自動トリガー (BC-18 連動)
- [ ] P3: Jules Pipeline への WAL 統合
- [ ] P4: `/boot` の WAL 読み込み対応

---

*Design v1.0 — Intent-WAL YAML スキーマ定義 (2026-02-15)*
