---
description: コード開発時のプロトコル自動参照
activation: glob
pattern: "**/*.py"
priority: 2
hegemonikon: M6-Praxis
---

# コード開発プロトコル（Glob Rule）

> **発動条件**: `*.py` ファイル編集時に自動適用
> **ソース**: Legacy Modules 01, 04, 14 から蒸留

---

## 自動チェックポイント

このルールが発動したら、以下を確認:

### 1. DMZ チェック

編集対象が以下に該当する場合、警告を発する:
- `^\.env$` / `config*.py` / `secrets*` / `docker-compose.yml`

```
⚠️ DMZ ALERT: 保護資産を編集中
詳細: /dev dmz
```

### 2. TDD リマインダー

新規関数を追加する場合:
```
🧪 TDD Protocol: テストを先に書いていますか？
詳細: /dev tdd
```

### 3. Commit 準備

変更をコミットする前に:
```
📝 Narrative Commit: Context/Solution/Alternatives を含めてください
詳細: /dev commit
```

---

## 詳細参照

より詳しいプロトコルが必要な場合:

1. **Skill経由（自動）**: `/do` 実行時に M6 Praxis が参照
2. **Workflow経由（手動）**: `/dev [protocol]` で原典を展開
3. **原典直接参照**:
   ```
   view_file "M:\Brain\99_🗃️_保管庫｜Archive\プロンプト ライブラリー\モジュール（開発用）\個別のモジュール\Module XX ....md"
   ```

---

## 関連

- [Code Protocols Skill](file:///M:/Hegemonikon/.agent/skills/code-protocols/SKILL.md)
- [/dev Workflow](file:///M:/Hegemonikon/.agent/workflows/dev.md)
- [Legacy Modules Index](file:///M:/Hegemonikon/docs/archive/legacy-rules/legacy-modules-index.md)
