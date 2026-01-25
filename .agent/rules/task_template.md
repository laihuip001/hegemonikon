---
id: task-template
title: task.md テンプレート（フェーズ依存関係付き）
---

# task.md テンプレート

以下のフォーマットを使用して、フェーズ間の依存関係を明示すること。

---

## 推奨フォーマット

```markdown
# [タスク名]

## 進行状況

- [ ] Phase 1: [説明]
  - blockers: なし
- [ ] Phase 2: [説明]
  - blockers: Phase 1
- [ ] Phase 3: [説明]
  - blockers: Phase 1, Phase 2
- [ ] Phase N: [説明] ⚠️ 破壊的操作
  - blockers: Phase 1-N-1 全て完了後
  - guard: Git 追跡確認、バックアップ確認
```

---

## ルール（対策2）

1. **blockers フィールド必須**: 各フェーズに前提条件を明記
2. **破壊的フェーズの警告**: 削除・リセット系には `⚠️ 破壊的操作` を付与
3. **guard フィールド**: 破壊的フェーズには実行前チェック項目を記載

---

## 例

```markdown
# Forge 解体・統合タスク

## 進行状況

- [x] Phase 1: prompt-lang → mekhane/ergasterion/
  - blockers: なし
- [x] Phase 2: 44 modules → T-series skills
  - blockers: なし（独立可能）
- [ ] Phase 3: 6 presets → T-series skills
  - blockers: なし
- [ ] Phase 4: profiles → .agent/rules/profiles/
  - blockers: なし
- [ ] Phase 5: knowledge_base → mekhane/anamnesis/
  - blockers: なし
- [ ] Phase 6: docs → docs/archive/forge/
  - blockers: なし
- [ ] Phase 7: forge/ 削除 ⚠️ 破壊的操作
  - blockers: Phase 1-6 全て完了後
  - guard: `git status` で未追跡なし確認、GitHub に push 済み確認
```

---

*対策2: フェーズ依存関係の明示*
