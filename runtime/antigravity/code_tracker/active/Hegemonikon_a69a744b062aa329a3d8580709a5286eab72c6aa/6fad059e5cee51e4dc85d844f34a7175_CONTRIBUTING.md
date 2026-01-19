�
# Contributing to Hegemonikón

## 開発方針

このプロジェクトはプライベートリポジトリですが、将来的な拡張を見据えた構造になっています。

## ディレクトリ構造

| パス | 目的 |
|------|------|
| `kernel/` | 核心層 - 変更には慎重なレビューが必要 |
| `skills/` | M-Series認知モジュール - 拡張・改善を歓迎 |
| `forge/` | Forge従属プロジェクト |
| `docs/` | 設計ドキュメント・監査レポート |

## コミット規約

```
<type>(<scope>): <subject>

type: feat, fix, docs, style, refactor, test, chore
scope: kernel, skills, forge, docs
```

例:
- `feat(skills): add M9 function`
- `docs(kernel): update doctrine`
- `fix(forge): resolve path issue`

## 命名規則

- **スキル名**: `m{N}-{greek-name}` (例: `m1-aisthesis`)
- **ドキュメント**: ケバブケース (例: `phase2-design.md`)
- **コード**: プロジェクト標準に従う

## 設計原則

> **"Form follows logic. Logic follows beauty."**

変更を加える際は、以下を遵守:

1. **論理的整合性**: 既存の公理体系と矛盾しないこと
2. **意味的階層**: 命名と配置が意味を正確に表現すること
3. **最小複雑性**: 必要最小限の変更で目的を達成すること
�
*cascade08"(a69a744b062aa329a3d8580709a5286eab72c6aa22file:///C:/Users/raikh/Hegemonikon/CONTRIBUTING.md:"file:///C:/Users/raikh/Hegemonikon