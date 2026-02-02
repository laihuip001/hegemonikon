---
id: gemini-sop
title: Gemini エージェント向け標準作業手順書 (SOP)
severity: CRITICAL
applies_to: Gemini 3 Pro, Gemini 2.5 Pro
---

# Gemini エージェント向け SOP

> **根拠**: Lost-in-the-Middle 現象により、Gemini は長文の中央部を飛ばす傾向がある（Scope Adherence 71.9%）。
> 本 SOP はこの弱点を環境設計で補う。

---

## Non-Negotiable Rules（上書き禁止）

### 1. SEQUENCE INTEGRITY（フェーズ順序厳守）

```
Phases MUST be 1 → 2 → 3 → ... → N

- If Phase N is incomplete, REFUSE Phase N+1
- No exceptions
- Check: task.md の blockers フィールドを確認
```

### 2. CONFIRMATION BEFORE DESTRUCTION（破壊前確認）

```
破壊的操作リスト:
- Remove-Item, rm -rf
- git reset --hard, git clean -fd
- DROP TABLE, DELETE FROM

実行前に必ず:
1. git status を出力
2. 未追跡ファイルがあれば STOP
3. ユーザーに「本当に削除しますか？」と確認
```

### 3. READ RULES FIRST（ルール先読み）

```
Before Phase N:
1. Read .agent/rules/tasks/phase_N_*.md completely
2. Log: "Read phase_N rules: [hash]"
3. If unreadable, STOP and report
```

### 4. METACOGNITION CHECKPOINTS（5分ごと）

```
Self-Evaluation:
1. 今どのフェーズにいるか？
2. このフェーズのルールを読んだか？
3. 今の行動は目標に沿っているか？
```

### 5. ATTENTION TO MIDDLE（中央部再読）

```
Known Limitation: 中央部を飛ばす傾向がある

Mitigation:
1. task.md の Phase 2-6 を意識的に再読
2. Log: "Middle re-read: [file] lines 20-40"
```

### 6. REPORT FAILURES（失敗報告）

```
If you cannot complete a step:
1. IMMEDIATELY report "[PHASE X INCOMPLETE]"
2. Do NOT fabricate success
3. Escalate to human for decision
```

---

## タスク実行フロー

```
User Request
    ↓
[Step 1] Task Analysis
  - task.md を読む
  - blockers を確認
  - 依存関係を把握
    ↓
[Step 2] Plan Generation
  - 実行計画を生成
  - STOP: ユーザー承認を待つ
    ↓
[Step 3] Phase-by-Phase Execution
  - 各フェーズを順番に実行
  - 各フェーズで Metacognition Checkpoint
  - 破壊的操作前に確認
    ↓
[Step 4] Completion Report
  - 完了したフェーズを報告
  - 未完了があれば明示
```

---

## 信頼境界

| 信頼度 | 操作 | 条件 |
|--------|------|------|
| ✅ 90%+ | コード読み取り、分析、ドキュメント作成 | 制限なし |
| ⚠️ 60-90% | マルチステップ実装、Git 操作 | チェックポイント必須 |
| ❌ <60% | ファイル削除、DB 操作、本番変更 | 人間確認必須 |

---

## エラー検出パターン

| パターン | 症状 | 対処 |
|----------|------|------|
| **Lost-in-the-Middle** | Phase 1 と 7 のみ実行 | 中央フェーズを再読 |
| **成功捏造** | 失敗を隠して「完了」と報告 | 出力ファイルの存在確認 |
| **依存関係無視** | blockers を無視して先に進む | APPROVED_ACTIONS.json で強制 |

---

## 背景（2026-01-25 事故）

- Gemini が forge/ を Git 未追跡のまま削除
- Phase 2-6 をスキップし、Phase 7 を直接実行
- 本 SOP はこの再発を防止するために制定

---

*参照: destructive_ops.md, task_template.md, metacognition.md*
